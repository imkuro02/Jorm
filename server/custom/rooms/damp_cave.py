import random

from actors.npcs import create_npc
from combat.manager import Combat
from configuration.constants.actor_status_type import ActorStatusType
from configuration.constants.stat_type import StatType
from items.manager import load_item
from systems.inventory import InventoryManager
from systems.room import Room
from systems.utils import unload
from configuration.constants.tickrate import TICKRATE
from configuration.constants.damage_type import DamageType
from combat.damage_event import Damage

class damp_cave(Room):
    @classmethod
    def compare_replace(self, room_object):
        # return False
        if "damp cave" not in room_object.name.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def move_actor_after(self, actor):

        damage = True
        has_torch = False

        quest_completed = actor.quest_manager.check_quest_state('damp_cave_fairy_quest') == 'turned_in'

        if damage and actor.room_previous == None:
            damage = False
        if damage and actor.room_previous not in actor.room.world.rooms:
            damage = False
        if damage and type(actor.room.world.rooms[actor.room_previous]) != type(self):
            damage = False
        if actor.inventory_manager.get_item_by_premade_id('torch'):
            damage = False
            has_torch = True

        if quest_completed:
            br = f'Small fairies circle you in joy, glowing up your path'
            actor.pretty_broadcast(br,None,list_pretty_name_objects=[actor])
        else:

            if not has_torch:
                br = f'{actor.id} can\'t see without a torch!'
                actor.pretty_broadcast(br,br,list_pretty_name_objects=[actor])
            else:
                br = f'{actor.id} use a torch to keep the darkness away.'
                actor.pretty_broadcast(br,None,list_pretty_name_objects=[actor])

        if damage and not quest_completed:
            damage_obj = Damage(
                damage_taker_actor= actor,
                damage_source_actor= actor,
                damage_source_action= self,
                damage_value=10,
                damage_type=DamageType.PURE,
                add_threat=False,
                silent=False,
                dont_proc=True,
            )
            damage_obj.run()


        
            



        
