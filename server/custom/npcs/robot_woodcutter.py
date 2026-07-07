from actors.npcs import Npc
from configuration.constants.actor_status_type import ActorStatusType
from configuration.constants.color import Color
from items.misc import Item
class robot_woodcutter(Npc):
    @classmethod
    def compare_replace(self, npc_object):
        if "robot_woodcutter" != npc_object.npc_id:
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wander_directions_order = ['south', 'north']
        self.wander_direction_current = 0
        self.wander_ticks_passed = 0
        self.wander_ticks_required = 30*3
        self.wander_ticks_warning_required = 10
        self.footprints = []
        self.pre_footprints = []
        self.footprints_max = 1

    def despawn_footprints(self):
        for i in self.footprints:
            if i.inventory_manager != None:
                i.inventory_manager.remove_item(i) 
            i.unload()
        self.footprints = []

    def despawn_pre_footprints(self):
        for i in self.pre_footprints:
            if i.inventory_manager != None:
                i.inventory_manager.remove_item(i) 
            i.unload()
        self.pre_footprints = []

    def spawn_footprints(self, dir):
        corpse = Item()
        corpse.name = f'Footprints'
        corpse.description = f'There is a set of tire tracks leading {dir.lower()}, you wonder who they belong to.'
        corpse.description_room = f'{Color.BAD}A pair of tire tracks is leading {dir.lower()}{Color.BACK}'
        corpse.stack_max = 1
        corpse.keep = False
        corpse.can_pick_up = False
        corpse.footprint_leading_dir = dir
        corpse.invisible = True
        corpse.premade_id = 'footprints_something_blabla'
        
        self.room.inventory_manager.add_item(corpse)
        self.footprints.append(corpse)

        list_pretty_name_objects = [self]
        for i in self.room.actors.values():
            br = f'{self.id} {Color.BAD}leaves a trail of tire tracks behind.{Color.BACK}'
            i.pretty_broadcast(br, br, list_pretty_name_objects = list_pretty_name_objects)
            break

        if len(self.footprints)-1>=self.footprints_max:
            if self.footprints[0].inventory_manager == None:
                self.despawn_footprints()
                return

            for i in self.footprints[0].inventory_manager.owner.actors.values():
                list_pretty_name_objects = [self]
                br = f'{Color.BAD}The tire tracks leading {dir} dry up and the trail goes cold.{Color.BACK}'
                i.pretty_broadcast(br, br, list_pretty_name_objects = list_pretty_name_objects)
                break

            self.footprints[0].inventory_manager.remove_item(self.footprints[0])
            self.footprints[0].unload()
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
            self.pre_footprints[0].unload()
            self.pre_footprints.pop(0)


    def wander(self, warning = False):
        #if self.room.is_player_present():
        #    return
        for actor in self.room.actors.values():
            if not actor.party_manager.get_is_friendly(self):
                return

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
        from custom.npcs import _utils
        _utils.greet_message(self, f'{self.id} says "You are in the way"')
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

