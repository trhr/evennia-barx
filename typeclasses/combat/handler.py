from typeclasses.scripts import DefaultScript

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

    def at_start(self):
        self.db.tilt = 0
        self.db.wills = {}
        self.db.actions = []

    def add_character(self, character):
        character.ndb.tilt_handler = self
        self.db.wills.update({character : character.db.will})
        return True

    def queue_action(self, character, target, **kwargs):
        """
        Args:
            character
            action_type
            target
        """
        existing_actions = self.db.actions

        action_dict = { 
                "character" : character,
                "target" : target,
                }

        action_dict.update(kwargs)

        existing_actions.append(action_dict)

        if len(self.db.actions) > len(existing_actions):
            return True
        else:
            return False


    def process_action(self, action):
        pass


    def get_current_tilt(self):
        return self.db.tilt

    def is_combat_over(self, characters=[]):
        for character in characters:
            pass
