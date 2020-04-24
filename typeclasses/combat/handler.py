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
    def at_script_creation(self):
        self.key = "TiltHandler"
        self.persistent = True
        self.interval = 15
        self.start_delay = True
        self.repeats = 0
        self.db.tilt = {}
        self.db.starting_wills = {}
        self.db.wills = {}
        self.db.actions = []

    def at_start(self):
        """
        Sets up the script
        """
        for character in self.db.wills.keys():
            self.add_character(character)

    def at_repeat(self):
        if len(self.db.wills) < 2:
            self.stop()
        self._sort_actions()
        self._queue_actions()
        self.db.actions = []
        self.msg_all("You sense a lull in the combat...")

    def at_stop(self):
        """
        Cleans up the script
        """
        characters = self.db.wills.keys()
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
        self.db.tilt.update({character: 0})
        character.ndb.combat_round_actions = []
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
        self._sort_actions()
        existing_actions = self.db.actions
        if not existing_actions and not character.ndb.combat_round_actions:
            if self.time_until_next_repeat() < self.interval/3:
                character.msg(f"It's too late for either player to start a flurry, wait until the next lull...",fullwidth=True)
                return False
            self.msg_all(f"|[200|w{character} readies an attack.|n")

        if (self._get_total_keyframes(character) + kwargs.get("keyframes", 1000))/1000 > self.interval:
            character.msg("You can't be sure a combo that long will work...", fullwidth=True)
            return False

        action_dict = { 
                "character": character,
                "target": target,
                }

        action_dict.update(kwargs)

        existing_actions.append(action_dict)

        if len(self.db.actions) > len(existing_actions)-1:
            return True
        else:
            return False

    def _sort_actions(self):
        """
        Sorts actions into two piles nondestructively
        """
        actions = self.db.actions
        while len(self.db.actions) > 0:
            action = self._get_next_action()
            if not action.get("character").ndb.combat_round_actions:
                action.get("character").ndb.combat_round_actions = []
            action.get("character").ndb.combat_round_actions.append(action)

    def _queue_actions(self):
        """
            Queue character actions with delays.
        """
        # print(f"Queuing actions for {character}")
        for character in self.db.wills.keys():
            process_stack = []
            keyframes_in_queue = 0
            action: dict
            while len(character.ndb.combat_round_actions) > 0:
                action = character.ndb.combat_round_actions.pop(0)
                if action.get("keyframes") > 0:
                    process_stack.append(
                            delay(
                                keyframes_in_queue/1000,
                                self._process_action,
                                action
                            )
                    )
                    keyframes_in_queue += action.get("keyframes", 1000)
                else: # Instant action
                    process_stack.append(self._process_action(action))
            #character.ndb.process_stack = defer.DeferredList(process_stack)
            #character.ndb.process_stack.addCallback(self._cleanup_round, character)
            character.ndb.process_stack = process_stack

    def _cleanup_round(self, character):
        del character.ndb.process_stack
        self.db.actions = []
        self.msg_all(f"There is a lull in the combat...")
        return True

    def _process_action(self, action=None):
        """
        Take the action that was previously delayed
        """

        if not action:
            action = self._get_next_action()
        character = action.get("character")
        target = action.get("target")
        attack_verb = action.get("attack_verb", "swing")
        weapon_noun = action.get("weapon_noun", "fist")
        tilt_damage = action.get("tilt_damage", 0)
        will_damage = action.get("will_damage", 0)

        severity = self._check_injury_severity(character)
        tilt_damage = self._calc_injury_damage_modifier(tilt_damage, severity)
        self._deal_tilt_damage(character, target, tilt_damage)
        self._deal_will_damage(character, target, will_damage)

        effect_str = ""
        if tilt_damage:
            effect_str += f"{character} feels the battle shift in their favor. "
            if tilt_damage <= 3 and target.ndb.combat_round_actions:
                if target.ndb.combat_round_actions[0].get("tilt_damage") > 3:
                    target.ndb.combat_round_actions[0]["tilt_damage"] -= 1
                    effect_str += f"{target} got beat to the punch! "

        if will_damage:
            effect_str += f"{target} loses some of their will to fight! "
        if will_damage >= 10 and target.ndb.combat_round_actions:
            target.ndb.combat_round_actions.pop(0)
            effect_str += f"Yowch!"

        effect_str.strip()
        self.msg_all(f"{character} {attack_verb} a {weapon_noun} at {target}. {effect_str}")
        self.loss_by_tilt()
        return True

    def msg_all(self, msg):
        for character in self.db.wills.keys():
            character.msg(f"|[200|w{msg}|n", fullwidth=True)

    def loss_by_tilt(self):
        characters = self.db.starting_wills.keys()
        blocked = False
        for character in characters:
            try:
                if self.get_tilt(character) > self.db.wills.get(character):
                    attackers = self.get_attackers(character)
                    for attacker in attackers:
                        if attacker.db.noflee:
                            blocked = True
                            self.msg_all(f"{character} tries to flee but is blocked by {attacker}!")
                            break
                    if not blocked:
                        self.msg_all(f"{character} has fled!")
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

    def get_tilt(self, character):
        return self.db.tilt.get(character)

    def get_attackers(self, character):
        """
        Gets the list of characters targeting a character
        """
        attackers=[]
        for participant in self.db.wills.keys():
            if participant.ndb.target == character:
                attackers.append(participant)
        return attackers

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

    def _deal_tilt_damage(self, character, target, damage):
        self.db.tilt.update({target: self.db.tilt.get(target) + damage})
        self.db.tilt.update({character: self.db.tilt.get(character) - damage})

    def _deal_will_damage(self, character, target, damage):
        self.db.wills.update({target: self.db.wills.get(target) - damage})

    def _check_injury_severity(self, character):
        severity = 0
        if character.db.injuries:
            severity += character.db.injuries.get("right_arm", 0)
            severity += round(character.db.injuries.get("left_arm", 0)/2)
        return severity

    def _calc_injury_damage_modifier(self, damage, severity=0):
        if damage and severity:
            return round(damage-(damage*severity))
        else:
            return damage
