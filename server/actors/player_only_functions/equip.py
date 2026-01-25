from actors.player_only_functions.checks import check_alive, check_no_empty_line, check_not_trading, check_not_in_combat
from configuration.config import ItemType, EquipmentSlotType, StatType, Audio

@check_not_in_combat
@check_not_trading
def command_equipment(self, line):
    # if you type equip item, it will wear that item
    if line != '':
        item = self.get_item(line, search_mode = 'equipable')
        if item == None:
            self.sendLine('Equip what?', sound = Audio.ERROR)
            return
        
        item = item[0]

        if item.equiped:
            self.inventory_unequip(item)
        else:
            self.inventory_equip(item)
        # you can technically eq an item and unequip again to get the affliction
        # for one turn, until it is your turn, so things that might proc while enemy is first
        # you could have 2 of, easy solution is to have finish turn run twice for that not to happen
        # or literally anything, idk u can figure it out
        to_del = []
        for i in self.affect_manager.affects.values():
            if 'Wearing' in i.name or 'Wielding' in i.name:
                to_del.append(i)
        for i in to_del:
            i.on_finished(silent = True)
        self.finish_turn(force_cooldown = True)

        return

    output = f'You are wearing:\n{self.get_character_equipment(hide_empty = False)}\n'
    '''
    for i in self.slots_manager.slots:
        if None == self.slots_manager.slots[i]:
            output = output + f'{EquipmentSlotType.name[i] + ":":<12} ...\n'
        else:
            output = output + f'{EquipmentSlotType.name[i] + ":":<12} {self.inventory_manager.items[self.slots_manager.slots[i]].name}\n'
    '''
    self.sendLine(output)

def inventory_equip(self, item, forced = False):
    if item.slot != None:

        req_not_met = False
        for stat_name in item.stat_manager.reqs:
            if self.stat_manager.stats[stat_name] < item.stat_manager.reqs[stat_name]:
                if not forced:
                    self.sendLine(
                        f'@redYou do not meet the requirements of {item.stat_manager.reqs[stat_name]} {StatType.name[stat_name]}@normal',
                        sound = Audio.ERROR
                        )
                req_not_met = True

        if req_not_met and forced == False:
            return

        if self.slots_manager.slots[item.slot] != None:
            self.inventory_unequip(self.inventory_manager.items[self.slots_manager.slots[item.slot]])

        self.slots_manager.slots[item.slot] = item.id

        item.equiped = True
        for stat_name in item.stat_manager.stats:
            stat_val = item.stat_manager.stats[stat_name]
            self.stat_manager.gain_stat_points(stat_name, stat_val)
            #utils.debug_print(stat_name, item.stat_manager.stats[stat_name])
            #if stat_name == StatType.HPMAX: self.stat_manager.stats[StatType.HP] += stat_val
            #if stat_name == StatType.MPMAX: self.stat_manager.stats[StatType.MP] += stat_val
            #if stat_name == StatType.PHYARMORMAX: self.stat_manager.stats[StatType.PHYARMOR] += stat_val
            #if stat_name == StatType.MAGARMORMAX: self.stat_manager.stats[StatType.MAGARMOR] += stat_val
            #self.stat_manager.stats[stat_name] += stat_val
            #utils.debug_print(self.stat_manager.stats[stat_name])

        self.inventory_manager.limit = self.inventory_manager.base_limit + self.stat_manager.stats[StatType.INVSLOTS]

        for skill in item.skill_manager.skills:
            self.skill_manager.learn(skill, item.skill_manager.skills[skill])

        if not forced:
            self.sendSound(Audio.ITEM_GET)
            self.simple_broadcast(
                f'You equip {item.name}',
                f'{self.pretty_name()} equips {item.name}'
            )
            self.stat_manager.hp_mp_clamp_update()

        #self.slots[item.slot] = item.id
        #utils.debug_print(self.slots[item.slot])

        # clamp the max mp and hp


def inventory_unequip(self, item, silent = False):
    if item.equiped:
        self.slots_manager.slots[item.slot] = None
        item.equiped = False

        for stat_name in item.stat_manager.stats:
            stat_val = item.stat_manager.stats[stat_name]
            self.stat_manager.gain_stat_points(stat_name, -stat_val)
            #if stat_name == StatType.HPMAX: self.stat_manager.stats[StatType.HP] -= stat_val
            #if stat_name == StatType.MPMAX: self.stat_manager.stats[StatType.MP] -= stat_val
            #if stat_name == StatType.PHYARMORMAX: self.stat_manager.stats[StatType.PHYARMOR] -= stat_val
            #if stat_name == StatType.MAGARMORMAX: self.stat_manager.stats[StatType.MAGARMOR] -= stat_val
            #self.stat_manager.stats[stat_name] -= stat_val

        self.inventory_manager.limit = self.inventory_manager.base_limit + self.stat_manager.stats[StatType.INVSLOTS]

        for skill in item.skill_manager.skills:
            self.skill_manager.unlearn(skill, item.skill_manager.skills[skill])

        if silent:
            return

        self.stat_manager.hp_mp_clamp_update()
        self.sendSound(Audio.ITEM_GET)
        self.simple_broadcast(
            f'You unequip {item.name}',
            f'{self.pretty_name()} unequips {item.name}'
            )
