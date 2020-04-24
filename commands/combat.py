from commands.command import Command

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
            tilt_handler = create_script(Tilt)
            tilt_handler.add_character(self.caller, target=self.target)
            tilt_handler.add_character(self.target, target=self.caller)
            self.caller.location.msg_contents(f"{self.caller} has a bone to pick with {self.target}!")

class Jab(Command):
    """
    Throw a jab!
    """
    key = "jab"

    def func(self):
        if self.caller.ndb.tilt_handler:
            self.caller.ndb.tilt_handler.add_action_to_stack(self.caller, self.caller.ndb.target, tilt_damage=1, keyframes=80) # 1.25 DPS
            self.caller.msg("|[002|wAdded Jab to Stack|n", fullwidth=True)
        else:
            self.caller.msg("You're not in combat!")

class Punch(Command):
    """
    Throw a punch!
    """
    key = "punch"

    def func(self):
        if self.caller.ndb.tilt_handler:
            self.caller.ndb.tilt_handler.add_action_to_stack(self.caller, self.caller.ndb.target, tilt_damage=5, keyframes=400) #1.1 DPS
            self.caller.msg("|[002|wAdded Punch to Stack|n", fullwidth=True)
        else:
            self.caller.msg("You're not in combat!")

class Haymaker(Command):
    """
    Throw a punch!
    """
    key = "haymaker"

    def func(self):
        if self.caller.ndb.tilt_handler:
            self.caller.ndb.tilt_handler.add_action_to_stack(self.caller, self.caller.ndb.target, will_damage=10, keyframes=1000) # 1.0 DPS
            self.caller.msg("|[002|wAdded Haymaker to Stack|n", fullwidth=True)
        else:
            self.caller.msg("You're not in combat!")

class Guard(Command):
    """
    Into a guard!
    """

    def func(self):
        if self.caller.ndb.tilt_handler:
            self.caller.ndb.tilt_handler.add_action_to_stack(self.caller, self.caller, will_damage=-6, keyframes=450) # 1.1 HPS
            self.caller.msg("|[002|wAdded Guard to Stack|n", fullwidth=True)
        else:
            self.caller.msg("You're not in combat!")