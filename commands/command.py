"""
Commands

Commands describe the input the account can do to the game.

"""

from evennia import Command as BaseCommand
from evennia.utils.utils import inherits_from
from typeclasses.objects import Bones
from typeclasses.characters import Character

# from evennia import default_cmds


class Command(BaseCommand):
    """
    Inherit from this if you want to create your own command styles
    from scratch.  Note that Evennia's default commands inherits from
    MuxCommand instead.

    Note that the class's `__doc__` string (this text) is
    used by Evennia to create the automatic help entry for
    the command, so make sure to document consistently here.

    Each Command implements the following methods, called
    in this order (only func() is actually required):
        - at_pre_cmd(): If this returns anything truthy, execution is aborted.
        - parse(): Should perform any extra parsing needed on self.args
            and store the result on self.
        - func(): Performs the actual work.
        - at_post_cmd(): Extra actions, often things done after
            every command, like prompts.

    """

    pass

from world import wild

class Join(Command):
    key = "join"

    def func(self):
        if self.caller.location.dbref == "#21":
            wild.enter_wilderness(self.caller)
            self.msg("ARF ARF > X GON GIVE IT TO YOU < LOOK AROUND")

class Score(Command):
    key = "score"
 
    def func(self):
        # get all bones
#        from typeclasses.objects import Bones
#        bones = Bones.objects.all()
#        scores = {}
#        for bone in bones:
#            if bone.db.buried:
#                scores.update({bone.locks.get("control"): scores.get(bone.locks.get("control"),0)+bone.db.value})

#        self.msg("|r----Top |gDogs----|n")
#        self.msg("|rPlayer|-|-|-|-|-Score|n")
#        self.msg("---------------------------------------")
#        for k,v in scores.items():
#            self.msg(f"{k}|-|-|-|-{v}")
      from world.topdogs import scorelist

      self.msg(scorelist())

class Sniff(Command):
    """
    Sniff another dog to catch their trail and follow them around.
    Usage: sniff <character>

    """
    key = "sniff"
    target = None

    def parse(self):
       if not self.args:
           self.msg("Who would you like to sniff? Usage: 'sniff <character>'")
       else:
           self.target = self.caller.search(self.args.strip())
           if not inherits_from(self.target, Character):
               self.target = None
               self.msg("You can only sniff characters!")

    def func(self):
        if self.target:
            self.msg(f"You sniff {self.target}!")
            self.target.msg(f"{self.caller} sniffs you!")
            self.caller.db.sniffed+=[self.target]


class Bury(Command):
    """
    Bury any bones you find. This will increase your score.
    Usage: bury <bones>
    """
    key = "bury"
    target = None

    def parse(self):
        if not self.args:
           self.msg("What would you like to bury? Usage: 'bury <bones>'")
        else:
           self.target = self.caller.search(self.args.strip())
           if not inherits_from(self.target, Bones):
               self.target = None
               self.msg("You can only bury bones!")

    def func(self):
        if self.target:
            self.msg(f"Burying {self.target}")
            self.target.location = self.caller.location
            self.target.db.buried = True
            self.target.locks.add("view:none()")
            self.target.locks.add("get:none()")
            self.target.locks.add(f"control:pid({self.caller.dbref})")
            self.caller.location.msg_contents(f"{self.caller} digs up {self.target}!", exclude=self.caller)

class Unearth(Command):
    """
    Unearth someone else's poorly buried bones on the current map.
    Usage: unearth
    """
    key = "unearth"
    target = None

    def parse(self):
        self.target = self.caller.location.search("bones")
  
    def func(self):
        if self.target:
            self.target.locks.add("view:all()")
            self.target.locks.add("get:all()")
            self.target.locks.add("control:none()")
            self.target.location = self.caller
            self.msg(f"You dig up {target}!")
            self.caller.location.msg_contents(f"{self.caller} digs up {self.target}!", exclude=self.caller)

# -------------------------------------------------------------
#
# The default commands inherit from
#
#   evennia.commands.default.muxcommand.MuxCommand.
#
# If you want to make sweeping changes to default commands you can
# uncomment this copy of the MuxCommand parent and add
#
#   COMMAND_DEFAULT_CLASS = "commands.command.MuxCommand"
#
# to your settings file. Be warned that the default commands expect
# the functionality implemented in the parse() method, so be
# careful with what you change.
#
# -------------------------------------------------------------

# from evennia.utils import utils
#
#
# class MuxCommand(Command):
#     """
#     This sets up the basis for a MUX command. The idea
#     is that most other Mux-related commands should just
#     inherit from this and don't have to implement much
#     parsing of their own unless they do something particularly
#     advanced.
#
#     Note that the class's __doc__ string (this text) is
#     used by Evennia to create the automatic help entry for
#     the command, so make sure to document consistently here.
#     """
#     def has_perm(self, srcobj):
#         """
#         This is called by the cmdhandler to determine
#         if srcobj is allowed to execute this command.
#         We just show it here for completeness - we
#         are satisfied using the default check in Command.
#         """
#         return super().has_perm(srcobj)
#
#     def at_pre_cmd(self):
#         """
#         This hook is called before self.parse() on all commands
#         """
#         pass
#
#     def at_post_cmd(self):
#         """
#         This hook is called after the command has finished executing
#         (after self.func()).
#         """
#         pass
#
#     def parse(self):
#         """
#         This method is called by the cmdhandler once the command name
#         has been identified. It creates a new set of member variables
#         that can be later accessed from self.func() (see below)
#
#         The following variables are available for our use when entering this
#         method (from the command definition, and assigned on the fly by the
#         cmdhandler):
#            self.key - the name of this command ('look')
#            self.aliases - the aliases of this cmd ('l')
#            self.permissions - permission string for this command
#            self.help_category - overall category of command
#
#            self.caller - the object calling this command
#            self.cmdstring - the actual command name used to call this
#                             (this allows you to know which alias was used,
#                              for example)
#            self.args - the raw input; everything following self.cmdstring.
#            self.cmdset - the cmdset from which this command was picked. Not
#                          often used (useful for commands like 'help' or to
#                          list all available commands etc)
#            self.obj - the object on which this command was defined. It is often
#                          the same as self.caller.
#
#         A MUX command has the following possible syntax:
#
#           name[ with several words][/switch[/switch..]] arg1[,arg2,...] [[=|,] arg[,..]]
#
#         The 'name[ with several words]' part is already dealt with by the
#         cmdhandler at this point, and stored in self.cmdname (we don't use
#         it here). The rest of the command is stored in self.args, which can
#         start with the switch indicator /.
#
#         This parser breaks self.args into its constituents and stores them in the
#         following variables:
#           self.switches = [list of /switches (without the /)]
#           self.raw = This is the raw argument input, including switches
#           self.args = This is re-defined to be everything *except* the switches
#           self.lhs = Everything to the left of = (lhs:'left-hand side'). If
#                      no = is found, this is identical to self.args.
#           self.rhs: Everything to the right of = (rhs:'right-hand side').
#                     If no '=' is found, this is None.
#           self.lhslist - [self.lhs split into a list by comma]
#           self.rhslist - [list of self.rhs split into a list by comma]
#           self.arglist = [list of space-separated args (stripped, including '=' if it exists)]
#
#           All args and list members are stripped of excess whitespace around the
#           strings, but case is preserved.
#         """
#         raw = self.args
#         args = raw.strip()
#
#         # split out switches
#         switches = []
#         if args and len(args) > 1 and args[0] == "/":
#             # we have a switch, or a set of switches. These end with a space.
#             switches = args[1:].split(None, 1)
#             if len(switches) > 1:
#                 switches, args = switches
#                 switches = switches.split('/')
#             else:
#                 args = ""
#                 switches = switches[0].split('/')
#         arglist = [arg.strip() for arg in args.split()]
#
#         # check for arg1, arg2, ... = argA, argB, ... constructs
#         lhs, rhs = args, None
#         lhslist, rhslist = [arg.strip() for arg in args.split(',')], []
#         if args and '=' in args:
#             lhs, rhs = [arg.strip() for arg in args.split('=', 1)]
#             lhslist = [arg.strip() for arg in lhs.split(',')]
#             rhslist = [arg.strip() for arg in rhs.split(',')]
#
#         # save to object properties:
#         self.raw = raw
#         self.switches = switches
#         self.args = args.strip()
#         self.arglist = arglist
#         self.lhs = lhs
#         self.lhslist = lhslist
#         self.rhs = rhs
#         self.rhslist = rhslist
#
#         # if the class has the account_caller property set on itself, we make
#         # sure that self.caller is always the account if possible. We also create
#         # a special property "character" for the puppeted object, if any. This
#         # is convenient for commands defined on the Account only.
#         if hasattr(self, "account_caller") and self.account_caller:
#             if utils.inherits_from(self.caller, "evennia.objects.objects.DefaultObject"):
#                 # caller is an Object/Character
#                 self.character = self.caller
#                 self.caller = self.caller.account
#             elif utils.inherits_from(self.caller, "evennia.accounts.accounts.DefaultAccount"):
#                 # caller was already an Account
#                 self.character = self.caller.get_puppet(self.session)
#             else:
#                 self.character = None
