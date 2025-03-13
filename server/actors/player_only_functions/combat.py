from actors.player_only_functions.checks import check_alive, check_no_empty_line, check_no_empty_line, check_your_turn, check_not_in_combat
from configuration.config import DamageType, ItemType, ActorStatusType, StatType
import utils
from skills.manager import get_skills, use_skill

@check_your_turn
@check_alive
def command_fight(self, line):
    #error_output = self.room.new_combat()
    #if isinstance(error_output, str):
    #    self.sendLine(error_output)

    if self.status == ActorStatusType.FIGHTING:
        action = self.ai.get_best_skill()
        if action != None:
            use_skill(self, action[1], action[0])
            self.finish_turn()
        return
    
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
    list_of_items = [utils.remove_color(item.name) for item in self.inventory_manager.items.values() if item.item_type == ItemType.CONSUMABLE]
    #list_of_items = [utils.remove_color(item.name) for item in self.inventory_manager.items.values()]
    whole_list = list_of_items + list_of_skill_names
    list_of_actors = [actor.name for actor in self.room.actors.values()]

    action = None
    target = None

    # target yourself if not trying to target anything else
    if ' on ' not in line and ' at ' not in line:
        action = line
        action = utils.match_word(action, list_of_items + list_of_skill_names)
        target = self

    # if you are targetting something else set target to that
    else:
        action, target = line.replace(' on ',' | ').replace(' at ',' | ').split(' | ')
        action = utils.match_word(action, list_of_items + list_of_skill_names)
        #target = utils.match_word(target, list_of_items + list_of_actors)


    _action = None
    _target = None

    if action in list_of_items:
        _action = self.get_item(action)
    if action in list_of_skill_names:
        _action = name_to_id[action]

    if isinstance(target, str): 
        #if target in list_of_items:
        #    _target = self.get_item(target)
        
        _target = self.get_actor(target)
    else:
        _target = target

    if _action == None:
        self.sendLine('Use what?')
        return

    if _target == None:
        self.sendLine('On who?')
        return

    if action in list_of_skill_names:
        if use_skill(self, _target, _action):
            self.finish_turn()
            return

    if action in list_of_items:
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

@check_not_in_combat
def command_rest(self, line):
    if line == '':
        if self.recall_site not in self.room.world.rooms:
            self.recall_site = 'home'

        self.sendLine(f'Your resting spot is {self.room.world.rooms[self.recall_site].name}')
        return

    if line.lower() in 'set':
        if not self.room.can_be_recall_site:
            self.sendLine('@redThis is not a suitable rest spot.@normal')
            return
        self.recall_site = self.room.id
        self.sendLine(f'@green{self.room.name} is now your rest spot.@normal')
        return

    if line.lower() in 'now':
        if self.status == ActorStatusType.DEAD:
            self.status = ActorStatusType.NORMAL

            self.stat_manager.stats[StatType.HP] = self.stat_manager.stats[StatType.HPMAX]
            self.stat_manager.stats[StatType.MP] = self.stat_manager.stats[StatType.MPMAX]

            self.simple_broadcast(
                'You ressurect',
                f'{self.pretty_name()} ressurects')

            #tp home
            if self.recall_site not in self.protocol.factory.world.rooms:
                self.recall_site = 'tutorial'
            self.protocol.factory.world.rooms[self.recall_site].move_actor(self)

            self.simple_broadcast(
                None,
                f'{self.pretty_name()} has ressurected')
        else:

            self.stat_manager.stats[StatType.HP] = self.stat_manager.stats[StatType.HPMAX]
            self.stat_manager.stats[StatType.MP] = self.stat_manager.stats[StatType.MPMAX]

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
                self.protocol.factory.world.rooms[self.recall_site].move_actor(self)

                self.simple_broadcast(
                    None,
                    f'{self.pretty_name()} has returned to rest'
                    )
        self.affect_manager.unload_all_affects()
        return

def command_party(self, line):
    self.party_manager.handle_party_message(line)
            