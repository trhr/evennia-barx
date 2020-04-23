from evennia.utils.test_resources import EvenniaTest
from typeclasses.combat.handler import Tilt
from evennia import create_script
import time
from evennia.utils import delay

class TestCombat(EvenniaTest):

    def setUp(self):
        super().setUp()
        self.char1.db.will=100
        self.char2.db.will=50

    def get_handler(self):
        chandler = create_script(Tilt)
        chandler.add_character(self.char1)
        chandler.add_character(self.char2)
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
        self.assertEquals(chandler.get_current_tilt(), 0)

    def test_attack(self):
        chandler = self.get_handler()
        self.assertTrue(chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=5))
        self.assertTrue(chandler._process_action())
        self.assertNotEquals(chandler.db.tilt, 0)

    def test_victory_by_tilt(self):
        chandler = self.get_handler()
        chandler.db.tilt=250
        chandler.loss_by_tilt()
        self.assertIsNone(self.char1.ndb.tilt_handler)

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

    def test_attack_combo(self):
        chandler = self.get_handler()
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=1, keyframes=10000)
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=1, keyframes=10000)
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=1, keyframes=10000)
        chandler.add_action_to_stack(self.char2, self.char1, tilt_damage=1, keyframes=10000)
        chandler.add_action_to_stack(self.char2, self.char1, tilt_damage=1, keyframes=10000)
        chandler.add_action_to_stack(self.char2, self.char1, tilt_damage=1, keyframes=10000)
        chandler._sort_actions()
        self.assertEqual(len(self.char1.ndb.combat_round_actions), 3)
        self.assertEqual(len(self.char2.ndb.combat_round_actions), 3)

    def test_attack_keyframe(self):
        chandler = self.get_handler()
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=1, keyframes=500)
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=1, keyframes=500)
        chandler._sort_actions()
        self.assertEqual(len(self.char1.ndb.combat_round_actions), 2)
        total_keyframes = chandler._get_total_keyframes(self.char1)
        self.assertEqual(total_keyframes, 1000)


    def test_combat_lull(self):
        chandler = self.get_handler()
        self.assertIsNone(self.char1.ndb.combat_round_actions)
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=5, keyframes=200)
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=2, keyframes=400)
        chandler.add_action_to_stack(self.char1, self.char2, tilt_damage=3, keyframes=600)
        chandler.add_action_to_stack(self.char2, self.char1, tilt_damage=6, keyframes=200)
        chandler.add_action_to_stack(self.char2, self.char1, tilt_damage=8, keyframes=400)
        chandler.add_action_to_stack(self.char2, self.char1, tilt_damage=1, keyframes=600)
        chandler._sort_actions()
        self.assertIsNotNone(self.char1.ndb.combat_round_actions)
        char1_stack = chandler._queue_actions(self.char1)
        char2_stack = chandler._queue_actions(self.char2)
        self.assertIsNotNone(self.char1.ndb.combat_round_actions)
        self.assertEqual(chandler.db.tilt, 0)
        # TODO Test the deferred value after all the actions have been added

    def resolve_full_round_combat(self):
        chandler = self.get_handler()

    def test_nosurrender(self):
        chandler = self.get_handler
