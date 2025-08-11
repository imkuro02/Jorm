import uuid
from configuration.config import ItemType, ITEMS
import random
from utils import get_object_parent
class Item:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.premade_id = None
        self.item_type = ItemType.MISC
        self.name = 'Name of item'
        self.description = 'Description here'
        self.description_room = None
        self.stack = 1
        self.stack_max = 100
        self.keep = False
        self.inventory_manager = None # the inventory manager of this item
        self.new = True # show if item is newly added to inv
        self.time_on_ground = 0
        self.ticks_until_ambience = 100

        # scenery stuff
        self.can_pick_up = True
        # if invisible is true, then the room wont display it in the list of items on ground
        # but if description_room is anything but false, that will still be displayed
        self.invisible = False 

        # crafting
        self.crafting_recipe_ingredients = []
        self.crafting_ingredient_for = []

    def tick(self):
        if self.ambience == None:
            return

        self.ticks_until_ambience -= 1

        if self.ticks_until_ambience <= 0:
            self.ticks_until_ambience = random.randint(30*60,30*120)

            owner = self.inventory_manager.owner
            if get_object_parent(owner) == 'Room':
                owner = owner
            else:
                owner = owner.room

            if len(owner.actors) >= 1:
                
                ac = random.choice(list(owner.actors.values()))
                ac.simple_broadcast(self.ambience, self.ambience, sound = self.ambience_sfx)
    
    def pretty_name(self, rank_only = False):
        def get_article(word): # chatGPT
            vowels = "aeiou"
            if word == "":
                return "a"  # fallback
            if word[0].lower() in vowels:
                return "an"
            if 'the ' in word.lower():
                return ''
            return "a"

        #output = f'@white{get_article(self.name)} {self.name}@normal'
        output = f'@white{self.name}@normal'
        if rank_only:
            if self.item_type == ItemType.EQUIPMENT:  
                if self.rank != 0: 
                    if self.rank > 0:
                        output = output + f' (@green+{self.rank}@normal)'
                    else:
                        output = output + f' (@red{self.rank}@normal)'
                return output
                
        if self.item_type == ItemType.EQUIPMENT:     
            if self.rank != 0: 
                if self.rank > 0:
                    output = output + f' (@green+{self.rank}@normal)'
                else:
                    output = output + f' (@red{self.rank}@normal)'
            if self.equiped:   output = output + f' (@greenE@normal)'
            if self.keep:      output = output + f' (@redK@normal)'
            if self.new:       output = output + f' (@yellowN@normal)'
        else:
            if self.stack != 1: output = output + f' x{self.stack}'
            if self.keep:      output = output + f' (@redK@normal)'
            if self.new:       output = output + f' (@yellowN@normal)'

        return output
       
    def to_dict(self):
        my_dict = {
            'id': self.id,
            'premade_id': self.premade_id,
            'item_type': self.item_type,
            'name': self.name,
            'description': self.description,
            'keep': self.keep
        }
        return my_dict

    # function used to save to db
    def save(self):
        my_dict = {
            'premade_id': self.premade_id,
            'id': self.id,
            'item_type': self.item_type,
            'name': self.name,
            'description': self.description,
            'keep': self.keep,
        }
        return my_dict

    def identify(self, identifier = None):
        output = f'{self.pretty_name()}\n'
        output += f'@cyan{self.description}@normal\n'
        
        
        if self.crafting_ingredient_for != []:
            output += '\n'
            output += f'Ingredient for: '
            for i in self.crafting_ingredient_for:
                output = output + ITEMS[i]['name'] + ', '

            output = output[:-2]
            output += '\n'

        if self.crafting_recipe_ingredients != []:
            output += f'Recipes: \n'
            for recipe in self.crafting_recipe_ingredients:
                for ingredient in recipe:
                    output += f"{recipe[ingredient]} {ITEMS[ingredient]['name']}, "
                output = output[:-2] + '\n'
                #output = output + str(recipe) + '\n'
            #output = output[:-2]
            output += '\n'

        
            
        
        self.new = False
        return output

    def use(self, user, target):
        if user != target:
            user.simple_broadcast(
                f'You rub {self.pretty_name()} on {target.pretty_name()}... Nothing happens.',
                f'{user.pretty_name()} rubs {self.pretty_name()} on {target.pretty_name()}... Nothing happens.'
            )
        else:
            user.simple_broadcast(
                f'You rub {self.pretty_name()} on yourself... Nothing happens.',
                f'{user.pretty_name()} rubs {self.pretty_name()} on themselves... Nothing happens.'
            )
        return False

    # called at start of turn
    def set_turn(self):
        pass

    # called at end of turn
    def finish_turn(self):
        pass

    # called whenever hp updates in any way
    def take_damage_before_calc(self, damage_obj):
        return damage_obj

    def take_damage_after_calc(self, damage_obj):
        return damage_obj
    
    def deal_damage(self, damage_obj):
        return damage_obj
    
    def dealt_damage(self, damage_obj):
        #if self.stack >= 10:
        #    self.inventory_manager.owner.simple_broadcast(f'You are carrying so much of {self.name} it deals extra damage!','')
        return damage_obj
    
    # called when exp is gained
    def gain_exp(self, exp):
        return exp