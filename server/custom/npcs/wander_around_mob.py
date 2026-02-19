from actors.npcs import Npc
from configuration.config import ActorStatusType
from items.misc import Item
from configuration.config import Color
class wander_around_mob(Npc):
    @classmethod
    def compare_replace(self, npc_object):
        if "overworld/c6a0418c-71e1-41f5-8779-bfe88a2db798" != npc_object.room.id:
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wander_directions_order = ['north', 'east', 'south', 'west']
        self.wander_direction_current = 0
        self.wander_ticks_passed = 0
        self.wander_ticks_required = 30*10
        self.wander_ticks_warning_required = 10
        self.footprints = []
        self.pre_footprints = []
        self.footprints_max = 1

        self.trigger_manager.trigger_add(trigger_key = 'command_go', trigger_action = self.trigger_dont_leave)
        self.trigger_manager.trigger_add(trigger_key = 'command_rest', trigger_action = self.trigger_dont_leave)

    def trigger_dont_leave(self, player, line):
        if player.status == ActorStatusType.DEAD:
            return False

        player.send_line(f'You cannot do that while {self.pretty_name()} is here')
        return False

    def despawn_footprints(self):
        for i in self.footprints:
            i.inventory_manager.remove_item(i) 
        self.footprints = []

    def despawn_pre_footprints(self):
        for i in self.pre_footprints:
            i.inventory_manager.remove_item(i) 
        self.pre_footprints = []

    def spawn_footprints(self, dir):
        corpse = Item()
        corpse.name = f'Footprints'
        corpse.description = f'There is a set of footprints leading {dir.lower()}, you wonder who they belong to.'
        corpse.description_room = f'{Color.BAD}A pair of footprints is leading {dir.lower()}{Color.BACK}'
        corpse.stack_max = 1
        corpse.keep = False
        corpse.can_pick_up = False
        corpse.footprint_leading_dir = dir
        corpse.invisible = True
        corpse.premade_id = 'footprints_something_blabla'
        
        self.room.inventory_manager.add_item(corpse)
        self.footprints.append(corpse)

        for i in self.room.actors.values():
            br = f'{self.pretty_name()} {Color.BAD}leaves a trail of footprints behind.{Color.BACK}'
            i.simple_broadcast(br,br)
            break

        if len(self.footprints)-1>=self.footprints_max:
            for i in self.footprints[0].inventory_manager.owner.actors.values():
                br = f'{Color.BAD}The footprints leading {dir} dry up and the trail goes cold.{Color.BACK}'
                i.simple_broadcast(br,br)
                break
                
            self.footprints[0].inventory_manager.remove_item(self.footprints[0])
            self.footprints.pop(0)

        self.despawn_pre_footprints()
        
        

    def spawn_pre_footprints(self, _exit):
        corpse = Item()
        corpse.name = _exit.direction
        corpse.description = f'{Color.BAD}There is something approaching from {_exit.direction}{Color.BACK}'
        corpse.description_room = f'{Color.BAD}There is something approaching from {_exit.direction}{Color.BACK}'
        corpse.stack_max = 1
        corpse.keep = False
        corpse.can_pick_up = False
        corpse.footprint_leading_dir = _exit.direction
        corpse.invisible = True
        corpse.premade_id = 'footprints_something_blabla1'
        
        _exit.room.inventory_manager.add_item(corpse)
        self.pre_footprints.append(corpse)

        if len(self.pre_footprints)-1>=1:
            self.pre_footprints[0].inventory_manager.remove_item(self.pre_footprints[0])
            self.pre_footprints.pop(0)


    def wander(self, warning = False):
        _exits = self.room.exits
        exits = {}
        for i in _exits:
            exits[i.direction] = i.to_room_id 
        if self.wander_directions_order[self.wander_direction_current] in exits:
            
            if warning:
                for i in self.room.world.rooms[exits[self.wander_directions_order[self.wander_direction_current]]].exits:
                    if i.to_room_id != self.room.id:
                        continue
                    for ac in self.room.world.rooms[exits[self.wander_directions_order[self.wander_direction_current]]].actors.values():
                        br = f'{Color.BAD}You can hear something approaching from {i.direction}.{Color.BACK}'
                        ac.simple_broadcast(br,br)
                        break
                    self.spawn_pre_footprints(i)
            else:
                self.spawn_footprints(self.wander_directions_order[self.wander_direction_current])
                
                self.room.world.rooms[exits[self.wander_directions_order[self.wander_direction_current]]].move_actor(self)
        else:
            if not warning:
                self.wander_direction_current += 1
                if self.wander_direction_current >= len(self.wander_directions_order):
                    self.wander_direction_current = 0
                    
    def tick(self):
        super().tick()
        self.wander_ticks_passed += 1
        if self.wander_ticks_passed == self.wander_ticks_warning_required:
            self.wander(warning = True)
        if self.wander_ticks_passed == self.wander_ticks_required:
            self.wander(warning = False)
            self.wander_ticks_passed = 0

    def die(self):
        self.despawn_footprints()
        self.despawn_pre_footprints()
        super().die()

    def unload(self):
        self.despawn_footprints()
        self.despawn_pre_footprints()
        super().unload()

