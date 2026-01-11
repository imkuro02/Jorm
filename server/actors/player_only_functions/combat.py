from actors.player_only_functions.checks import check_no_unfriendlies_present_in_room, check_not_in_party_or_is_party_leader, check_alive, check_no_empty_line, check_no_empty_line, check_your_turn, check_not_in_combat
from configuration.config import DamageType, ItemType, ActorStatusType, StatType, Audio, SKILLS
import utils
from skills.manager import get_skills, use_skill
from affects import affects
'''
def command_target(self, line):
    list_of_actors = [actor.name for actor in self.room.actors.values()]
    list_of_items = [utils.remove_color(item.name) for item in self.inventory_manager.items.values()]
    target = utils.get_match(line, {**self.room.actors, **self.inventory_manager.items})

    if line in 'c none clear 0 stop noone'.split():
        self.ai.target = None
        self.sendLine('Target cleared')
        return

    if line == '':
        if self.ai.target != None:
            self.sendLine(f'Target is: {self.ai.target.pretty_name()}')
        else:
            self.sendLine(f'You have no target')
        return

    if target == None:
        self.sendLine('Target unclear!')
        return

    self.ai.target = target
    self.sendLine(f'Targetting: {self.ai.target.pretty_name()}')
'''

@check_your_turn
@check_alive
def command_fight(self, line):
    if self.room.combat != None:
        self.sendLine('There is already a fight here!')
        return
        
    if self.status == ActorStatusType.FIGHTING:
        self.sendLine('You are already fighting! you can "flee" or "pass" or "use <skill>"')
        #if self.ai.predict_use_best_skill(offensive_only = True, for_prediction = False) == False:
        #   self.command_pass_turn(line = '')
        #self.ai.tick()
        return
    else:
        self.finish_turn()

    if self.party_manager.party == None:
        self.room.join_combat(self)
    else:
        if self.party_manager.party.actor == self:
            self.room.join_combat(self)
        else:
            self.sendLine('You are not the party leader')

    #self.ai.clear_prediction()



@check_alive
def command_pass_turn(self, line):
    if self.room.combat == None:
        self.finish_turn(force_cooldown = True)
        return
    if self.status != ActorStatusType.FIGHTING:
        self.finish_turn(force_cooldown = True)
        return
    if self.room.combat.current_actor != self:
        return
    self.simple_broadcast(
        'You pass your turn',
        f'{self.pretty_name()} passes their turn.'
    )
    self.finish_turn()

@check_no_empty_line
#@check_your_turn
@check_alive
#@check_not_in_combat
def command_use_try(self, line):
    self.command_use(line, is_trying=True)


def command_use(self, line, silent = False):
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
        best_match, best_score = utils.match_word(
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

        
        best_match, best_score = utils.match_word(
            ' '.join(line[len(line)-i:len(line)]), dict_of_actors.keys(), get_score=True
        )

        #print('target:', ' '.join(line[len(line)-i:len(line)]), 'found:', best_match, 'score:', best_score)
        if best_score >=89:
            _target = utils.get_match(best_match, self.room.actors)
            break

    if _action == None:
        if silent: 
            return False
        self.sendLine(f'Use what?   - "{line}"')
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
        self.sendLine(f'Use {action_name} on who?')
        return False


    self.ai.prediction_skill = _action
    self.ai.prediction_target = _target


    #utils.debug_print([i for i in self.queued_lines if not i.strip().startswith('try')])
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

'''
def command_use(self, line, is_trying = False):
    _line = line
    is_trying = True

    if line.endswith((' on', ' at')):
        self.sendLine('Use on who?')
        return False

    id_to_name, name_to_id = get_skills()
    list_of_skill_names = [skill for skill in name_to_id.keys()]
    #list_of_items = [utils.remove_color(item.name) for item in self.inventory_manager.items.values() if item.item_type == ItemType.CONSUMABLE]
    list_of_items = [utils.remove_color(item.name) for item in self.inventory_manager.items.values()]
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
        action = utils.get_match(action, {**skills_dict, **self.inventory_manager.items})
        target = self

    # if you are targetting something else set target to that
    else:
        action, target = line.replace(' on ',' | ').replace(' at ',' | ').split(' | ')
        action = utils.get_match(action, {**skills_dict, **self.inventory_manager.items})
        target = utils.get_match(target, {**self.room.actors, **self.inventory_manager.items})

    #self.sendLine(action.name)

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
        self.sendLine(f'Use what?   - "{line}"')
        return False

    if _target == None:
        self.sendLine(f'On who?     - "{line}"')
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
                self.sendLine('> Use command queued! <')
                return True

    #utils.debug_print([i for i in self.queued_lines if not i.strip().startswith('try')])
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
'''

def rest_set(self, line):
    if not self.room.can_be_recall_site:
        self.sendLine('@redThis is not a suitable rest spot.@normal')
        return
    self.recall_site = self.room.id
    self.sendLine(f'@green{self.room.name} is now your rest spot.@normal')

@check_alive
def rest_here(self, line):
    self.sendSound(Audio.BUFF)

    self.simple_broadcast(
        f'You rest',
        f'{self.pretty_name()} rests'
        )

    self.stat_manager.stats[StatType.HP] = int(self.stat_manager.stats[StatType.HPMAX])
    #self.stat_manager.stats[StatType.MP] = int(self.stat_manager.stats[StatType.MPMAX])
    self.stat_manager.stats[StatType.PHYARMOR] = int(self.stat_manager.stats[StatType.PHYARMORMAX])
    self.stat_manager.stats[StatType.MAGARMOR] = int(self.stat_manager.stats[StatType.MAGARMORMAX])
    self.affect_manager.unload_all_affects(forced = False)
    self.cooldown_manager.unload_all_cooldowns()
    #self.new_room_look()
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
        self.stat_manager.stats[StatType.HP] = int(self.stat_manager.stats[StatType.HPMAX])
        #self.stat_manager.stats[StatType.MP] = int(self.stat_manager.stats[StatType.MPMAX])
        self.stat_manager.stats[StatType.PHYARMOR] = int(self.stat_manager.stats[StatType.PHYARMORMAX])
        self.stat_manager.stats[StatType.MAGARMOR] = int(self.stat_manager.stats[StatType.MAGARMORMAX])

        self.simple_broadcast(
            None,
            f'{self.pretty_name()} ressurects')

        #tp home
        if self.recall_site not in self.protocol.factory.world.rooms:
            self.recall_site = 'tutorial'

        if self.party_manager.party == None:
            rest_site = self.recall_site
        else:
            rest_site = self.party_manager.party.actor.recall_site
        self.protocol.factory.world.rooms[rest_site].move_actor(self, silent = True)

        self.new_room_look()
        self.simple_broadcast(
            'You ressurect',
            f'{self.pretty_name()} has ressurected')
    else:

        if self.room.id == self.recall_site:
            self.simple_broadcast(
                f'You rest',
                f'{self.pretty_name()} rests'
                )
        else:

            self.simple_broadcast(
                None,
                f'{self.pretty_name()} returns back to rest'
                )

            #tp home
            if self.recall_site not in self.protocol.factory.world.rooms:
                self.recall_site = 'tutorial'

            if self.party_manager.party == None:
                rest_site = self.recall_site
            else:
                rest_site = self.party_manager.party.actor.recall_site
            self.protocol.factory.world.rooms[rest_site].move_actor(self, silent = True)

            self.new_room_look()
            self.simple_broadcast(
                'You returned to rest',
                f'{self.pretty_name()} has returned to rest'
                )


    self.stat_manager.stats[StatType.HP] = int(self.stat_manager.stats[StatType.HPMAX])
    #self.stat_manager.stats[StatType.MP] = int(self.stat_manager.stats[StatType.MPMAX])
    self.stat_manager.stats[StatType.PHYARMOR] = int(self.stat_manager.stats[StatType.PHYARMORMAX])
    self.stat_manager.stats[StatType.MAGARMOR] = int(self.stat_manager.stats[StatType.MAGARMORMAX])
    self.affect_manager.unload_all_affects()
    self.cooldown_manager.unload_all_cooldowns()
    self.finish_turn()

    '''
    well_rested = affects.AffectWellRested(
        affect_source_actor = self,
        affect_target_actor = self,
        name = 'Rested', description = f'You take half damage round 1',
        turns = 0 + int(self.stat_manager.stats[StatType.LVL] * 15),
        custom_go_away = True
    )
    self.affect_manager.set_affect_object(well_rested)
    '''


@check_not_in_combat
def command_rest(self, line):
    line = 'home'
    if line == '':
        if self.recall_site not in self.room.world.rooms:
            self.recall_site = 'home'

        output = ''
        output += f'Your resting spot is {self.room.world.rooms[self.recall_site].pretty_name()}'
        if self.status == ActorStatusType.DEAD:
            output += f'\nYou need to use "rest home" to ressurect'
        self.sendLine(output)
        return

    if line.lower() in 'set':
        self.rest_set(line)
        return

    if line.lower() in 'now' or line.lower() in 'here':
        self.rest_here_request(line)
        return

    if line.lower() in 'home':
        self.rest_home_request(line)
        return



def command_party(self, line):
    self.party_manager.handle_party_message(line)
