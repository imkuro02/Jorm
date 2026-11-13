import systems.utils
from actors.player_only_functions.checks import (
    check_alive,
    check_not_in_combat,
    check_your_turn,
    check_no_empty_line,
    check_not_trading,
    check_quest_state
)

from custom.utils import CustomDialogQuestionList

from configuration.config import SKILLS
from configuration.constants.audio import Audio
from configuration.constants.stat_type import StatType
from configuration.constants.item_type import ItemType
from configuration.config import (
    ITEMS,
    LORE,
)
import items.manager as items


def command_scrap_dialog_start(self, player, line):
    questions = {
        'reforge':    'What do you want to scrap?',
    }

    options = {}
    reforges = {}
    for item in player.inventory_manager.items.values():
        if not item.can_tinker_with():
            continue
        reforges[item.id] = item.pretty_name()

    if reforges == {}:
        player.send_line('You are lacking items to scrap')
        return

    options = {
        'reforge': reforges.copy(),
        }


    player.current_dialog = CustomDialogQuestionList(player, 
        self, _dialog_tree = None, 
        questions = questions, options = options, 
        question_list_dialog_answers_function = self.command_scrap_dialog_answer
        )

    player.current_dialog.print_dialog()
    return True

def command_scrap_dialog_answer(dialog_obj):
    line = f"{dialog_obj.answers['reforge']}"
    dialog_obj.player.command_scrap(line)

@check_quest_state(quest_id = 'robot_scrap', required_state = 'turned_in')
@check_not_trading
#@check_no_empty_line
@check_not_in_combat
@check_alive
def command_scrap(self, line):
    if line == '':
        setattr(self, 'command_scrap_dialog_answer', command_scrap_dialog_answer)
        setattr(self, 'command_scrap_dialog_start', command_scrap_dialog_start)
        self.command_scrap_dialog_start(self = self, player = self, line = '')
        return

    items_to_get = []

    #if self.inventory_manager.get_amount_of_free_item_slots() == 0:
    #    self.send_line('You need atleast one free inventory slot to scrap items.')
    #    return
    
    for item in self.inventory_manager.items.values():
        items_to_get.append(item)

    item_found = self.get_item(line)
    if line != "all":
        if item_found == None:
            self.send_line("Scrap what?", sound=Audio.ERROR)
            return

    items_to_get = item_found

    items_pretty_name_before_pickup = []
    items_scrapped = []
    for item in items_to_get:
        if item.item_type == ItemType.CURRENCY: 
            self.send_line(
                f"{item.pretty_name(self)} can\'t be scrapped"
            )
            continue

        item_pretty_name_before_pickup = item.pretty_name(self)

        if not item.can_tinker_with():
            self.send_line(
                f"Cannot scrap {item.pretty_name(self)} since its kept or equipped"
            )
            continue

        items_pretty_name_before_pickup.append(item_pretty_name_before_pickup)
        self.inventory_manager.remove_item(item)
        #item.unload()
        scrap = items.load_item("currency_0")
        scrap.stack = item.stack
        if item.item_type == ItemType.EQUIPMENT:
            scrap.stack = item.stack * item.stat_manager.reqs[StatType.LVL]
        self.inventory_manager.add_item(scrap, forced=True)
        items_scrapped.append(item)

    if items_scrapped == []:
        self.send_line('You scrap nothing')
        return

    self.send_line(f"You scrap {', '.join(items_pretty_name_before_pickup)}")
    """
    self.simple_broadcast(
        f"You scrap {', '.join(items_pretty_name_before_pickup)}",
        f"{self.pretty_name(self)} scraps {', '.join(items_pretty_name_before_pickup)}",
    )"""























def command_reforge_dialog_start(self, player, line):
    questions = {
        'reforge':    'What equipment do you want to reforge?',
    }

    options = {}
    reforges = {}
    for item in player.inventory_manager.items.values():
        if item.item_type != ItemType.EQUIPMENT:
            continue
        if not item.can_tinker_with():
            continue
        reforges[item.id] = item.pretty_name()

    if reforges == {}:
        player.send_line('You are lacking items to reforge')
        return

    options = {
        'reforge': reforges.copy(),
        }


    player.current_dialog = CustomDialogQuestionList(player, 
        self, _dialog_tree = None, 
        questions = questions, options = options, 
        question_list_dialog_answers_function = self.command_reforge_dialog_answer
        )

    player.current_dialog.print_dialog()
    return True

def command_reforge_dialog_answer(dialog_obj):
    line = f"{dialog_obj.answers['reforge']}"
    dialog_obj.player.command_reforge(line)

@check_quest_state(quest_id = 'blacksmith_reforge', required_state = 'turned_in')
@check_not_trading
#@check_no_empty_line
@check_not_in_combat
@check_alive
def command_reforge(self, line):
    if line == '':
        setattr(self, 'command_reforge_dialog_answer', command_reforge_dialog_answer)
        setattr(self, 'command_reforge_dialog_start', command_reforge_dialog_start)
        self.command_reforge_dialog_start(self = self, player = self, line = '')
        return

    print('wtf')
    if line == "all":
        self.send_line("WHAT AN AWFUL IDEA!! NO!")
        return

    items_to_get = []

    for item in self.inventory_manager.items.values():
        items_to_get.append(item)

    item_found = self.get_item(line)
    if item_found == None:
        self.send_line("Reforge what?", sound=Audio.ERROR)
        return

    items_to_get = item_found

    items_pretty_name_before_reforge = []
    items_pretty_name_after_reforge = []
    for item in items_to_get:
        if item.item_type != ItemType.EQUIPMENT:
            self.send_line(
                f"Cannot reforge {item.pretty_name(self)} since its not an equipment"
            )
            continue

        item_pretty_name_before_reforge = item.pretty_name(self)

        if not item.can_tinker_with():
            self.send_line(
                f"Cannot reforge {item.pretty_name(self)} since its kept or equipped"
            )
            continue

        items_pretty_name_before_reforge.append(item_pretty_name_before_reforge)
        reforge_cost = 10 * item.stat_manager.reqs[StatType.LVL]
        reforge_currency = "currency_0"

        # self.inventory_manager.remove_item(item = ingredients_to_use[index], stack = list(recipe_to_use.values())[index])
        # self.inventory_manager.remove_item(item)
        # scrap = items.load_item('currency_0')
        # scrap.stack = item.stack
        # if item.item_type == ItemType.EQUIPMENT:
        #    scrap.stack = item.stack * item.stat_manager.reqs[StatType.LVL]
        # self.inventory_manager.add_item(scrap)
        if not self.inventory_manager.remove_items_by_id(
            "currency_0", stack=reforge_cost
        ):
            self.send_line(
                f"You need atleast {reforge_cost} of {ITEMS[reforge_currency]['name']} to reforge this item."
            )
            return

        item = item.reforge()

        items_pretty_name_after_reforge.append(item.pretty_name(self))

    if items_pretty_name_before_reforge == []:
        return

    self.simple_broadcast(
        f"You reforge {', '.join(items_pretty_name_before_reforge)} into {', '.join(items_pretty_name_after_reforge)}, you spent {reforge_cost} {ITEMS[reforge_currency]['name']}",
        f"{self.pretty_name(self)} reforge {', '.join(items_pretty_name_before_reforge)} into {', '.join(items_pretty_name_after_reforge)}, they spent {reforge_cost} {ITEMS[reforge_currency]['name']}",
    )

























def command_brew_dialog_start(self, player, line):
    questions = {
        'brew':    'What brew do you want to use?',
        'herb':    'What herb do you want to use?',
    }

    options = {}
    brews = {}
    for item in player.inventory_manager.items.values():
        if 'custom_potion' != f'{item.premade_id}':
            continue
        brews[item.id] = item.name
    herbs = {}
    for item in player.inventory_manager.items.values():
        if ' custom_potion_ingredient_' not in f' {item.premade_id}_':
            continue
        herbs[item.id] = item.name

    if herbs == {}:
        player.send_line('You are lacking herbs')
        return

    if herbs == {}:
        player.send_line('You are lacking brews')
        return

    options = {
        'brew': brews.copy(),
        'herb': herbs.copy(),
        }


    player.current_dialog = CustomDialogQuestionList(player, 
        self, _dialog_tree = None, 
        questions = questions, options = options, 
        question_list_dialog_answers_function = self.command_brew_dialog_answer
        )

    player.current_dialog.print_dialog()
    return True

def command_brew_dialog_answer(dialog_obj):
    line = f"{dialog_obj.answers['brew']} {dialog_obj.answers['herb']}"
    dialog_obj.player.command_brew(line)

@check_quest_state(quest_id = 'learn_brewing', required_state = 'turned_in')
@check_not_trading
@check_not_in_combat
@check_alive
def command_brew(self, line):
    
    player = self
    #player.send_line(line)
    #player.command_brew_dialog_answer = command_brew_dialog_answer
    if line == '':
        setattr(player, 'command_brew_dialog_answer', command_brew_dialog_answer)
        setattr(player, 'command_brew_dialog_start', command_brew_dialog_start)
        self.command_brew_dialog_start(self = player, player = player, line = '')
        return

    #line = line.replace('mix','')
    _dict = player.inventory_manager.items

    obj_1, obj_2 = systems.utils.get_two_objects_from_line(line, dict_1 = _dict, dict_2 = _dict)

    

    if obj_1 == None or obj_2 == None:
        player.send_line('You need to brew / mix a brew and a herb')
        return False

    if obj_1.premade_id != 'custom_potion' and obj_2.premade_id != 'custom_potion':
        player.send_line('You need to brew / mix a brew and a herb')
        return False
    
    if obj_1.premade_id != 'custom_potion' and obj_2.premade_id == 'custom_potion':
        _obj_a = obj_1
        _obj_b = obj_2
        obj_1 = _obj_b
        obj_2 = _obj_a
    
    mind = player.stat_manager.stats[StatType.MIND]
    soul = player.stat_manager.stats[StatType.SOUL]
    lvl = int((mind+soul)/15) + 1
    if lvl <= int(obj_1.item_properties['herbs_mixed']):
        player.send_line('This brew is too powerful for you to mix further')
        return True

    if type(obj_2).__name__ != 'Consumable':
        player.send_line('You need to brew / mix a brew and a herb')
        return False
    
    if ' custom_potion_ingredient_' not in f' {obj_2.premade_id.lower()}':
        player.send_line('You need to brew / mix a brew and a herb')
        return False

    list_pretty_name_objects = [player, obj_1, obj_2]
    br1 = f'{player.id} mix {obj_2.id} into {obj_1.id}'
    br2 = f'{player.id} mixes {obj_2.id} into {obj_1.id}'
    player.pretty_broadcast(br1,br2,list_pretty_name_objects=list_pretty_name_objects,sound=Audio.DRINK)

    player.inventory_manager.remove_item(obj_2, 1)

    for skill in obj_2.skills.values():
        skill_id = skill['skill_id']
        #skill_lv = skill['skill_lv']
        new = {'skill_id': str(skill_id), 'skill_lv': 0}
        obj_1.skills[skill_id] = obj_1.skills.get(skill_id, new) 
        obj_1.skills[skill_id]['skill_lv'] += skill['skill_lv']#+ 10
        obj_1.item_properties['skills'] = str(obj_1.skills)

    obj_1.item_properties['herbs_mixed'] = str(int(obj_1.item_properties['herbs_mixed']) + 1)
    obj_1.sync_skills()
    return True
