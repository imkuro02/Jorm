from actors.npcs import Npc
from configuration.constants.actor_status_type import ActorStatusType

class rat(Npc):
    @classmethod
    def compare_replace(self, npc_object):
        if "rat" != npc_object.npc_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
        self.trigger_manager.trigger_add(trigger_key = 'pet', trigger_action = self.trigger_pet)
        self.description += '\nYou can "pet" the rat'


    #    self.trigger_manager.trigger_add(trigger_key = 'command_go', trigger_action = self.trigger_command_go)

    #def trigger_command_go(self, player, line):
    #    line = line.replace('command_go ','')
    #    _dir = player.find_direction_for_command_go(line)
    #    _l = f'{player.name} {line}... {_dir.__dict__}'
    #    self.simple_broadcast(_l,_l)

    def trigger_pet(self, player, line):
        line = line.replace('pet','')
        if not line:
            return False

        if player.get_actor(line) != self:
            return False

        list_pretty_name_objects = [player, self]

        if self.status != ActorStatusType.NORMAL:
            player.pretty_broadcast(
                f'{player.id} try to pet {self.id} but they are busy skittering about!',
                f'{player.id} tries to pet {self.id} but they are busy skittering about!',
                list_pretty_name_objects = list_pretty_name_objects
            )
            return True

        player.pretty_broadcast(
            f'{player.id} pet {self.id}',
            f'{player.id} pets {self.id} ',
            list_pretty_name_objects = list_pretty_name_objects
        )

        self.skill_manager.learn('bite')
        self.ai.prediction_skill = 'bite'
        self.ai.prediction_target = player
        self.ai.use_prediction(no_checks=True)
        self.skill_manager.unlearn('bite')
        self.ai.clear_prediction
        return True

