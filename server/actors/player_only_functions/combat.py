import systems.utils
from actors.player_only_functions.checks import (
    check_alive,
    check_no_unfriendlies_present_in_room,
    check_not_in_combat,
    check_not_in_party_or_is_party_leader,
    check_your_turn,
)
from configuration.config import SKILLS

from skills.manager import get_skills, construct_skill

from configuration.constants.actor_status_type import ActorStatusType
from configuration.constants.audio import Audio
from configuration.constants.stat_type import StatType
from configuration.constants.color import Color

@check_your_turn
@check_alive
def command_fight(self, line):
    if self.room.combat != None:
        self.send_line("There is already a fight here!")
        return

    if self.status == ActorStatusType.FIGHTING:
        self.send_line(
            'You are already fighting! you can "flee" or "pass" or "use <skill>"'
        )
        # if self.ai.predict_use_best_skill(offensive_only = True, for_prediction = False) == False:
        #   self.command_pass_turn(line = '')
        # self.ai.tick()
        return
    else:
        self.finish_turn()

    if self.party_manager.party == None:
        self.room.join_combat(self)
    else:
        if self.party_manager.party.actor == self:
            self.room.join_combat(self)
        else:
            self.send_line("You are not the party leader")

    # self.ai.clear_prediction()


@check_alive
@check_your_turn
def command_pass_turn(self, line):
    if self.room.combat == None:
        self.finish_turn(force_cooldown=True)
        return
    if self.status != ActorStatusType.FIGHTING:
        self.finish_turn(force_cooldown=True)
        return
    if self.room.combat.current_actor != self:
        return
    self.simple_broadcast(
        "You pass your turn", f"{self.pretty_name()} passes their turn."
    )
    self.finish_turn()


"""
@check_no_empty_line
#@check_your_turn
@check_alive
#@check_not_in_combat
def command_use_try(self, line):
    self.command_use(line, is_trying=True)



def command_use_item(self, line, silent = False):
    pass

def command_use_skill(self, line, silent = False):
    _line = line
    id_to_name, name_to_id = get_skills()

    action = None
    target = None

    dict_of_actors = {}
    for i in self.room.actors:
        dict_of_actors[self.room.actors[i].name] = i

    _action = None
    _target = None

    line = line.split(' ')

    action_name = None

    for i in range(0,len(line)):
        best_match, best_score = systems.utils.match_word(
            ' '.join(line[0:i+1]), name_to_id.keys(), get_score=True
        )

        #print('skill:', line[0:i+1], 'found:', best_match, 'score:', best_score)
        if best_score >=89:
            _action = name_to_id[best_match]
            action_name = best_match
            break

    if action_name == None:
        return False
    if line[0][0].lower() != action_name[0].lower():
        return False

    for i in range(0,len(line)):
        #' '.join(line[len(line)-i:len(line)]), dict_of_actors, get_score=True
        if ' '.join(line[len(line)-i:len(line)]).strip() == '':
            continue


        best_match, best_score = systems.utils.match_word(
            ' '.join(line[len(line)-i:len(line)]), dict_of_actors.keys(), get_score=True
        )

        #print('target:', ' '.join(line[len(line)-i:len(line)]), 'found:', best_match, 'score:', best_score)
        if best_score >=89:
            _target = systems.utils.get_match(best_match, self.room.actors)
            break

    if _action == None:
        if silent:
            return False
        self.send_line(f'Use what?   - "{line}"')
        return False

    if _target == None:
        #if silent:
        #    return False

        if bool(SKILLS[_action]['is_offensive']):
            for i in self.room.actors.values():
                if i.party_manager.get_party_id() != self.party_manager.get_party_id():
                    _target = i
        else:
            if bool(SKILLS[_action]['target_self_is_valid']):
                _target = self


    if _target == None:
        if silent:
            return False
        self.send_line(f'Use {action_name} on who?')
        return False


    self.ai.prediction_skill = _action
    self.ai.prediction_target = _target


    #systems.utils.debug_print([i for i in self.queued_lines if not i.strip().startswith('try')])
    if self.room.combat == None:
        if self.ai.use_prediction():
            # clear all try commands
            self.queued_lines = [i for i in self.queued_lines if not i.strip().startswith('try')]

        self.ai.clear_prediction()
        return True

    if self.room.combat.current_actor == self:
        if self.ai.use_prediction():
            # clear all try commands
            self.queued_lines = [i for i in self.queued_lines if not i.strip().startswith('try')]

        self.ai.clear_prediction()
        return True

    self.ai.clear_prediction()
    return True


def use2(self, line, silent = False):
    line = line.lower()
    dict_of_actors = {}
    skill_id_to_name, skill_name_to_id = get_skills()

    item_name_to_id = {}
    item_id_to_name = {}
    for item in self.inventory_manager.items.keys():
        item_name_to_id[self.inventory_manager.items[item].name] = item
    for item in self.inventory_manager.items.keys():
        item_id_to_name[item] = self.inventory_manager.items[item].name

    for i in self.room.actors:
        dict_of_actors[self.room.actors[i].name] = i

    _action = None
    _target = None

    line = line.split(' ')

    action_name = None

    most_likely_action = ''
    most_likely_action_score = 0

    for i in range(0,len(line)):
        # get action as item
        best_match, best_score = systems.utils.match_word(
            ' '.join(line[0:i+1]), item_name_to_id.keys(), get_score=True
        )

        if best_score >=80:
            _action = self.inventory_manager.items[item_name_to_id[best_match]]
            action_name = best_match
            break

        if most_likely_action_score <= best_score:
            most_likely_action = best_match
            most_likely_action_score = best_score

        #get action as skill
        best_match, best_score = systems.utils.match_word(
            ' '.join(line[0:i+1]), skill_name_to_id.keys(), get_score=True
        )

        if best_score >=80:
            _action = skill_name_to_id[best_match]
            action_name = best_match
            break

        if most_likely_action_score <= best_score:
            most_likely_action = best_match
            most_likely_action_score = best_score


    if action_name == None:
        if not silent:
            self.send_line(f'Couldnt find skill or item to use, did you mean to use "{most_likely_action}"? ({most_likely_action_score}% sure)')
        return False
    if line[0][0].lower() != action_name[0].lower():
        if not silent:
            self.send_line(f'Couldnt find skill or item to use, did you mean to use "{most_likely_action}"? ({most_likely_action_score}% sure)')
        return False

    line = ' '.join(line).replace(best_match.lower(), '', 1).strip().split(' ')
    line.insert(0,'IDK_AND_IDC!!')

    for i in range(0,len(line)):
        if ' '.join(line[len(line)-i:len(line)]).strip() == '':
            continue

        # get target as item
        best_match, best_score = systems.utils.match_word(
            ' '.join(line[0:i+1]), item_name_to_id.keys(), get_score=True
        )

        if best_score >= 80:
            _target = self.inventory_manager.items[item_name_to_id[best_match]]
            break

        # get target as actor
        best_match, best_score = systems.utils.match_word(
            ' '.join(line[len(line)-i:len(line)]), dict_of_actors.keys(), get_score=True
        )

        if best_score >=80:
            _target = systems.utils.get_match(best_match, self.room.actors)
            break

    if len(line) <= 2:
        if _action == None:
            if silent:
                return False
            self.send_line(f'Use what?   - "{line}"')
            return False

        if _target == None:
            if _action in skill_id_to_name:
                if bool(SKILLS[_action]['is_offensive']):
                    for i in self.room.actors.values():
                        if i.party_manager.get_party_id() != self.party_manager.get_party_id():
                            _target = i
                else:
                    if bool(SKILLS[_action]['target_self_is_valid']):
                        _target = self
            else:
                _target = self


    if _target == None:
        if silent:
            return False
        self.send_line(f'Use {action_name} on?')
        return False



    self.ai.clear_prediction()

    if _action in self.skill_manager.skills:
        self.ai.prediction_skill = _action
    else:
        self.ai.prediction_item = _action

    self.ai.prediction_target = _target


    #systems.utils.debug_print([i for i in self.queued_lines if not i.strip().startswith('try')])
    if self.room.combat == None:
        self.ai.use_prediction()
        self.ai.clear_prediction()
        return True

    if self.room.combat.current_actor == self:
        self.ai.use_prediction()
        self.ai.clear_prediction()
        return True

    self.ai.clear_prediction()
    return True
"""

@check_alive
#@check_your_turn
def use(self, line, silent=False):
    
    line = line.lower()
    dict_of_actors = {}
    skill_id_to_name, skill_name_to_id = get_skills()

    item_name_to_id = {}
    item_id_to_name = {}
    for item in self.inventory_manager.items.keys():
        item_name_to_id[self.inventory_manager.items[item].name] = item
    for item in self.inventory_manager.items.keys():
        item_id_to_name[item] = self.inventory_manager.items[item].name

    for i in self.room.actors:
        dict_of_actors[self.room.actors[i].name] = i

    _action = None
    _target = None

    line = line.split(" ")

    action_name = None

    most_likely_action = ""
    most_likely_action_score = 0

    list_of_skill_names = [skill for skill in skill_name_to_id.keys()]
    skills_dict = {}

    class FakeSkill:
        def __init__(self, name):
            self.name = name

        def pretty_name(self):
            return self.name

    for skill in list_of_skill_names:
        skills_dict[skill] = FakeSkill(skill)

    found_action_with = ""
    for i in range(0, len(line)):
        best_match = systems.utils.get_match(
            #" ".join(line[0 : i + 1]), {**skills_dict, **self.inventory_manager.items}
            " ".join(line[0 : i + 1]), skills_dict
        )
        if best_match == None:
            continue
        action_name = best_match.name
        found_action_with = " ".join(line[0 : i + 1])
        _action = best_match

    if action_name == None:
        if not silent:
            #self.send_line("Could not find skill to use")
            self.send_line("Could not find item or skill to use")
        return False
    # if line[0][0].lower() != action_name[0].lower():
    #    if not silent: self.send_line('Could not find item or skill to use')
    #    return False

    line = " ".join(line).replace(found_action_with, "", 1).strip().split(" ")
    line.insert(0, "IDK_AND_IDC!!")

    for i in range(0, len(line)):
        if " ".join(line[len(line) - i : len(line)]).strip() == "":
            continue

        _l_bozo = line[-i:]  # ' '.join(line[len(line)-i:len(line)])
        best_match = systems.utils.get_match(
            #" ".join(_l_bozo), {**self.room.actors, **self.inventory_manager.items}
            #" ".join(_l_bozo), self.room.actors
            " ".join(_l_bozo), {**self.room.actors, **self.inventory_manager.items, **self.room.inventory_manager.items}
        )
        if best_match == None:
            continue
        # action_name = best_match.name
        _target = best_match


    if len(line) <= 1:
        if _action == None:
            if silent:
                return False
            self.send_line(f'Use what?   - "{line}"')
            return False

    if self.ai.target != None:
        if self.ai.target.id not in {**self.room.actors, **self.inventory_manager.items, **self.room.inventory_manager.items}:
            self.ai.target = None
    '''
    # old code that defaults target to yourself, not needed
    if _target == None and self.ai.target == None:
        if _action.name in skill_name_to_id:
            if bool(SKILLS[skill_name_to_id[_action.name]]["is_offensive"]):
                for i in self.room.actors.values():
                    if (
                        i.party_manager.get_party_id()
                        != self.party_manager.get_party_id()
                    ):
                        _target = i
            else:
                if bool(SKILLS[skill_name_to_id[_action.name]]["target_self_is_valid"]):
                    _target = self
        else:
            _target = self

    
    if _target == None and self.ai.target == None:
        _target = self

    '''
    if self.ai.target != None and _target == None:
        _target = self.ai.target

    #if _target == None:
    #    if silent:
    #        return False
    #    self.send_line(f"Use {action_name} on?")
    #    return True

    #systems.utils.debug_print(_target.id)

    self.ai.clear_prediction()

    if _action.name in skill_name_to_id:
        self.ai.prediction = construct_skill(skill_name_to_id[_action.name])(skill_id = skill_name_to_id[_action.name], user = self)
        self.ai.prediction.other = _target
        self.ai.prediction.evaluate()

    if self.status == ActorStatusType.NORMAL:
        self.ai.use_prediction()
        self.ai.clear_prediction()
        return True

    if self.room.combat == None:
        self.ai.use_prediction()
        self.ai.clear_prediction()
        return True

    if self.room.combat.current_actor != self:
        self.send_line(f'{Color.IMPORTANT}Your action will be executed on your turn{Color.NORMAL}')
        #self.ai.use_prediction()
        #self.ai.clear_prediction()
        return True

    #self.ai.clear_prediction()
    return True

def command_use(self, line, silent=False):
    return use(self, line, silent=False)

def command_target(self, line, slinet = False):
    if line == '':
        self.ai.target = None
        self.send_line('Target unset')
        return None

    tar = self.get_actor(line)
    if tar != None:
        self.ai.target = tar
        self.send_line(f'Target set to {tar.pretty_name(self)}')
        return tar

    tar = self.get_item(line, search_mode = "self_and_room")
    if tar != None:
        tar = tar[0]
        self.ai.target = tar
        self.send_line(f'Target set to {tar.pretty_name(self)}')
        return tar

    self.ai.target = None
    self.send_line('Target unset')
    return None
"""
def command_use(self, line, is_trying = False):
    _line = line
    is_trying = True

    if line.endswith((' on', ' at')):
        self.send_line('Use on who?')
        return False

    id_to_name, name_to_id = get_skills()
    list_of_skill_names = [skill for skill in name_to_id.keys()]
    #list_of_items = [systems.utils.remove_color(item.name) for item in self.inventory_manager.items.values() if item.item_type == ItemType.CONSUMABLE]
    list_of_items = [systems.utils.remove_color(item.name) for item in self.inventory_manager.items.values()]
    whole_list = list_of_items + list_of_skill_names
    list_of_actors = [actor.name for actor in self.room.actors.values()]

    action = None
    target = None

    skills_dict = {}

    class FakeSkill:
        def __init__(self, name):
            self.name = name

        def pretty_name(self):
            return self.name

    for skill in list_of_skill_names:
        skills_dict[skill] = FakeSkill(skill)

    # target yourself if not trying to target anything else
    if ' on ' not in line and ' at ' not in line:
        action = line
        action = systems.utils.get_match(action, {**skills_dict, **self.inventory_manager.items})
        target = self

    # if you are targetting something else set target to that
    else:
        action, target = line.replace(' on ',' | ').replace(' at ',' | ').split(' | ')
        action = systems.utils.get_match(action, {**skills_dict, **self.inventory_manager.items})
        target = systems.utils.get_match(target, {**self.room.actors, **self.inventory_manager.items})

    #self.send_line(action.name)

    _action = None
    _target = None

    _action = action
    if isinstance(target, str):
        if target in list_of_items:
            _target = target #self.get_item(target)
        if target in list_of_actors:
            _target = self.get_actor(target)
    else:
        _target = target

    if _action == None:
        self.send_line(f'Use what?   - "{line}"')
        return False

    if _target == None:
        self.send_line(f'On who?     - "{line}"')
        return False


    self.ai.prediction_target = None
    self.ai.prediction_skill = None
    self.ai.prediction_item = None

    self.ai.prediction_target = _target

    if _action in skills_dict.values():
        self.ai.prediction_skill = name_to_id[_action.name]
    if _action in self.inventory_manager.items.values():
        self.ai.prediction_item = _action

    if not is_trying:
        if self.room.combat != None:
            if self.room.combat.current_actor != self:
                self.send_line('> Use command queued! <')
                return True

    #systems.utils.debug_print([i for i in self.queued_lines if not i.strip().startswith('try')])
    if self.room.combat == None:
        if self.ai.use_prediction():
            # clear all try commands
            self.queued_lines = [i for i in self.queued_lines if not i.strip().startswith('try')]

        self.ai.clear_prediction()
        return True

    if self.room.combat.current_actor == self:
        if self.ai.use_prediction():
            # clear all try commands
            self.queued_lines = [i for i in self.queued_lines if not i.strip().startswith('try')]

        self.ai.clear_prediction()
        return True

    self.ai.clear_prediction()
    return True
"""


def rest_set(self, line):
    if not self.room.can_be_recall_site:
        self.send_line("@redThis is not a suitable rest spot.@normal")
        return
    self.recall_site = self.room.id
    self.send_line(f"@green{self.room.name} is now your rest spot.@normal")


@check_alive
def rest_here(self, line):
    self.sendSound(Audio.BUFF)

    self.simple_broadcast(f"You rest", f"{self.pretty_name()} rests")

    self.stat_manager.stats[StatType.HP] = int(self.stat_manager.stats[StatType.HPMAX])
    # self.stat_manager.stats[StatType.MP] = int(self.stat_manager.stats[StatType.MPMAX])
    self.stat_manager.stats[StatType.PHYARMOR] = int(
        self.stat_manager.stats[StatType.PHYARMORMAX]
    )
    self.stat_manager.stats[StatType.MAGARMOR] = int(
        self.stat_manager.stats[StatType.MAGARMORMAX]
    )
    self.affect_manager.unload_all_affects(forced=False)
    self.cooldown_manager.unload_all_cooldowns()
    # self.new_room_look()
    self.finish_turn()


@check_not_in_party_or_is_party_leader
def rest_home_request(self, line):
    if self.party_manager.party != None:
        for par in self.party_manager.party.participants.values():
            if par == self:
                continue
            par.rest_home(line)
    self.rest_home(line)


@check_not_in_party_or_is_party_leader
@check_no_unfriendlies_present_in_room
def rest_here_request(self, line):
    if self.party_manager.party != None:
        for par in self.party_manager.party.participants.values():
            if par == self:
                continue
            par.rest_here(line)
    self.rest_here(line)


def rest_home(self, line):
    self.sendSound(Audio.BUFF)
    if self.status == ActorStatusType.DEAD:
        self.status = ActorStatusType.NORMAL


        self.stat_manager.stats[StatType.HP] = int(
            1
        )
        self.stat_manager.stats[StatType.PHYARMOR] = int(
           1
        )
        self.stat_manager.stats[StatType.MAGARMOR] = int(
            1
        )
        '''
        self.stat_manager.stats[StatType.HP] = int(
            self.stat_manager.stats[StatType.HPMAX]
        )
        # self.stat_manager.stats[StatType.MP] = int(self.stat_manager.stats[StatType.MPMAX])
        self.stat_manager.stats[StatType.PHYARMOR] = int(
            self.stat_manager.stats[StatType.PHYARMORMAX]
        )
        self.stat_manager.stats[StatType.MAGARMOR] = int(
            self.stat_manager.stats[StatType.MAGARMORMAX]
        )
        '''

        self.affect_manager.unload_all_affects()
        self.cooldown_manager.unload_all_cooldowns()
        self.simple_broadcast(None, f"{self.pretty_name()} ressurects")

        # tp home
        if self.recall_site not in self.protocol.factory.world.rooms:
            self.recall_site = "tutorial"

        if self.party_manager.party == None:
            rest_site = self.recall_site
        else:
            rest_site = self.party_manager.party.actor.recall_site
        self.protocol.factory.world.rooms[rest_site].move_actor(self, silent=True)

        self.new_room_look()
        self.simple_broadcast("You ressurect", f"{self.pretty_name()} has ressurected")
    else:
        if self.room.id == self.recall_site:
            self.simple_broadcast(f"You rest", f"{self.pretty_name()} rests")
        else:
            self.simple_broadcast(None, f"{self.pretty_name()} returns back to rest")

            # tp home
            if self.recall_site not in self.protocol.factory.world.rooms:
                self.recall_site = "tutorial"

            if self.party_manager.party == None:
                rest_site = self.recall_site
            else:
                rest_site = self.party_manager.party.actor.recall_site
            self.protocol.factory.world.rooms[rest_site].move_actor(self, silent=True)

            self.new_room_look()
            self.simple_broadcast(
                "You returned to rest", f"{self.pretty_name()} has returned to rest"
            )

    '''
    self.stat_manager.stats[StatType.HP] = int(self.stat_manager.stats[StatType.HPMAX])
    # self.stat_manager.stats[StatType.MP] = int(self.stat_manager.stats[StatType.MPMAX])
    self.stat_manager.stats[StatType.PHYARMOR] = int(
        self.stat_manager.stats[StatType.PHYARMORMAX]
    )
    self.stat_manager.stats[StatType.MAGARMOR] = int(
        self.stat_manager.stats[StatType.MAGARMORMAX]
    )
    self.affect_manager.unload_all_affects()
    self.cooldown_manager.unload_all_cooldowns()
    '''
    self.finish_turn()

    self.status = ActorStatusType.NORMAL



@check_not_in_combat
def command_rest(self, line):
    line = "home"
    if line == "":
        if self.recall_site not in self.room.world.rooms:
            self.recall_site = "home"

        output = ""
        output += f"Your resting spot is {self.room.world.rooms[self.recall_site].pretty_name()}"
        if self.status == ActorStatusType.DEAD:
            output += f'\nYou need to use "rest home" to ressurect'
        self.send_line(output)
        return

    if line.lower() in "set":
        self.rest_set(line)
        return

    if line.lower() in "now" or line.lower() in "here":
        self.rest_here_request(line)
        return

    if line.lower() in "home":
        self.rest_home_request(line)
        return


def command_party(self, line):
    self.party_manager.handle_party_message(line)
