from actors.npcs import Npc
from configuration.constants.actor_status_type import ActorStatusType
from configuration.constants.color import Color
from items.misc import Item
from configuration.constants.tickrate import TICKRATE


# EXAMPLE for spawning mobs:
# snail+class=[CustomWanderAroundMob]+wandering_mob_config=[snail_tracks]+wander_directions_order=[north east south west]


wandering_mob_config = {
    'default': {
        'wander_footprint_name':                'Footprints',
        'wander_footprint_description':         'There is a set of footprints leading #DIR#, who do they belong to?',
        'wander_footprint_description_room':    'A pair of footprints is leading #DIR#',
        'wander_footprint_spawn_text':          '#SELF# leaves a trail of footprints behind.',
        'wander_footprint_despawn_text':        'The footprints leading #DIR# dry up and the trail goes cold.',

        'wander_pre_footprint_name':            'Footprints',
        'wander_pre_footprint_description':     'There is something approaching from the #DIR#',
        'wander_pre_footprint_description_room':'There is something approaching from the #DIR#',
        'wander_pre_footprint_spawn_text':      'You hear something approaching from the #DIR#',
        'wander_pre_footprint_despawn_text':    '#SELF# arrives from #DIR#',

        'wander_in_the_way_warning':            None,
    },

    'robot_tracks': {
        'wander_footprint_name':                'Tire tracks',
        'wander_footprint_description':         'There is a set of tire tracks leading #DIR#, who do they belong to?',
        'wander_footprint_description_room':    'A pair of tire tracks are leading #DIR#',
        'wander_footprint_spawn_text':          '#SELF# leaves a trail of tire tracks behind.',
        'wander_footprint_despawn_text':        'The tire tracks leading #DIR# dry up and the trail goes cold.',

        'wander_pre_footprint_name':            'Tire tracks',
        'wander_pre_footprint_description':     'There is something rumbling #DIR#',
        'wander_pre_footprint_description_room':'There is something rumbling #DIR#',
        'wander_pre_footprint_spawn_text':      'You hear something begin to rumble #DIR#',
        'wander_pre_footprint_despawn_text':    '#SELF# drives in from #DIR#',

        'wander_in_the_way_warning':            'Beep boop, out of my way! #SELF# beeps in a playful tune',
    },

    'snail_tracks': {
        'wander_footprint_name':                'Trail of slime',
        'wander_footprint_description':         'There is a trail of slime leading #DIR#, what do they belong to?',
        'wander_footprint_description_room':    'A trail of slime is leading #DIR#',
        'wander_footprint_spawn_text':          '#SELF# leaves a trail of slime behind.',
        'wander_footprint_despawn_text':        'The slime trail leading #DIR# dry up and the trail goes cold.',

        'wander_pre_footprint_name':            'Trail of slime',
        'wander_pre_footprint_description':     'There is something rumbling #DIR#',
        'wander_pre_footprint_description_room':'There is something rumbling #DIR#',
        'wander_pre_footprint_spawn_text':      'You hear something begin to rumble #DIR#',
        'wander_pre_footprint_despawn_text':    '#SELF# creeps in from #DIR#',

        'wander_in_the_way_warning':            None,
    }
}
class CustomWanderAroundMob(Npc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wander_directions_order = ['north', 'east', 'south', 'west']
        self.name = self.name.replace('The','The Wandering')
        self.wander_direction_current = 0
        self.wander_ticks_passed = 0
        self.wander_ticks_required = TICKRATE*10
        self.wander_ticks_warning_required = 10
        self.footprints = []
        self.pre_footprints = []
        self.footprints_max = 1

        # _npcs rat+class=[CustomWanderAroundMob]+wander_directions_order=[north south]
        if 'wander_directions_order' in self.npc_properties:
            self.wander_directions_order = self.npc_properties['wander_directions_order'][0].split()

        self.wander_footprint_name =                'Footprints'
        self.wander_footprint_description =         'There is a set of footprints leading #DIR#, who do they belong to?'
        self.wander_footprint_description_room =    'A pair of footprints is leading #DIR#'
        self.wander_footprint_spawn_text =          '#SELF# leaves a trail of footprints behind.'
        self.wander_footprint_despawn_text =        'The footprints leading #DIR# dry up and the trail goes cold.'
        
        self.wander_pre_footprint_name =            'Footprints'
        self.wander_pre_footprint_description =     'There is something approaching from the #DIR#'
        self.wander_pre_footprint_description_room ='There is something approaching from the #DIR#'
        self.wander_pre_footprint_spawn_text =      'You hear something approaching from the #DIR#'
        self.wander_pre_footprint_despawn_text =    '#SELF# arrives from #DIR#'
        
        self.wander_in_the_way_warning =            None

        wander_properties = [
            'wander_footprint_name',
            'wander_footprint_description',
            'wander_footprint_description_room',
            'wander_footprint_spawn_text',
            'wander_footprint_despawn_text',
            'wander_pre_footprint_name',
            'wander_pre_footprint_description',
            'wander_pre_footprint_description_room',
            'wander_pre_footprint_spawn_text',
            'wander_pre_footprint_despawn_text',
            'wander_in_the_way_warning',
        ]

        # _npcs rat+class=[CustomWanderAroundMob]+wandering_mob_config=[robot_tracks]
        if 'wandering_mob_config' in self.npc_properties:
            if self.npc_properties['wandering_mob_config'][0] in wandering_mob_config:
                for key in wandering_mob_config[self.npc_properties['wandering_mob_config'][0]]:
                    setattr(self, key, wandering_mob_config[self.npc_properties['wandering_mob_config'][0]][key])

        for key in wander_properties:
            if key in self.npc_properties:
                setattr(self, key, self.npc_properties[key][0])
        


    def trigger_dont_leave(self, player, line):
        if player.status == ActorStatusType.DEAD:
            return False

        player.send_line(f'You cannot do that while {self.pretty_name(identifier = player)} is here')
        return True

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
        foot = Item()
        foot.name =              self.wander_footprint_name
        foot.description =       self.wander_footprint_description.replace('#DIR#',dir.lower()).replace('#SELF#',self.id)
        foot.description_room =  self.wander_footprint_description_room.replace('#DIR#',dir.lower()).replace('#SELF#',self.id)
        foot.stack_max = 1
        foot.keep = False
        foot.can_pick_up = False
        foot.footprint_leading_dir = dir
        foot.invisible = True
        foot.premade_id = 'footprints_something_blabla'
        
        self.room.inventory_manager.add_item(foot)
        self.footprints.append(foot)

        for i in self.room.actors.values():
            list_pretty_name_objects = [self]
            br = f'{self.id} {Color.BAD}leaves a trail of footprints behind.{Color.BACK}'
            i.pretty_broadcast(br,br, list_pretty_name_objects = list_pretty_name_objects)
            break

        if len(self.footprints)-1>=self.footprints_max:
            if self.footprints[0].inventory_manager == None:
                self.despawn_footprints()
                return

            for i in self.footprints[0].inventory_manager.owner.actors.values():
                br = self.wander_footprint_despawn_text.replace('#DIR#',dir.lower()).replace('#SELF#',self.id)
                i.simple_broadcast(br,br)
                break

            self.footprints[0].inventory_manager.remove_item(self.footprints[0])
            self.footprints[0].unload()
            self.footprints.pop(0)


        self.despawn_pre_footprints()
        for i in self.footprints[0].inventory_manager.owner.actors.values():
            br = self.wander_pre_footprint_despawn_text.replace('#DIR#',dir.lower()).replace('#SELF#',self.id)
            i.simple_broadcast(br,br)
            break
        
        

    def spawn_pre_footprints(self, _exit):
        try:
            corpse = Item()
            corpse.name = _exit.direction
            corpse.description = self.wander_pre_footprint_description.replace('#DIR#',_exit.direction).replace('#SELF#',self.id)
            corpse.description_room = self.wander_pre_footprint_description_room.replace('#DIR#',_exit.direction).replace('#SELF#',self.id)
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
        except Exception as e:
            from systems.utils import debug_print
            debug_print(e)
            print(e)


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
                        br = self.wander_pre_footprint_spawn_text.replace('#DIR#', i.direction).replace('#SELF#', self.id)
                        ac.simple_broadcast(br,br)
                        break
                    self.spawn_pre_footprints(i)
            else:
                self.spawn_footprints(self.wander_directions_order[self.wander_direction_current])
                
                self.room.world.rooms[exits[self.wander_directions_order[self.wander_direction_current]]].move_actor(self, silent = True)
                for i in self.room.exits:
                    if i.to_room_id != self.room_previous:
                        continue
                    br = self.wander_pre_footprint_despawn_text.replace('#SELF#', self.id).replace('#DIR#', i.direction)
                    self.pretty_broadcast(br,br, list_pretty_name_objects = [self])
        else:
            if not warning:
                self.wander_direction_current += 1
                if self.wander_direction_current >= len(self.wander_directions_order):
                    self.wander_direction_current = 0
                    
    def tick(self):
        super().tick()

        if self.wander_in_the_way_warning:
            from scripts.greet_message import greet_message
            greet_message(self, self.wander_in_the_way_warning.replace('#SELF#', self.id))

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

from actors.npcs import Npc
from configuration.constants.actor_status_type import ActorStatusType
from configuration.constants.color import Color
from items.misc import Item
