from typeclasses.scripts import DefaultScript
from evennia.utils import delay
from twisted.internet import defer

class Tilt(DefaultScript):
    """
    The Parameters of Combat

    - Combat can be visualized as a number line with a start position of "0." This is called the 'Tilt'
    - Combat ends when the value of the Tilt exceeds the will of either opponent to fight, e.g. A_WILL |-------0---| B_WILL
    - Being squarely hit decreases the Will of the target to fight
    - Being lightly hit increases the tilt in favor of the person hitting
    ---- QED: Combat success balances on how much someone "wants" to fight and badly they are "losing"

    - Being injured decreases effectiveness of fighting, e.g. two highly injured players won't hurt each other as much
    - Weapons injure differently; piercing weapons tend to crit, not wound; crushing weapons tend to wound, not crit, etc.
    - Mocking an opponent may increase or decrease their 'will' to fight without injury; so might persuasion or flattery.
    - Wounding tends to happen on the extremities. The head, neck, and torso are all 'vitals' and should be treated differently.
    -----QED: Inflicting injuries is a valid way to win a combat, but not the only way

    - Combat occurs in a keyframe timeline. Some creatures and attacks are simply faster. These attacks may be interrupted or have their effectiveness changed by attacks with shorter durations.
    - Combat occurs in combinations. Multiple 'frames' can follow each other
    - However, combat also regularly 'lulls,' either due to an injury, tiredness, or simply having nothing else to do.

    """

    key = "TiltHandler"
    persistent = True
    interval = 15

    def at_start(self):
        """
        Sets up the script
        """
        self.db.tilt = 0
        self.db.starting_wills = {}
        self.db.wills = {}
        self.db.actions = []

    def at_repeat(self):
        if len(self.db.wills)<2:
            self.stop()
        self._sort_actions()
        for character in self.db.wills.keys():
            self._queue_actions(character)


    def at_stop(self):
        """
        Cleans up the script
        """
        characters = self.db.starting_wills.keys()
        for character in characters:
            self.remove_character(character)

    def add_character(self, character, target=None):
        """
        A new character has joined the battle
        """
        character.ndb.tilt_handler = self
        if not character.ndb.target:
            character.ndb.target = target
        self.db.starting_wills.update({character: character.db.will})
        self.db.wills.update({character: character.db.will})
        return True

    def remove_character(self, character):
        """
        A character has left the battle
        """
        del character.ndb.tilt_handler
        del character.ndb.combat_round_actions
        del character.ndb.target
        del character.ndb.process_stack
        del self.db.starting_wills[character]
        del self.db.wills[character]
        if len(self.db.wills) < 2:
            self.stop()

    def add_action_to_stack(self, character, target, **kwargs):
        """
        Queues an action into the action dict.

        Kwargs:
           tilt_damage
           will_damage
           keyframes
        """

        existing_actions = self.db.actions

        action_dict = { 
                "character" : character,
                "target" : target,
                }

        action_dict.update(kwargs)

        existing_actions.append(action_dict)

        if len(self.db.actions) > len(existing_actions)-1:
            return True
        else:
            return False

    def _sort_actions(self):
        """
        Sorts actions into two piles
        """
        actions = self.db.actions
        while len(self.db.actions) > 0:
            action = self._get_next_action()
            if not action.get("character").ndb.combat_round_actions:
                action.get("character").ndb.combat_round_actions = []
            action.get("character").ndb.combat_round_actions.append(action)

    def _queue_actions(self, character):
        """
            Queue a character's actions with delays.
        """
        actions = character.ndb.combat_round_actions
        process_stack = []
        keyframes_in_queue = 0
        action: dict
        while len(actions) > 0:
            action = actions.pop(0)
            process_stack.append(
                    delay(
                        keyframes_in_queue/1000,
                        self._process_action,
                        action
                    )
            )
            keyframes_in_queue += action.get("keyframes", 1000)
        character.ndb.process_stack = defer.DeferredList(process_stack)
        character.ndb.process_stack.addCallback(self._cleanup_round, character)
        return character.ndb.process_stack

    def _cleanup_round(self, character):
        del character.ndb.process_stack
        del character.ndb.combat_round_actions

    def _process_action(self, action=None):
        """
        Take the action that was previously delayed
        """
        if not action:
            action = self._get_next_action()

        character = action.get("character")
        target = action.get("target")
        tilt_damage = action.get("tilt_damage", 0)
        will_damage = action.get("will_damage", 0)

        self.db.tilt += tilt_damage
        self.db.wills.update({target: self.db.wills.get(target) - will_damage})
        self.msg_all(f"Tilt: {self.db.tilt}")
        return True

    def msg_all(self, msg):
        for character in self.db.wills.keys():
            character.msg(msg)

    def loss_by_tilt(self):
        characters = self.db.starting_wills.keys()
        for character in characters:
            try:
                if self.db.tilt > self.db.wills.get(character):
                    self.remove_character(character)
            except AttributeError:
                pass

    def cause_injury(self, character, **kwargs):
        location = kwargs.get("location", None)
        severity = kwargs.get("severity", None)

        if not character.db.injuries:
            character.db.injuries = {}

        if location:
            character.db.injuries.update({location: severity})

    def get_current_tilt(self):
        return self.db.tilt

    def _get_next_action(self):
        "Remove the next action from the queue and return it"
        return self.db.actions.pop(0)

    def _keyframes_to_seconds(self, action):
        return action.get("keyframes", 1000)/1000

    def _get_total_keyframes(self, character):
        total = 0
        for action in character.ndb.combat_round_actions:
            total += action.get("keyframes", 1000)
        return total
