from actors.npcs import Enemy
from configuration.config import ActorStatusType

class rat(Enemy):
    @classmethod
    def compare_replace(self, npc_object):
        if "rat" != npc_object.npc_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
        self.trigger_manager.trigger_add(trigger_key = 'pet', trigger_action = self.trigger_pet)
        self.description += '\nYou can "pet" the rat'

    def trigger_pet(self, player, line):
        line = line.replace('pet','')
        if not line:
            return False

        if player.get_actor(line) != self:
            return False

        if self.status != ActorStatusType.NORMAL:
            player.simple_broadcast(
                f'You try to pet {self.pretty_name()} but they are busy skittering about!',
                f'{player.pretty_name()} tries to pet {self.pretty_name()} but they are busy skittering about!',
            )
            return True

        player.simple_broadcast(
            f'You pet {self.pretty_name()}',
            f'{player.pretty_name()} pets {self.pretty_name()} ',
        )
        self.skill_manager.learn('bite')
        self.ai.prediction_skill = 'bite'
        self.ai.prediction_target = player
        self.ai.use_prediction(no_checks=True)
        self.skill_manager.unlearn('bite')
        self.ai.clear_prediction
        return True

