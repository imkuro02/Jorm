
from items.misc import Item
from configuration.config import StatType, ActorStatusType, DamageType
from items.manager import load_item
from combat.damage_event import Damage
from combat.combat_event import CombatEvent

class food_item_class(Item):
    @classmethod
    def compare_replace(self, item_object):
        return False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_drink = False
        self.can_eat = True
        self.can_read = False

        self.item_to_leave_after_consumed = None
        self.on_consume_remove_stacks_amount = 1

        self.trigger_manager.trigger_add('eat', self.trigger_consume)
        self.trigger_manager.trigger_add('drink', self.trigger_consume)
        self.trigger_manager.trigger_add('read', self.trigger_consume)
        
        self.description += f'\n{self.name} is consumable.'
        self.heal_value = 10

    def trigger_consume(self, player, line):
        if len(line.split())<=1:
            return False

        old_line = line
        items = player.get_item(line = line.replace('eat','').replace('drink','').replace('read','').strip(), search_mode='self')
        
        if items == None:
            return False
        
        if self == items[0]:
            attempting_var = 'can_'+old_line.split()[0]
            attempting = old_line.split()[0]
            if not getattr(self, attempting_var):
                player.sendLine(f'You can\'t {attempting} {self.name}') 
                return True
            
            if player.status == ActorStatusType.DEAD:
                player.sendLine(f'You can\'t {attempting} {self.name} right now')
                return True

            self.new = False
            player.simple_broadcast(f'You {attempting} the {self.name}', f'{player.pretty_name()} {attempting}s the {self.name}')

            cb = CombatEvent()
            damage_obj_hp = Damage(
                damage_taker_actor=player,
                damage_source_actor=player,
                damage_source_action=self,
                combat_event=cb,
                damage_value=self.heal_value,
                damage_type=DamageType.HEALING,
                damage_to_stat=StatType.HP,
            )

            damage_obj_pa = Damage(
                damage_taker_actor=player,
                damage_source_actor=player,
                damage_source_action=self,
                combat_event=cb,
                damage_value=self.heal_value,
                damage_type=DamageType.HEALING,
                damage_to_stat=StatType.PHYARMOR,
                silent = True,
            )

            damage_obj_ma = Damage(
                damage_taker_actor=player,
                damage_source_actor=player,
                damage_source_action=self,
                combat_event=cb,
                damage_value=self.heal_value,
                damage_type=DamageType.HEALING,
                damage_to_stat=StatType.MAGARMOR,
                silent = True,
            )

            cb.run()

            if self.on_consume_remove_stacks_amount != 0:
                player.inventory_manager.remove_item(self, 1)
            
            if player.stat_manager.stats[StatType.HP] >= player.stat_manager.stats[StatType.HPMAX]:
                player.sendLine(f'You are beyond full.')

            if self.item_to_leave_after_consumed != None:
                item_to_leave_after_consumed = load_item(self.item_to_leave_after_consumed)
                player.inventory_manager.add_item(item_to_leave_after_consumed)
            return True
        return False


class food_item_cannot_leave_tavern_class(food_item_class):
    @classmethod
    def compare_replace(self, item_object):
        return False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger_manager.trigger_add('command_go', self.trigger_go)
        self.description += f'\n{self.name} cannot be brought out of the tavern.'

    def trigger_go(self, player, line):
        if player.room.__class__.__name__ == 'tavern_room':
            return False

        if self in player.inventory_manager.items.values():
            food_items = []
            for i in self.inventory_manager.items.values():
                food_items.append(i)

            food_thrown_out_yet = False
            for i in food_items:
                if hasattr(i, 'can_leave_tavern'):
                    player.inventory_manager.remove_item(i)
                    if food_thrown_out_yet == False:
                        if i.can_eat:
                            player.sendLine(f'You food goes cold and you throw it away')
                        elif i.can_drink:
                            player.sendLine(f'You drink spills as you leave and you throw it away')
                    food_thrown_out_yet = True
            return False
        
class mug_of_ale(food_item_cannot_leave_tavern_class):
    @classmethod
    def compare_replace(self, item_object):
        if "tavern_food_item_mug_of_ale" != item_object.premade_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_leave_tavern = False
        self.can_drink = True
        self.can_eat = False
        self.item_to_leave_after_consumed = 'mug'

class dinner_0(food_item_cannot_leave_tavern_class):
    @classmethod
    def compare_replace(self, item_object):
        if "tavern_food_item_dinner_0" != item_object.premade_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.heal_value = 30
        self.item_to_leave_after_consumed = 'food_item_empty_plate'
        self.can_leave_tavern = False

class dinner_1(food_item_cannot_leave_tavern_class):
    @classmethod
    def compare_replace(self, item_object):
        if "tavern_food_item_dinner_1" != item_object.premade_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.heal_value = 50
        self.item_to_leave_after_consumed = 'food_item_empty_plate'
        self.can_leave_tavern = False

class dinner_2(food_item_cannot_leave_tavern_class):
    @classmethod
    def compare_replace(self, item_object):
        if "tavern_food_item_dinner_2" != item_object.premade_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.heal_value = 100
        self.item_to_leave_after_consumed = 'food_item_empty_plate'
        self.can_leave_tavern = False

class rat_cheese(food_item_class):
    @classmethod
    def compare_replace(self, item_object):
        if "food_item_cheese" != item_object.premade_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger_manager.trigger_add('command_get', self.trigger_get)
        self.heal_value = 15

    def trigger_get(self, player, line):
        items = player.get_item(line = line.replace('command_get','').strip(), search_mode='room')
        if items == None:
            return False
        
        if self in items:
            for i in self.inventory_manager.owner.room.actors.values():
                if 'rat' == i.npc_id:
                    player.sendLine(f'{i.pretty_name()} hisses at you')
                    return True
        else:
            return False
