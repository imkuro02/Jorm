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
        from custom.npcs import _utils
        _utils.greet_message(
            self = self, 
            message = f'{self.id} moo\'s at you',
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
        self.trigger_manager.trigger_add(trigger_key = 'command_flee', trigger_action = self.trigger_flee)

    def trigger_flee(self, player, line):
        player.send_line('you cannot flee now!')
        return True

    def tick(self):
        if self.room == None:
            return
        if self.status != ActorStatusType.FIGHTING:
            #self.pretty_broadcast('',f'{self.id} moo\'s away', list_pretty_name_objects = [self])
            self.unload()
        else:
            super().tick()

