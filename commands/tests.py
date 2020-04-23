from evennia.commands.default.tests import CommandTest
from commands.command import Attack

class TestCustomCommands(CommandTest):
    "tests the custom commands"
    def test_attack(self):
        self.call(Attack(), "Char2", "Char has a bone to pick with Char2!")