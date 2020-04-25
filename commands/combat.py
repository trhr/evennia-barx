"""
Startup: The amount of frames it takes to hit
TotalFrames: The total duration of a move before the character can begin a new move
BaseDamage: Damage dealt without 1v1 damage multiplier or move staleness/freshness bonus
Shieldlag: The unique amount of hitlag (freeze frames) when hitting a shield.
Invulnerability: Character cannot be hit by an attack on these frames
"""

from commands.command import Command
from evennia import create_script
from typeclasses.combat.handler import Tilt
from world.breeds.donkey_kong import statblock

def _is_valid_attack(character):
    if not character.ndb.tilt_handler:
        character.msg("You're not in combat!")
        return False
    else:
        character.msg("|[002|wAttack queued|n")

class Attack(Command):
    """
    Start a fight!
    """

    key = "kill"
    aliases = ["attack", "fight"]
    target = None

    def parse(self):
        if self.args:
            self.target = self.caller.search(self.args.strip())
        else:
            self.caller.msg("Fight who?")

    def func(self):
        if self.target:
            if not self.caller.ndb.tilt_handler:
                tilt_handler = create_script(Tilt)
                tilt_handler.add_character(self.caller, target=self.target)
                tilt_handler.add_character(self.target, target=self.caller)
                self.caller.location.msg_contents(f"{self.caller} has a bone to pick with {self.target}!")
            else:
                self.caller.msg(f"You're already in combat with {self.caller.ndb.target}!")
        else:
            self.caller.msg("Who would you like to fight?")

class Jab(Command):
    """
    Jabs can be executed up to three times in a row.
    """

    key = "jab"

    def func(self):
        if _is_valid_attack(self.caller):
            self.caller.ndb.tilt_handler.add_action_to_stack(
                self.caller,
                self.caller.ndb.target,
                **statblock.get("attacks").get("jab1")
            )

class Punch(Command):
    """
    A good middling attack.
    """
    key = "punch"

    def func(self):
        if _is_valid_attack(self.caller):
            self.caller.ndb.tilt_handler.add_action_to_stack(
                self.caller,
                self.caller.ndb.target,
                **statblock.get("attacks").get("punch")
            )


class Haymaker(Command):
    """
    A good middling attack.
    """
    key = "haymaker"

    def func(self):
        if _is_valid_attack(self.caller):
            self.caller.ndb.tilt_handler.add_action_to_stack(
                self.caller,
                self.caller.ndb.target,
                **statblock.get("attacks").get("haymaker")
            )

class Special(Command):
    """
    Its different for every breed!
    """
    key = "special"

    def func(self):
        if _is_valid_attack(self.caller):
            self.caller.ndb.tilt_handler.add_action_to_stack(
                self.caller,
                self.caller.ndb.target,
                **statblock.get("attacks").get("special")
            )

class Stun(Command):
    """
    Attack and stun.
    """
    key = "stun"

    def func(self):
        if _is_valid_attack(self.caller):
            self.caller.ndb.tilt_handler.add_action_to_stack(
                self.caller,
                self.caller.ndb.target,
                **statblock.get("attacks").get("stun")
            )

class Grab(Command):
    """
    Grab your opponent and don't let go.
    """
    key = "grab"

    def func(self):
        if _is_valid_attack(self.caller):
            self.caller.ndb.tilt_handler.add_action_to_stack(
                self.caller,
                self.caller.ndb.target,
                **statblock.get("attacks").get("grab")
            )


class Dodge(Command):
    """
    Move out of the way.
    """
    key = "dodge"

    def func(self):
        if _is_valid_attack(self.caller):
            self.caller.ndb.tilt_handler.add_action_to_stack(
                self.caller,
                self.caller.ndb.target,
                **statblock.get("attacks").get("dodge")
            )


