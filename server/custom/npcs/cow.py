from actors.npcs import Npc, create_npc
from configuration.constants.actor_status_type import ActorStatusType

class cow(Npc):
    @classmethod
    def compare_replace(self, npc_object):
        if "mini_boss_cow" != npc_object.npc_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger_manager.trigger_add(trigger_key = 'milk', trigger_action = self.trigger_milk)
        self.description += '\nYou can "milk" the cow'

    def tick(self):
        super().tick()
        if self.status != ActorStatusType.NORMAL:
            return

        if self.factory.ticks_passed % (30 * 4) == 0:
            if not hasattr(self,'actors_in_room_count'):
                self.actors_in_room_count = 0
            if self.actors_in_room_count != len(self.room.actors.values()):
                self.actors_in_room_count = len(self.room.actors.values())
                self.simple_broadcast(
                    "", f'{self.pretty_name()} Moo\'s at you'
                )

    def set_turn(self):
        if self.room.combat == None:
            return

        for i in self.room.combat.participants.values():
            if i.npc_id == 'mini_boss_bull':
                return

        self.simple_broadcast('The cow calms down...','The cow calms down...')
        self.status = ActorStatusType.NORMAL
    def trigger_milk(self, player, line):
        line = line.replace('milk','')
        if not line:
            return False

        if player.get_actor(line) != self:
            return False

        if self.status != ActorStatusType.NORMAL:
            player.simple_broadcast(
                f'You try to milk {self.pretty_name()} but they are busy mooing about!',
                f'{player.pretty_name()} tries to pet {self.pretty_name()} but they are busy mooing about!',
            )
            return True

        player.simple_broadcast(
            f'You milk {self.pretty_name()}, you soon come to regret this decision',
            f'{player.pretty_name()} milks {self.pretty_name()}, they soon come to regret this decision',
        )

        e = create_npc(self.room, 'mini_boss_bull')
        e.pretty_broadcast('A raging bull charges at you!','A raging bull charges at you!')
        _pl = player
        if _pl.party_manager.party != None:
            _pl = _pl.party_manager.party.leader
        _pl.command_fight('')
        
        return True


class bull(Npc):
    @classmethod
    def compare_replace(self, npc_object):
        if "mini_boss_bull" != npc_object.npc_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_join_fights = False
        self.trigger_manager.trigger_add(trigger_key = 'command_flee', trigger_action = self.trigger_flee)
        self.description += '\nYou can "milk" the cow'

    def trigger_flee(self, player, line):
        player.send_line('you cannot flee now!')
        return True

