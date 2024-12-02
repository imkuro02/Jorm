from actors.player_only_functions.checks import check_alive, check_no_empty_line, check_no_empty_line, check_your_turn, check_not_in_combat
from config import DamageType, ItemType, ActorStatusType, StatType
import utils
from skills.manager import get_skills, use_skill

@check_alive
def command_fight(self, line):
    error_output = self.room.new_combat()
    if isinstance(error_output, str):
        self.sendLine(error_output)

@check_alive
def command_pass_turn(self, line):
    if self.room.combat == None:
        self.finish_turn()
        return
    if self.status != ActorStatusType.FIGHTING:
        self.finish_turn()
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
def command_use(self, line):

    if line.endswith((' on', ' at')):
        self.sendLine('Use on who?')
        return

    id_to_name, name_to_id = get_skills()
    list_of_skill_names = [skill for skill in name_to_id.keys()]
    list_of_consumables = [utils.remove_color(item.name) for item in self.inventory.values() if item.item_type == ItemType.CONSUMABLE]
    whole_list = list_of_consumables + list_of_skill_names

    action = None
    target = self

    # target yourself if not trying to target anything else
    if ' on ' not in line and ' at ' not in line:
        action = line
        target = self
    # if you are targetting something else set target to that
    else:
        action, target = line.replace(' on ',' | ').replace(' at ',' | ').split(' | ')
        target = self.get_entity(target)
        # if no target is found then return
        if target == None:
            return

    best_match = utils.match_word(action, whole_list)

    # if you are trying to use an item
    #print(best_match)
    if best_match in list_of_consumables:
        item = self.get_item(action)

        def use_item(item, user, target):
            #self.use_manager.use_broadcast(self, target, item.use_perspectives)
            item.use(user, target)
            return

        if target == self:
            use_item(item, self, target)
            self.finish_turn()
            return

        elif target != self:
            if self.room.combat == None:
                self.sendLine('You can\'t use items on others out of combat')
                return

            if self not in self.room.combat.participants.values():
                self.sendLine(f'You can\'t use items on others while you are not in combat')
                return

            if target not in self.room.combat.participants.values():
                self.sendLine(f'You can\'t use items on others while they are not fighting')
                return

            use_item(item, self, target)
            self.finish_turn()


    elif best_match in list_of_skill_names:
        if action.lower() not in best_match.lower():
            self.sendLine('Use what?')
            return
        skill_id = name_to_id[best_match]
        # if skills.use finished with True statement and there were no errors
        if use_skill(self, target, skill_id) == True:
            self.finish_turn()

@check_not_in_combat
def command_rest(self, line):
    if self.status == ActorStatusType.DEAD:
        self.status = ActorStatusType.NORMAL

        self.stats[StatType.HP] = self.stats[StatType.HPMAX]
        self.stats[StatType.MP] = self.stats[StatType.MPMAX]

        self.simple_broadcast(
            'You ressurect',
            f'{self.pretty_name()} ressurects')
        self.protocol.factory.world.rooms['home'].move_player(self)
        self.simple_broadcast(
            None,
            f'{self.pretty_name()} has ressurected')
    else:

        self.stats[StatType.HP] = self.stats[StatType.HPMAX]
        self.stats[StatType.MP] = self.stats[StatType.MPMAX]

        if self.room.uid == 'home':
            self.simple_broadcast(
                f'You rest',
                f'{self.pretty_name()} rests'
                )
        else:
            self.simple_broadcast(
                f'You return to town to rest',
                f'{self.pretty_name()} returns back to town to rest'
                )
            self.protocol.factory.world.rooms['home'].move_player(self)
            self.simple_broadcast(
                None,
                f'{self.pretty_name()} has returned to town to rest'
                )
    self.affect_manager.unload_all_affects()
            