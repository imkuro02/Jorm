from actors.npcs import Npc
from configuration.constants.actor_status_type import ActorStatusType

from combat.damage_event import Damage
from configuration.constants.damage_type import DamageType
from configuration.constants.stat_type import StatType

class beetle_tree_guard(Npc):
    @classmethod
    def compare_replace(self, npc_object):
        if "beetle_man" != npc_object.npc_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.west_log = 'overworld/57e8dcb4-4c40-40e1-a7c9-33c261eb3ff3'
        self.east_log = 'overworld/9beade9f-4e7e-4f65-b387-62f5d4e2d2e2'
        self.yeet_room = 'overworld/a2c99cd0-ede4-4b9f-9857-ef099fe81482'

        self.pacified = False

        self.trigger_manager.trigger_add(trigger_key = 'command_go', trigger_action = self.trigger_command_go)

    def set_pacified(self, _bool):
        self.pacified = _bool

    def trigger_command_go(self, player, line):
        line = line.replace('command_go ','')
        _dir = player.find_direction_for_command_go(line)
        if _dir == None:
            return False
        
        if (self.room.id == self.west_log and _dir.direction == 'east') or (self.room.id == self.east_log and _dir.direction == 'west'):
            player.pretty_broadcast(
                f'{self.id} gets angry and wrestles you\nYou tumble into the water below the log\nSPLASH!',
                f'{self.id} gets angry and wrestles {player.id}\{player.id} tumbles into the water below the log\nSPLASH!',
                list_pretty_name_objects=[self, player]
            )
            player.move_party_leader(room_id = self.yeet_room, no_new_room_look = True)
            damage_obj = Damage(
                    damage_taker_actor=player,
                    damage_source_action=self,
                    combat_event=None,
                    damage_source_actor=self,
                    damage_value=1000,
                    damage_type=DamageType.PHYSICAL,
                    damage_to_stat=StatType.PHYARMOR
                )
            damage_obj.run()
            return True

  

