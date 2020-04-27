from evennia.utils.test_resources import EvenniaTest, mockdelay, mockdeferLater
from evennia.commands.default.tests import CommandTest
from typeclasses.combat.handler import Tilt
from evennia import create_script
from mock import Mock, patch
from world.breeds.donkey_kong import statblock

class TestCombat(EvenniaTest):

    def setUp(self):
        super().setUp()
        self.char1.db.will=500
        self.char2.db.will=500
        self.char1.db.statblock = statblock
        self.char2.db.statblock = statblock

    def get_handler(self):
        print(f"\nTesting {self.id()}: ")
        chandler = create_script(Tilt)
        chandler.add_character(self.char1)
        self.char1.ndb.target = self.char2
        chandler.add_character(self.char2)
        self.char2.ndb.target = self.char1
        return chandler

    def test_script_creation(self):
        chandler = self.get_handler()
        self.assertIsNotNone(self, chandler)

    def test_add_character(self):
        chandler = self.get_handler()
        chandler.add_character(self.char1)
        chandler.add_character(self.char2)
        self.assertIsNotNone(self.char1.ndb.tilt_handler)

    def test_target(self):
        chandler = create_script(Tilt)
        chandler.add_character(self.char1, target=self.char2)
        chandler.add_character(self.char2, target=self.char1)
        self.assertEqual(self.char2.ndb.target, self.char1)

    def test_tilt_exists(self):
        chandler = self.get_handler()
        self.assertEquals(chandler.get_tilt(self.char1), 0)

    def test_attack(self):
        chandler = self.get_handler()
        self.assertTrue(chandler.add_action_to_stack(self.char1, self.char2, basedamage=5))
#        self.assertTrue(chandler._process_action())
#        self.assertNotEquals(chandler.get_tilt(self.char2), 0)

    def test_get_keyframes(self):
        chandler = self.get_handler()
        res = chandler._get_character_total_keyframes(self.char1)
        self.assertEqual(0, res)

    def test_victory_by_tilt(self):
        chandler = self.get_handler()
        chandler.db.tilt[self.char1]=100000
        knockback = chandler.calc_knockback(chandler.get_tilt(self.char1), 600, 1, self.char2)
        chandler.loss_by_tilt(self.char1, knockback)
        self.assertIsNone(self.char1.ndb.tilt_handler)

#    def test_nosurrender(self):
#        chandler = self.get_handler()
#        chandler.db.tilt[self.char1]=250
#        self.char2.db.noflee = True
#        chandler.loss_by_tilt()
#        self.assertIsNotNone(self.char1.ndb.tilt_handler)

#    def test_square_hit(self):
#        chandler = self.get_handler()
#        self.assertTrue(chandler.add_action_to_stack(self.char1, self.char2, will_damage=5))
#        self.assertTrue(chandler._process_action())
#        self.assertNotEquals(self.char2.db.will, chandler.db.wills.get(self.char2))

#    def test_light_hit(self):
#        chandler = self.get_handler()
#        self.assertTrue(chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=5))
#        self.assertTrue(chandler._process_action())
#        self.assertNotEquals(chandler.db.tilt, 0)

 #   def test_injury(self):
 #       chandler = self.get_handler()
 #       chandler.cause_injury(self.char1, location="right_arm", severity=1)
 #       self.assertIsNotNone(self.char1.db.injuries)

#    def test_weapon_injury(self):
#        chandler = self.get_handler()

#    def test_mocking(self):
#        chandler = self.get_handler()

#    def test_wounding(self):
#        chandler = self.get_handler()

    def test_attack_keyframe(self):
        chandler = self.get_handler()
        chandler.add_action_to_stack(self.char1, self.char2, startup=5, totalframes=24, basedamage=4.0, shieldlag= 8, invulnerability = range(5, 6))
        chandler._sort_actions()
        totalframes = chandler._get_character_total_keyframes(self.char1)
        self.assertEqual(totalframes, 24)

    @patch("typeclasses.combat.handler.delay", mockdelay)
    def test_attack_combo(self):
        chandler = self.get_handler()
        chandler.db.maxframes = 100
        chandler.add_action_to_stack(self.char1, self.char2, startup=5, totalframes=24, basedamage=4.0, shieldlag=8, invulnerability = range(5, 6))
        chandler.add_action_to_stack(self.char1, self.char2, startup=5, totalframes=24, basedamage=4.0, shieldlag=8, invulnerability = range(5, 6))
        chandler.add_action_to_stack(self.char1, self.char2, startup=5, totalframes=24, basedamage=4.0, shieldlag=8, invulnerability = range(5, 6))
        chandler.add_action_to_stack(self.char1, self.char2, startup=5, totalframes=24, basedamage=4.0, shieldlag=8, invulnerability = range(5, 6))
        chandler.at_repeat()
        self.assertAlmostEqual(chandler.get_tilt(self.char2), 16, delta=.05)

    @patch("typeclasses.combat.handler.delay", mockdelay)
    def test_full_round_combat(self):
        chandler = self.get_handler()
        self.assertEqual(self.char1.ndb.combat_round_actions, [])
        chandler.add_action_to_stack(self.char1, self.char2, startup=15, totalframes=24, basedamage=8.0, shieldlag=8, invulnerability = (16, 17))
        chandler.add_action_to_stack(self.char1, self.char2, startup=5, totalframes=9, basedamage=4.0, shieldlag=8, invulnerability = (6, 7))
        chandler.add_action_to_stack(self.char1, self.char2, startup=11, totalframes=17, basedamage=6.0, shieldlag=8, invulnerability = (12, 13))
        chandler.add_action_to_stack(self.char2, self.char1, startup=10, totalframes=25, basedamage=9.0, shieldlag=8, invulnerability = (11, 12))
        chandler.add_action_to_stack(self.char2, self.char1, startup=10, totalframes=25, basedamage=9.0, shieldlag=8, invulnerability = (11, 12))
        chandler.at_repeat()
        self.assertNotEqual(chandler.get_tilt(self.char1), 0)
        self.assertEqual(chandler.get_tilt(self.char1), 9)
        self.assertEqual(chandler.get_tilt(self.char2), 10)
        self.assertEqual(self.char1.ndb.combat_round_actions, [])

    def test_cleanup(self):
        chandler = self.get_handler()
        chandler.remove_character(self.char1)
        self.assertIsNone(self.char1.ndb.tilt_handler)
        self.assertIsNone(self.char2.ndb.tilt_handler)

    def test_calc_severity(self):
        chandler = self.get_handler()
        damage = chandler._calc_injury_damage_modifier(100, .1)
        self.assertEquals(damage, 90)
        damage = chandler._calc_injury_damage_modifier(100, .4)
        self.assertEquals(damage, 60)
        damage = chandler._calc_injury_damage_modifier(100, .8)
        self.assertEquals(damage, 20)
        damage = chandler._calc_injury_damage_modifier(1000, .5)
        self.assertEquals(damage, 500)

 #   def test_injury_effect(self):
 #       chandler = self.get_handler()
 #       chandler.cause_injury(self.char1, location="right_arm", severity=.1)
 #       chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=100, totalframes=1000)
 #       chandler._process_action()
 #       self.assertNotEqual(chandler.get_tilt(self.char1), -100)

    def test_too_many_attacks(self):
        chandler = self.get_handler()
        chandler.db.maxframes = 240
        res = chandler.add_action_to_stack(self.char1, self.char2, totalframes=120)
        self.assertTrue(res)
        res = chandler.add_action_to_stack(self.char1, self.char2, totalframes=120)
        self.assertTrue(res)
        res = chandler.add_action_to_stack(self.char1, self.char2, totalframes=1)
        self.assertFalse(res)
        res = chandler.add_action_to_stack(self.char1, self.char2, totalframes=60000)
        self.assertFalse(res)

    def test_back_to_back_lulls(self):
        chandler = self.get_handler()
        chandler.at_repeat()
        chandler.at_repeat()
        #self.assertIsNone(self.char1.ndb.tilt_handler)

    def test_tilt_advantage(self):
        chandler = self.get_handler()
        percentage = chandler._calc_tilt_advantage(self.char1)
        self.assertAlmostEqual(percentage, 55, delta=.05)
        chandler._deal_tilt_damage(self.char2, self.char1, 10)
        percentage = chandler._calc_tilt_advantage(self.char1)
        self.assertAlmostEqual(percentage, 52.767, delta=.05)
        chandler._deal_tilt_damage(self.char2, self.char1, 10)
        percentage = chandler._calc_tilt_advantage(self.char1)
        self.assertAlmostEqual(percentage, 50.520, delta=.05)
        chandler._deal_tilt_damage(self.char2, self.char1, 50)
        percentage = chandler._calc_tilt_advantage(self.char1)
        self.assertAlmostEqual(percentage, 39.469, delta=.05)
        chandler._deal_tilt_damage(self.char2, self.char1, 50)
        percentage = chandler._calc_tilt_advantage(self.char1)
        self.assertAlmostEqual(percentage, 29.616, delta=.05)

    def test_interrupt_battle_string(self):
        chandler = self.get_handler()
        chandler.db.maxframes=60
        p1 = "SSSSXXWWWWWWWWWSSSSSSSSSSXWWWWWWSSSSSSSSSSSSSSSSSSSSSSSSSSSS"
        p2 = "SSSSSSSSXWWWWWWSSSSSSXWWWWWWSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS"
        ac = "SSSSSSIWWSSSSSWWSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSDDDDDDDDDDDD"
        ex = "SSSSIIIWWSSSSSSSSSXWWWWWWSSSSSSSSSSSSSSSSSSSSSSSSSSSSSDDDDDD"

        p1, p2 = chandler._calc_interrupts(p1, p2)
        #self.assertEqual(ex, p2)

    def test_interrupt(self):
        chandler = self.get_handler()
        chandler.db.maxframes=60
        chandler.add_action_to_stack(self.char1, self.char2, startup=5, invulnerability=(6,7), totalframes=20, basedamage=5)
        chandler.add_action_to_stack(self.char2, self.char1, startup=13, invulnerability=(14,15), totalframes=34, basedamage=15)
        # Character 1 interrupts Character 2
        chandler.add_action_to_stack(self.char1, self.char2, startup=6, invulnerability=(7,8), totalframes=18, basedamage=5)
        chandler.add_action_to_stack(self.char2, self.char1, startup=2, invulnerability=(3,4), totalframes=6, basedamage=15)
        # Character 2 interrupts Character 1
        chandler.add_action_to_stack(self.char1, self.char2, startup=9, invulnerability=(10, 11, 12), totalframes=18, basedamage=13)
        chandler.add_action_to_stack(self.char2, self.char1, startup=9, invulnerability=(10, 11, 12), totalframes=17, basedamage=15)
        # No interrupts
        chandler._sort_actions()
        chandler._queue_actions()
        p1_results="SSSSSXXWWWWWWWWWWWWWIIISSSSSSSSSXXXWWWWWW"
        self.assertEqual(self.char1.ndb.battle_results, p1_results)
        p2_results="IIIIIISSXXWWSSSSSSSSSXXXWWWWW"
        self.assertEqual(self.char2.ndb.battle_results, p2_results)

    #@patch("typeclasses.combat.handler.delay", mockdelay)
    def test_block_design(self):
        chandler = self.get_handler()
        chandler.db.maxframes = 210
        chandler.add_action_to_stack(self.char1, self.char2, startup=5, totalframes=24, basedamage=4.0, shieldlag=8, invulnerability = range(5, 6))
        chandler.add_action_to_stack(self.char2, self.char1, startup=5, totalframes=24, basedamage=4.0, shieldlag=8, invulnerability = range(5, 6))
        chandler.add_action_to_stack(self.char1, self.char2, startup=5, totalframes=24, basedamage=4.0, shieldlag=8, invulnerability = range(5, 6))
        chandler.add_action_to_stack(self.char2, self.char1, startup=5, totalframes=24, basedamage=4.0, shieldlag=8, invulnerability = range(5, 6))

        chandler._sort_actions()
        chandler._queue_actions()
        chandler._render_battle_string()
        self.assertEqual(len(self.char1.ndb.battle_results), 210)
        self.assertEqual(len(self.char2.ndb.battle_results), 210)
       # p1_results="SSSSSXXWWWWWWWWWWWWWIIISSSSSSSSSXXXWWWWWW"
       # self.assertEqual(self.char1.ndb.battle_results, p1_results)

    def test_dodge(self):
        chandler = self.get_handler()
        chandler.db.maxframes=100
        chandler.add_action_to_stack(self.char1, self.char2, startup=7, totalframes=26, basedamage=0.0, shieldlag=-1, invulnerability = [8,9])
        chandler.add_action_to_stack(self.char2, self.char1, startup=7, totalframes=24, basedamage=4.0, shieldlag=8, invulnerability = [8,9])
        chandler.add_action_to_stack(self.char1, self.char2, key="dodge", startup=0, totalframes=26, basedamage=0.0, shieldlag=-1, invulnerability = [3,4,5,6,6,7,8,9,10,11,12,13,14,15,16,17,18])
        chandler.add_action_to_stack(self.char2, self.char1, startup=16, totalframes=24, basedamage=4.0, shieldlag=8, invulnerability = [17, 18, 19])
        chandler.add_action_to_stack(self.char1, self.char2, startup=7, totalframes=26, basedamage=0.0, shieldlag=-1, invulnerability = [8,9])
        chandler.add_action_to_stack(self.char2, self.char1, startup=16, totalframes=24, basedamage=4.0, shieldlag=8, invulnerability = [17, 18, 19])
        chandler._sort_actions()
        chandler._queue_actions()
        chandler._render_battle_string()
        p2_results="SSSSSSSXXWWWWWWWWWWWWWWWYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"
        self.assertEqual(self.char2.ndb.battle_results, p2_results)

class CombatCommands(CommandTest):
    def setUp(self):
        super().setUp()
        self.char1.db.statblock = statblock
        self.char2.db.statblock = statblock

    def get_handler(self):
        print(f"\nTesting {self.id()}: ")
        chandler = create_script(Tilt)
        chandler.add_character(self.char1)
        self.char1.ndb.target = self.char2
        chandler.add_character(self.char2)
        self.char2.ndb.target = self.char1
        return chandler

    @patch("typeclasses.combat.handler.delay", mockdelay)
    def test_jab(self):
        chandler = self.get_handler()
        from commands.combat import Jab
        self.assertEqual(chandler.db.actions, [])
        self.call(Jab(), "", caller=self.char1)
        self.call(Jab(), "", caller=self.char1)
        self.call(Jab(), "", caller=self.char2)
        chandler.at_repeat()
        self.assertNotEqual(chandler.get_tilt(self.char1), 0)
