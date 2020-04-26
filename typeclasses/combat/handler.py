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
        self.db.maxframes = 240

    def at_start(self):
        """
        Sets up the script
        """
        for character in self.db.tilt.keys():
            target = self.db.target.get(character, None)
            self.add_character(character, target)

    def at_repeat(self):
        self.msg_all("|[520|004]]]]]]]]]  T H E   S U R G E   I S   O N   ]]]")

        if len(self.db.tilt) < 2:
            self.stop()
        self._sort_actions()
        self._queue_actions()
        wait_frames = 0
        for character in self.db.tilt:
            if character.ndb.keyframes_in_queue > wait_frames:
                wait_frames = character.ndb.keyframes_in_queue
        delay(self._keyframes_to_seconds(wait_frames), self._cleanup_round)

    def at_stop(self):
        """
        Cleans up the script
        """
        self.show_battle_summary()
        characters = self.db.tilt.keys()
        for character in characters:
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
        character.ndb.battle_results = ""
        character.ndb.keyframes_in_queue = 0
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
        if not existing_actions and not character.ndb.combat_round_actions:
            if self.time_until_next_repeat() < self.interval/3:
                character.msg(f"It's too late for either player to start a flurry. Wait until the next lull...")
                return False
            self.msg_all(f"|[200|w|-{character} readies an attack.|n")
            if not self.db.first_to_act:
                self.db.first_to_act = character

        action_dict = { 
                "character": character,
                "target": target,
                }

        action_dict.update(kwargs)

        if self._get_character_total_keyframes(character) + self._get_keyframes(action_dict) > self.db.maxframes:
            character.msg("You can't plan that far ahead!")
            return False

        existing_actions.append(action_dict)

        if len(self.db.actions) > len(existing_actions)-1:
            self._sort_actions()
            return True
        else:
            return False

    def _render_battle_string(self):
        for character in self.db.tilt.keys():
            while len(character.ndb.battle_results) < self.db.maxframes:
                character.ndb.battle_results+="Z"
        self.show_battle_summary()

    def _cleanup_round(self):
        for character in self.db.tilt.keys():
            del character.ndb.process_stack
            character.ndb.keyframes_in_queue=0
            character.ndb.combat_round_actions=[]
            character.ndb.battle_results = ""
        self.db.actions = []
        self.db.first_to_act = None

        return True

    def _sort_actions(self):
        """Sorts actions into two piles"""
        while self.db.actions:
            action = self._get_next_action()
            action.get("character").ndb.combat_round_actions.append(action)

    def _interrupt_next_action(self):
        participants = sorted(self.db.tilt.keys(), reverse=True, key=lambda p: p.db.statblock.get("weight"))
        for defender in participants:
            if defender.ndb.combat_round_actions:
                defn = defender.ndb.combat_round_actions[0]
                for attacker in self.get_attackers(defender):
                    if attacker.ndb.combat_round_actions:
                        atk = attacker.ndb.combat_round_actions[0]
                        if max(atk.get("invulnerability")) < defn.get("startup"):
                            defn.update({"basedamage": 0, "totalframes": min(atk.get("invulnerability")), "interrupted": True, "startup":0})



    def _queue_actions(self):
        """Queue character actions with delays."""

        participants = sorted(self.db.tilt.keys(), reverse=True, key=lambda p: p.db.statblock.get("weight"))

        for character in participants:
            keyframes_in_queue = 0

            while character.ndb.combat_round_actions:
                action = character.ndb.combat_round_actions.pop(0)
                startup = action.get("startup", 0)
                totalframes = action.get("totalframes", 0)
                invuln = action.get("invulnerability", 0)
                key = action.get('key', "")

                delay(
                    self._keyframes_to_seconds(keyframes_in_queue) + startup,
                    self._process_action,
                    action
                )
                keyframes_in_queue += totalframes

                ### BLOCK DESIGN
                # X 'INTERRUPTS' S
                if action.get('interrupted'):
                    for i in range (0, totalframes):
                        character.ndb.battle_results+="I"
                else:
                    for i in range (0, startup):
                        character.ndb.battle_results += "S"
                    if max(invuln) >= startup:
                        for i in range(startup, max(invuln)):
                            character.ndb.battle_results += "X"
                    if totalframes >= max(invuln):
                        for i in range(max(invuln), totalframes):
                            character.ndb.battle_results += "W"

            if self.db.first_to_act:
                pass
            else:
                pass # self.stop here, but it throws errors. Probably 'mark to stop'


    def _process_action(self, action=None):
        """Take the action that was previously delayed"""

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
        #print(f"[{damage} dealt]")
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
        #self.msg_all(f"{character} {attack_verb} a {weapon_noun} at {target}. {effect_str}")
        #character.ndb.battle_results += self._add_to_key_summary(action)
        knockback = self.calc_knockback(self.get_tilt(target), basedamage, baseknockback, target)
        #print(f"[{knockback}] knockback")
        self.loss_by_tilt(target, knockback)
        return True

    def msg_all(self, msg):
        """Send a message to all players with 'tilt' keys"""
        if self.db.tilt:
            for character in self.db.tilt.keys():
                character.msg(f"|[200|w{msg}|n")

    def loss_by_tilt(self, character, knockback):
        """Determine if character is knocked out, and remove if so."""
        if knockback > character.db.statblock.get("knockback_sustained"):
            self.msg_all(f"{character} has been knocked out!")
            self.remove_character(character)

    def cause_injury(self, character, **kwargs):
        """Set the character.db.injuries flag"""
        location = kwargs.get("location", None)
        severity = kwargs.get("severity", None)

        if not character.db.injuries:
            character.db.injuries = {}

        if location:
            character.db.injuries.update({location: severity})

    def get_tilt(self, character):
        """Return the tilt of the character, or 0"""
        return self.db.tilt.get(character, 0)

    def get_attackers(self, character):
        """Gets the list of characters targeting a character"""
        attackers=[]
        for participant in self.db.tilt.keys():
            if participant.ndb.target == character:
                attackers.append(participant)
        return attackers

    def _get_next_action(self):
        """Remove the next action from the queue and return it"""
        return self.db.actions.pop(0)

    def _keyframes_to_seconds(self, keyframes):
        """Convert keyframes into seconds"""
        return keyframes/60

    def _get_character_total_keyframes(self, character):
        """Gets a character's combat_round_actions keyframe totals (queued, waiting for process)"""
        total = 0
        if character.ndb.combat_round_actions:
            for action in character.ndb.combat_round_actions:
                total += action.get("totalframes", 60)
        return total

    def _get_character_queued_keyframes(self, character):
        """Nothing here"""
        pass

    def _get_keyframes(self, action):
        """Returns the keyframes in an action"""
        return action.get("totalframes", 60)

    def _deal_tilt_damage(self, character, target, damage):
        """Updates the tilt database to deal damage"""
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
        """Unused sigma func"""
        tilt = self.get_tilt(character)
        import math
        return 1/(1+math.exp(tilt/100-0.22314))*90+5

    def _calc_damage_modifiers(self, basedamage, freshness):
        """Unused, will calculate freshness and other mods"""
        return basedamage

    def calc_knockback(self, p, d, b, character):
        """Determines the amount of knockback caused by an attack"""
        w = 100
        s = 1.0
        r = 1
        return ((((((p/10)+((p*d)/20))*w*1.4)+18)*s)+b)*r

    def _calc_interrupts(self, *args):
        args = list(args)
        for idx, participant in enumerate(args):
            for i in range(0, len(participant)):
                if participant[i] in ['S']:
                    for other_participant in args:
                        if other_participant[i] in ["X"]:
                            for j in range(i, len(other_participant)):
                                k_count = 0
                                if j not in ["D", "W"]:
                                    swap = list(args[idx])
                                    swap[j] = "I"
                                    # Count how many W's to follow, then half.
                                    for k in range(j, len(swap)):
                                        try:
                                            if swap[k+2] in ["W"]:
                                                if swap[k+1] in ["W"]:
                                                    del swap[k]
                                                    del swap[k+1]
                                                    swap.append("DD")
                                        except IndexError:
                                            pass
                                    if swap[j+1] not in ["D", "W"]:
                                        continue
                                    else:
                                        args[idx] = ''.join(swap)
                                        break
        return args

    def _add_to_key_summary(self, action):
        """returns ||||HAYMAKER|||| text """
        totalframes = action.get("totalframes")
        return f"$pad({action.get('key')},{totalframes},c,|[553|=k||)|n"

    def show_battle_summary(self):
        """Msgs all characters a round summary"""
        for character in self.db.tilt:
            header_str = f"|[200|w|/"\
            "]]]]]]]]]]]]]]]]]]]]]   D O G   F I G H T  ]]]|/" \
            "     ]]]]]]]]]]]]]]]]]]]]]  R E S U L T S  ]]]|/"

            char_str = "|[000|305|/"\
            f"YOU:|-{character.ndb.battle_results}" \
            "|/"

            targ_str = "|[000|135"\
            f"THEM:|-{character.ndb.target.ndb.battle_results}" \
            "|/"

            footer_str = f"|[110|w|/"\
            "]]]]]    A   L U L L   I N   C O M B A T   ]]]|/"

            character.msg(f"{header_str}{char_str}{targ_str}{footer_str}")