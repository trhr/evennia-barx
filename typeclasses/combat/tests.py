from evennia.utils.test_resources import EvenniaTest
from typeclasses.combat.handler import Tilt
from evennia import create_script

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

    def test_script_creation(self)
        chandler = self.get_handler()
        self.assertExists(chandler)
