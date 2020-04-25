from typeclasses.scripts import DefaultScript
from evennia.utils import delay
from world.breeds.donkey_kong import statblock


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
        self.repeats = 0
        self.start_delay = True
        self.interval = 15
        self.persistent = True
        self.key = "TiltHandler"
        self.db.tilt = {}
        self.db.target = {}
        self.db.actions = []

    def at_start(self):
        """
        Sets up the script
        """
        for character in self.db.tilt.keys():
            target = self.db.target.get(character, None)
            self.add_character(character, target)
        self.db.summary = ""

    def at_repeat(self):
        if len(self.db.tilt) < 2:
            self.stop()
        self._sort_actions()
        self._queue_actions()
        self._cleanup_round()

    def at_stop(self):
        """
        Cleans up the script
        """
        characters = self.db.tilt.keys()
        for character in characters:
            character.msg(f"|[102|w{self.db.summary}|n", fullwidth=True)
            self.remove_character(character)

    def add_character(self, character, target=None):
        """
        A new character has joined the battle
        """
        character.ndb.tilt_handler = self
        if target:
            character.ndb.target = target
            self.db.target.update({character: target})
        self.db.tilt.update({character: self.get_tilt(character)})
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
        del self.db.tilt[character]
        if len(self.db.tilt) < 2:
            self.stop()

    def add_action_to_stack(self, character, target, **kwargs):
        """
        Queues an action into the action dict.

        Kwargs:
           startup
           totalframes
           basedamage
           shieldlag
           invulnerability
        """
        existing_actions = self.db.actions
        #if not existing_actions and not character.ndb.combat_round_actions:
        #    if self.time_until_next_repeat() < self.interval/3:
        #        character.msg(f"It's too late for either player to start a flurry. Wait until the next lull...", fullwidth=True)
        #        return False
        #    self.msg_all(f"|[200|w{character} readies an attack.|n")



        action_dict = { 
                "character": character,
                "target": target,
                }

        action_dict.update(kwargs)

        if self._keyframes_to_seconds(
                self._get_character_total_keyframes(character) + self._get_keyframes(action_dict)
        ) > self.interval:
            character.msg("You can't be sure a combo that long will work...", fullwidth=True)
            return False

        existing_actions.append(action_dict)
        print(existing_actions)
        if len(self.db.actions) > len(existing_actions)-1:
            return True
        else:
            return False

    def _cleanup_round(self):
        for character in self.db.tilt.keys():
            del character.ndb.process_stack
            character.ndb.combat_round_actions=[]
        self.db.actions = []
        for character in self.db.tilt.keys():
            character.msg(f"|[102|w{self.db.summary}|n", fullwidth=True)
        self.db.summary = ""
        return True

    def _sort_actions(self):
        """
        Sorts actions into two piles nondestructively
        """
        actions = self.db.actions
        while len(self.db.actions) > 0:
            action = self._get_next_action()
            action.get("character").ndb.combat_round_actions.append(action)

    def _queue_actions(self):
        """
            Queue character actions with delays.
        """

        for character in self.db.tilt.keys():
            process_stack = []
            keyframes_in_queue = self._get_character_total_keyframes(character)
            print(f"[{keyframes_in_queue} kf in q]")
            action: dict

            while character.ndb.combat_round_actions:
                action = character.ndb.combat_round_actions.pop(0)

                if action.get("totalframes", 0) > 0:
                    process_stack.append(
                            delay(
                                keyframes_in_queue/60 + action.get("startup", 0),
                                self._process_action,
                                action
                            )
                    )
                    keyframes_in_queue += action.get("totalframes", 0)
                else: # Instant action
                    process_stack.append(self._process_action(action))
            #except (TypeError, ValueError):
            #    pass

            character.ndb.process_stack = process_stack


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
        baseknockback = action.get("baseknockback", 0)
        basedamage = action.get("basedamage", 0)

        #severity = self._check_injury_severity(character)
        #tilt_damage = self._calc_injury_damage_modifier(tilt_damage, severity)
        #tilt_damage = tilt_damage*(self._calc_tilt_advantage(character)/100)
        freshness = 0
        damage = self._calc_damage_modifiers(basedamage, freshness)
        print(f"[{damage} dealt]")
        self._deal_tilt_damage(character, target, damage)

        effect_str = ""
#        if basedamage:
#            effect_str += f"{character} feels the battle shift in their favor. "
            #if basedamage <= 5 and target.ndb.combat_round_actions:
               # if target.ndb.combat_round_actions[0].get("basedamage") > 3:
               #     target.ndb.combat_round_actions[0]["basedamage"] -= 1
               #     effect_str += f"{target} got beat to the punch! "

#        if will_damage > 0:
#            effect_str += f"{target} loses some of their will to fight! "
#        else:
#            effect_str += f"{target} feels emboldened by the battle! "

#        if will_damage >= 10 and target.ndb.combat_round_actions:
#            target.ndb.combat_round_actions.pop(0)
#            effect_str += f"Yowch!"

        effect_str.strip()
        self.msg_all(f"{character} {attack_verb} a {weapon_noun} at {target}. {effect_str}")
        knockback = self.calc_knockback(self.get_tilt(target), basedamage, baseknockback, target)
        print(f"[{knockback}] knockback")
        self.loss_by_tilt(target, knockback)
        return True

    def msg_all(self, msg):
        if self.db.tilt:
            for character in self.db.tilt.keys():
                character.msg(f"|[200|w{msg}|n", fullwidth=True)
        self.db.summary = f"{self.db.summary} {msg}"

    def loss_by_tilt(self, character, knockback):
        if knockback > character.db.statblock.get("knockback_sustained"):
            self.msg_all(f"{character} has been knocked out!")
            self.remove_character(character)

    def cause_injury(self, character, **kwargs):
        location = kwargs.get("location", None)
        severity = kwargs.get("severity", None)

        if not character.db.injuries:
            character.db.injuries = {}

        if location:
            character.db.injuries.update({location: severity})

    def get_tilt(self, character):
        return self.db.tilt.get(character, 0)

    def get_attackers(self, character):
        """
        Gets the list of characters targeting a character
        """
        attackers=[]
        for participant in self.db.tilt.keys():
            if participant.ndb.target == character:
                attackers.append(participant)
        return attackers

    def _get_next_action(self):
        """Remove the next action from the queue and return it"""
        return self.db.actions.pop(0)

    def _keyframes_to_seconds(self, keyframes):
        return keyframes/60

    def _get_character_total_keyframes(self, character):
        total = 0
        for action in character.ndb.combat_round_actions:
            total += action.get("totalframes", 60)
        return total

    def _get_keyframes(self, action):
        return action.get("totalframes", 60)

    def _deal_tilt_damage(self, character, target, damage):
        self.db.tilt.update({target: self.db.tilt.get(target) + damage})

#    def _deal_will_damage(self, character, target, damage):
#        self.db.wills.update({target: self.db.wills.get(target) - damage})

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

    def _calc_tilt_advantage(self, character):
        tilt = self.get_tilt(character)
        import math
        return 1/(1+math.exp(tilt/100-0.22314))*90+5

    def _calc_damage_modifiers(self, basedamage, freshness):
        return basedamage

    def calc_knockback(self, p, d, b, character):
        w = 100
        s = 1.0
        r = 1
        return ((((((p/10)+((p*d)/20))*w*1.4)+18)*s)+b)*r

    def _add_to_key_summary(self, action):
        """
        ||||HAYMAKER||||
        """
        totalframes = action.get("totalframes")
        return f"$pad({action.get('key')},{totalframes},c,|[200|w||)|n"

    def show_battle_summary(self):
        pass