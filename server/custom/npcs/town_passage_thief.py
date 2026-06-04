from actors.npcs import Npc
from configuration.constants.actor_status_type import ActorStatusType

from combat.damage_event import Damage
from configuration.constants.damage_type import DamageType
from configuration.constants.stat_type import StatType

class town_passage_thief(Npc):
    @classmethod
    def compare_replace(self, npc_object):
        if npc_object.room.id != 'overworld/c8783b2d-0b8f-49b8-8375-7fd72d7a5ec1':
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.outside_of_lavoratory = 'overworld/c8783b2d-0b8f-49b8-8375-7fd72d7a5ec1'


        self.trigger_manager.trigger_add(trigger_key = 'command_go', trigger_action = self.trigger_command_go)

        self.anger_levels = {}


    def anger_raise(self, player):
        if player in self.anger_levels:
            self.anger_levels[player] += 1
        else:
            self.anger_levels[player] = 1

        if self.anger_levels[player] >= 4:
            player.pretty_broadcast(
                f'{self.id} punches you in the stomach',
                f'{self.id} punches {player.id} in the stomach',
                list_pretty_name_objects=[self, player]
            )
            damage_obj = Damage(
                    damage_taker_actor=player,
                    damage_source_action=self,
                    combat_event=None,
                    damage_source_actor=self,
                    damage_value=100,
                    damage_type=DamageType.PHYSICAL,
                    damage_to_stat=StatType.PHYARMOR
                )
            damage_obj.run()
            player.command_fight('')
            return True
        else:
            player.pretty_broadcast(
                f'{self.id} stands in your way, looking annoyed. "There is a line here, {player.id}"',
                f'{self.id} stands in {player.id}s way, looking annoyed. "There is a line here, {player.id}"',
                list_pretty_name_objects=[self, player]
            )
            return True

    def trigger_command_go(self, player, line):
        line = line.replace('command_go ','')
        _dir = player.find_direction_for_command_go(line)
        if _dir == None:
            return False
        
        if (self.room.id == self.outside_of_lavoratory and _dir.direction == 'east'):
            return self.anger_raise(player)

            

  

