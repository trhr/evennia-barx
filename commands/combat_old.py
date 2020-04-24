
class Jab(Command):
    """
    Throw a jab!
    """
    key = "jab"

    def func(self):
        if self.caller.ndb.tilt_handler:
            self.caller.ndb.tilt_handler.add_action_to_stack(self.caller, self.caller.ndb.target, tilt_damage=1, keyframes=400) # 2.5 DPS
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
            self.caller.ndb.tilt_handler.add_action_to_stack(self.caller, self.caller.ndb.target, tilt_damage=5, keyframes=1000) # 5.0 DPS
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
            self.caller.ndb.tilt_handler.add_action_to_stack(self.caller, self.caller.ndb.target, will_damage=10, keyframes=1000) # 10.0 DPS
            self.caller.msg("|[002|wAdded Haymaker to Stack|n", fullwidth=True)
        else:
            self.caller.msg("You're not in combat!")

class Guard(Command):
    """
    Into a guard!
    """
    key = "guard"

    def func(self):
        if self.caller.ndb.tilt_handler:
            self.caller.ndb.tilt_handler.add_action_to_stack(self.caller, self.caller, will_damage=-6, keyframes=333) # 18 HPS
            self.caller.msg("|[002|wAdded Guard to Stack|n", fullwidth=True)
        else:
            self.caller.msg("You're not in combat!")

class Grapple(Command):
    """
    Hold them close and never let go
    """

    key = "grapple"

    def func(self):
        if self.caller.ndb.tilt_handler:
            self.caller.ndb.tilt_handler.add_action_to_stack(self.caller, self.target, condition="grappled", keyframes=4000)
            self.caller.msg("[[002|wAdded Grapple to Stack|n", fullwidth=True)
        else:
            self.caller.msg("You're not in combat!")