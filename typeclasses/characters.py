"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter


class Character(DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.sniffed=[self]
        self.db.will=10
       #"|/|/$alt(HOW TO PLAY [READ THIS OR GET BIT],|230|225)|/|/Welcome to Barx! You are a dog. You have three commands.|/You can |*SNIFF|n other dogs, |*DIG|n up bones, or |*BURY|n your bones.|/(type 'help <command>' to learn more about using these commands.|/|/WINNING THE GAME: Win by being the dog with the most buried bones.|/|/KEEPING OTHER PEOPLE FROM WINNING: Dig up their bones. They become your bones.|/|/First to 10,000 points worth of buried bones wins. The server self-destructs at this point.|/|/|rReady to play? Type 'join'|/|/"

    def get_sniff_name(self, sniffer):
        if self in sniffer.db.sniffed:
            return self.key
        else:
            return "Someone"

    def msg(self, msg, **kwargs):
        if kwargs.get("fullwidth"):
            try:
                client_width = self.sessions.all()[0].protocol_flags.get("SCREENWIDTH", {0:80})
                client_width_px = client_width.get(0)
                msg = f"$pad({msg}, {client_width_px},c,-)"
            except IndexError:
                pass
        super().msg(msg)