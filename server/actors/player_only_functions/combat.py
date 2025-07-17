from actors.player_only_functions.checks import check_not_in_party_or_is_party_leader, check_alive, check_no_empty_line, check_no_empty_line, check_your_turn, check_not_in_combat
from configuration.config import DamageType, ItemType, ActorStatusType, StatType, Audio
import utils
from skills.manager import get_skills, use_skill


@check_your_turn
@check_alive

def command_fight(self, line):
    #error_output = self.room.new_combat()
    #if isinstance(error_output, str):
    #    self.sendLine(error_output)

    
    

    if self.status == ActorStatusType.FIGHTING:
        self.ai.tick()
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
@check_your_turn
@check_alive
#@check_not_in_combat
def command_use(self, line):
    _line = line

    if line.endswith((' on', ' at')):
        self.sendLine('Use on who?')
        return

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
    for skill in list_of_skill_names:
        skills_dict[skill] = FakeSkill(skill)

    # target yourself if not trying to target anything else
    if ' on ' not in line and ' at ' not in line:
        action = line
        action = utils.get_match(action, {**self.inventory_manager.items, **skills_dict})
        target = self

    # if you are targetting something else set target to that
    else:
        action, target = line.replace(' on ',' | ').replace(' at ',' | ').split(' | ')
        action = utils.get_match(action, {**self.inventory_manager.items, **skills_dict})
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
        self.sendLine('Use what?')
        return

    if _target == None:
        self.sendLine('On who?')
        return


    if _action in skills_dict.values():
        if use_skill(self, _target, name_to_id[_action.name]):
            self.finish_turn()
            return

    if _action in self.inventory_manager.items.values():
        if _action.use(self, _target):
            self.finish_turn()
            return

'''
def command_recall_set(self, line):
    self.recall_site = self.room.id
    self.sendLine(self.recall_site)

def command_recall_go(self, line):
    rooms = self.room.world.rooms
    if self.recall_site not in rooms:
        self.sendLine('recall site broked')
        return

    rooms[self.recall_site].move_actor(self)
'''

def rest_set(self, line):
    if not self.room.can_be_recall_site:
        self.sendLine('@redThis is not a suitable rest spot.@normal')
        return
    self.recall_site = self.room.id
    self.sendLine(f'@green{self.room.name} is now your rest spot.@normal')

@check_not_in_party_or_is_party_leader
def rest_now_request(self, line):
    if self.party_manager.party != None:
        for par in self.party_manager.party.participants.values():
            if par == self:
                continue
            par.rest_now(line)
    self.rest_now(line)

def rest_now(self, line):
    self.sendSound(Audio.BUFF)
    self.finish_turn()
    
    if self.status == ActorStatusType.DEAD:
        self.status = ActorStatusType.NORMAL

        self.stat_manager.stats[StatType.HP] = int(self.stat_manager.stats[StatType.HPMAX]*0.3)
        self.stat_manager.stats[StatType.MP] = int(self.stat_manager.stats[StatType.MPMAX]*0.3)

        self.simple_broadcast(
            'You ressurect',
            f'{self.pretty_name()} ressurects')

        #tp home
        if self.recall_site not in self.protocol.factory.world.rooms:
            self.recall_site = 'tutorial'

        if self.party_manager.party == None:
            rest_site = self.recall_site
        else:
            rest_site = self.party_manager.party.actor.recall_site
        self.protocol.factory.world.rooms[rest_site].move_actor(self, silent = True)

        self.simple_broadcast(
            None,
            f'{self.pretty_name()} has ressurected')
    else:

        if self.room.id == self.recall_site:
            self.simple_broadcast(
                f'You rest',
                f'{self.pretty_name()} rests'
                )
        else:
            self.simple_broadcast(
                f'You return to rest',
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

            self.simple_broadcast(
                None,
                f'{self.pretty_name()} has returned to rest'
                )
                
    if self.stat_manager.stats[StatType.HP] <= self.stat_manager.stats[StatType.HPMAX]*0.3:
        self.stat_manager.stats[StatType.HP] = int(self.stat_manager.stats[StatType.HPMAX]*0.3)
    if self.stat_manager.stats[StatType.MP] <= self.stat_manager.stats[StatType.MPMAX]*0.3:
        self.stat_manager.stats[StatType.MP] = int(self.stat_manager.stats[StatType.MPMAX]*0.3)
    self.affect_manager.unload_all_affects()

@check_not_in_combat
def command_rest(self, line):
    if line == '':
        if self.recall_site not in self.room.world.rooms:
            self.recall_site = 'home'

        self.sendLine(f'Your resting spot is {self.room.world.rooms[self.recall_site].name}')
        return

    if line.lower() in 'set':
        self.rest_set(line)
        return

    if line.lower() in 'now':
        self.rest_now_request(line)
        return

def command_party(self, line):
    self.party_manager.handle_party_message(line)
            