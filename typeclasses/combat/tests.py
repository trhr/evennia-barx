from evennia.utils.test_resources import EvenniaTest, mockdelay, mockdeferLater
from typeclasses.combat.handler import Tilt
from evennia import create_script
from mock import Mock, patch


class TestCombat(EvenniaTest):

    def setUp(self):
        super().setUp()
        self.char1.db.will=500
        self.char2.db.will=500

    def get_handler(self):
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

    def test_tilt_exists(self):
        chandler = self.get_handler()
        self.assertEquals(chandler.get_tilt(self.char1), 0)

    def test_attack(self):
        chandler = self.get_handler()
        self.assertTrue(chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=5))
        self.assertTrue(chandler._process_action())
        self.assertNotEquals(chandler.get_tilt(self.char1), 0)
        self.assertEquals(chandler.get_tilt(self.char2), 5)

    def test_victory_by_tilt(self):
        chandler = self.get_handler()
        chandler.db.tilt[self.char1]=100000
        chandler.loss_by_tilt()
        self.assertIsNone(self.char1.ndb.tilt_handler)

    def test_nosurrender(self):
        chandler = self.get_handler()
        chandler.db.tilt[self.char1]=250
        self.char2.db.noflee = True
        chandler.loss_by_tilt()
        self.assertIsNotNone(self.char1.ndb.tilt_handler)

    def test_square_hit(self):
        chandler = self.get_handler()
        self.assertTrue(chandler.add_action_to_stack(self.char1, self.char2, will_damage=5))
        self.assertTrue(chandler._process_action())
        self.assertNotEquals(self.char2.db.will, chandler.db.wills.get(self.char2))

    def test_light_hit(self):
        chandler = self.get_handler()
        self.assertTrue(chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=5))
        self.assertTrue(chandler._process_action())
        self.assertNotEquals(chandler.db.tilt, 0)

    def test_injury(self):
        chandler = self.get_handler()
        chandler.cause_injury(self.char1, location="right_arm", severity=1)
        self.assertIsNotNone(self.char1.db.injuries)

#    def test_weapon_injury(self):
#        chandler = self.get_handler()

#    def test_mocking(self):
#        chandler = self.get_handler()

#    def test_wounding(self):
#        chandler = self.get_handler()

    def test_attack_keyframe(self):
        chandler = self.get_handler()
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=1, keyframes=500)
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=1, keyframes=500)
        chandler._sort_actions()
        self.assertEqual(len(self.char1.ndb.combat_round_actions), 2)
        total_keyframes = chandler._get_total_keyframes(self.char1)
        self.assertEqual(total_keyframes, 1000)

    def test_attack_combo(self):
        chandler = self.get_handler()
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=5, keyframes=0)
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=5, keyframes=0)
        chandler.add_action_to_stack(self.char2, self.char1, tilt_damage=8, keyframes=0)
        chandler.add_action_to_stack(self.char2, self.char1, tilt_damage=8, keyframes=0)
        chandler._sort_actions()
        self.assertEqual(len(self.char1.ndb.combat_round_actions), 2)
        self.assertEqual(len(self.char2.ndb.combat_round_actions), 2)
        chandler.at_repeat()
        self.assertEqual(chandler.get_tilt(self.char1), 6)

    @patch("typeclasses.combat.handler.delay", mockdelay)
    def test_full_round_combat(self):
        chandler = self.get_handler()
        self.assertEqual(self.char1.ndb.combat_round_actions, [])
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=1, keyframes=1000)
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=2, keyframes=1000)
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=3, keyframes=1000)
        chandler.add_action_to_stack(self.char2, self.char1, tilt_damage=6, keyframes=1000)
        chandler.add_action_to_stack(self.char2, self.char1, tilt_damage=8, keyframes=1000)
        chandler.add_action_to_stack(self.char2, self.char1, tilt_damage=1, keyframes=1000)
        chandler.at_repeat()
        self.assertEqual(chandler.get_tilt(self.char1), 6)
        self.assertEqual(self.char1.ndb.combat_round_actions, [])

    def test_cleanup(self):
        chandler = self.get_handler()
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=1, keyframes=1000)
        chandler.at_repeat()
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

    def test_injury_effect(self):
        chandler = self.get_handler()
        chandler.cause_injury(self.char1, location="right_arm", severity=.1)
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=100, keyframes=1000)
        chandler._process_action()
        self.assertNotEqual(chandler.get_tilt(self.char1), -100)

    def test_too_many_attacks(self):
        chandler = self.get_handler()
        res = chandler.add_action_to_stack(self.char1,self.char2, keyframes=6000)
        self.assertTrue(res)
        res = chandler.add_action_to_stack(self.char1, self.char2, keyframes=6000)
        self.assertTrue(res)
        res = chandler.add_action_to_stack(self.char1, self.char2, keyframes=6000)
        self.assertFalse(res)

