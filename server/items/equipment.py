import random

import affects.affects as affects
import systems.utils
from configuration.config import (
    EQUIPMENT_REFORGES,
    SKILLS
)
from configuration.constants.actor_status_type import ActorStatusType
from configuration.constants.color import Color
from configuration.constants.equipment_slot_type import EquipmentSlotType
from configuration.constants.item_type import ItemType
from configuration.constants.stat_type import StatType, StatBonus
from configuration.constants.bonus_type import BonusType
from items.misc import Item
from systems.utils import Table
import copy
class EquipSkillManager:
    def __init__(self, item):
        self.item = item
        self.skills = {}

    # code copy pasted from actor skill manager
    def learn(self, skill_id, amount=1):
        if skill_id not in self.skills:
            self.skills[skill_id] = amount
        else:
            self.skills[skill_id] += amount

    def unlearn(self, skill_id, amount=1):
        if skill_id not in self.skills:
            systems.utils.debug_print(
                f"{self.item.name} cant unlearn {skill_id} because it is not learned"
            )
            return

        if amount == self.skills[skill_id]:
            del self.skills[skill_id]
            return

        self.skills[skill_id] -= amount


class EquipmentStatManager:
    def __init__(self, item):
        self.item = item

        self.stats = {
            StatType.HPMAX: 0,
            # StatType.MPMAX: 0,
            StatType.PHYARMORMAX: 0,
            StatType.MAGARMORMAX: 0,
            StatType.GRIT: 0,
            StatType.FLOW: 0,
            StatType.MIND: 0,
            StatType.SOUL: 0,
            StatType.INVSLOTS: 0,
        }

        self.reqs = {
            StatType.HPMAX: 0,
            # StatType.MPMAX: 0,
            StatType.PHYARMORMAX: 0,
            StatType.MAGARMORMAX: 0,
            StatType.GRIT: 0,
            StatType.FLOW: 0,
            StatType.MIND: 0,
            StatType.SOUL: 0,
            StatType.LVL: 0,
            StatType.INVSLOTS: 0,
        }


class EquipmentBonus:
    def __init__(self, id=0, type="stat", key="marmor", val=69, premade_bonus=False):
        self.id = id
        self.premade_bonus = premade_bonus
        self.type = type
        self.key = key
        self.val = val


class EquipmentBonusManager:
    def __init__(self, item):
        self.item = item
        self.bonuses = {}

    def check_if_valid(self, bonus):
        if (
            bonus.type != BonusType.REFORGE
            and bonus.type != BonusType.SPECIAL
            and bonus.type != BonusType.SKILL_LEVEL
            and bonus.type != BonusType.STAT
            and bonus.type != BonusType.STAT_REQ
        ):
            systems.utils.debug_print("def check_if_valid(self, bonus) not of type")
            return False

        if bonus.type == BonusType.SKILL_LEVEL:
            if bonus.key not in SKILLS:
                systems.utils.debug_print(
                    "def check_if_valid(self, bonus) not in skills"
                )
                return False

        if bonus.type == BonusType.REFORGE:
            if bonus.key not in EQUIPMENT_REFORGES:
                systems.utils.debug_print(
                    f"{bonus.key} def check_if_valid(self, bonus) not in "
                )
                return False

        if bonus.type == BonusType.SPECIAL:
            if bonus.key not in EQUIPMENT_REFORGES:
                systems.utils.debug_print(
                    f"{bonus.key} def check_if_valid(self, bonus) not in "
                )
                return False

        if bonus.type == BonusType.STAT:
            if bonus.key not in StatType.name:
                systems.utils.debug_print(
                    "def check_if_valid(self, bonus) not in stats"
                )
                return False

        return True

    def remove_bonus(self, bonus):
        # systems.utils.debug_print(bonus.__dict__, bonus.type == 'reforge')
        # systems.utils.debug_print(EQUIPMENT_REFORGES[bonus.key])
        match bonus.type:
            case BonusType.REFORGE | BonusType.SPECIAL:
                if (
                    EQUIPMENT_REFORGES[bonus.key]["affliction_to_create"]
                    == "StatBonusPerItemLevel"
                ):
                    reforge_variables = EQUIPMENT_REFORGES[bonus.key]["vars"]
                    stat = reforge_variables["var_a"]
                    _bonus = float(reforge_variables["var_b"])
                    _bonus = int(_bonus * self.item.stat_manager.reqs[StatType.LVL])
                    # self.item.stat_manager.reqs[stat] -= _bonus
                    self.item.stat_manager.stats[stat] -= _bonus

            case BonusType.SKILL_LEVEL:
                if bonus.key in SKILLS:
                    self.item.skill_manager.learn(bonus.key, -bonus.val)
                pass

            case BonusType.STAT:
                if bonus.key in [
                    StatType.HPMAX,
                    StatType.GRIT,
                    StatType.FLOW,
                    StatType.MIND,
                    StatType.SOUL,
                    StatType.PHYARMOR,
                    StatType.MAGARMOR,
                    StatType.INVSLOTS,
                ]:
                    self.item.stat_manager.stats[bonus.key] -= bonus.val

            case BonusType.STAT_REQ:
                if bonus.key in [
                    StatType.HPMAX,
                    StatType.GRIT,
                    StatType.FLOW,
                    StatType.MIND,
                    StatType.SOUL,
                    StatType.PHYARMOR,
                    StatType.MAGARMOR,
                    StatType.INVSLOTS,
                    StatType.LVL,
                ]:
                    self.item.stat_manager.reqs[bonus.key] -= bonus.val

        #systems.utils.debug_print(bonus.__dict__,'removed')
        del self.bonuses[bonus.id]

    # recursive is used for re-adding reforge bonuses
    # if recursive is true, remove all reforges
    # apply whatever bonus was added
    # then re-add the removed reforges
    # merging is supposed to merge its value to an already existing bonus if possible
    # currently disabled because it didnt fawking work
    def add_bonus(self, bonus, recursive=True, merging=True):
        if bonus.id == 0:
            id = len(self.bonuses) + 10_000
        else:
            id = bonus.id
            bonus.id = id

        if not self.check_if_valid(bonus):
            systems.utils.debug_print("failed to add bonus ", bonus.__dict__)
            return

        for i in copy.deepcopy(self.bonuses).values():
            if not merging:
                continue
            if self.bonuses[i.id].type != bonus.type or self.bonuses[i.id].key != bonus.key:
                continue
            if i.type not in [BonusType.SKILL_LEVEL, BonusType.STAT, BonusType.STAT_REQ]:
                continue
    
            bonus.val += i.val
            self.remove_bonus(i)
            if bonus.val == 0:
                return
            self.add_bonus(bonus, merging = False)
            return
        

        if not self.check_if_valid(bonus):
            systems.utils.debug_print("failed to add bonus ", bonus.__dict__)
            return

        self.bonuses[id] = bonus
        bonus.id = id

        # systems.utils.debug_print(bonus.__dict__,'added')

        if recursive:
            to_del = []
            for bon in self.bonuses.values():
                if bon.type == BonusType.REFORGE:
                    to_del.append(bon)

            for bon in to_del:
                self.remove_bonus(bon)
                # systems.utils.debug_print('temp removing reforge', bon)

        match bonus.type:
            case BonusType.REFORGE | BonusType.SPECIAL:
                if (
                    EQUIPMENT_REFORGES[bonus.key]["affliction_to_create"]
                    == "StatBonusPerItemLevel"
                ):
                    reforge_variables = EQUIPMENT_REFORGES[bonus.key]["vars"]
                    stat = reforge_variables["var_a"]
                    _bonus = float(reforge_variables["var_b"])
                    _bonus = int(_bonus * self.item.stat_manager.reqs[StatType.LVL])
                    # self.item.stat_manager.reqs[stat] += _bonus
                    self.item.stat_manager.stats[stat] += _bonus

            case BonusType.SKILL_LEVEL:
                if bonus.key in SKILLS:
                    self.item.skill_manager.learn(bonus.key, bonus.val)

            case BonusType.STAT:
                if bonus.key in [
                    StatType.HPMAX,
                    StatType.GRIT,
                    StatType.FLOW,
                    StatType.MIND,
                    StatType.SOUL,
                    StatType.PHYARMOR,
                    StatType.MAGARMOR,
                    StatType.INVSLOTS,
                ]:
                    self.item.stat_manager.stats[bonus.key] += bonus.val

            case BonusType.STAT_REQ:
                if bonus.key in [
                    StatType.HPMAX,
                    StatType.GRIT,
                    StatType.FLOW,
                    StatType.MIND,
                    StatType.SOUL,
                    StatType.PHYARMOR,
                    StatType.MAGARMOR,
                    StatType.INVSLOTS,
                    StatType.LVL,
                ]:
                    self.item.stat_manager.reqs[bonus.key] += bonus.val

        if recursive:
            for bon in to_del:
                # bon.id = bonus.id
                self.add_bonus(bon, recursive=False)
                # systems.utils.debug_print('after temp removing reforge, add it back', bon.__dict__)

        # resort list so there are no empty spaces
        tmp = {}
        x = 0
        for i in self.bonuses:
            x += 1
            tmp[x] = self.bonuses[i]
            tmp[x].id = x

        self.bonuses = tmp
        # return bonus


class Equipment(Item):
    def __init__(self):
        super().__init__()
        if hasattr(self, 'stat_manager'):
            return
        self.item_type = ItemType.EQUIPMENT
        self.stack_max = 1

        self.slot = EquipmentSlotType.TRINKET
        self.equiped = False

        self.rank = 0

        self.stat_manager = EquipmentStatManager(self)
        self.manager = EquipmentBonusManager(self)
        self.skill_manager = EquipSkillManager(self)

        """
        boon = EquipmentBonus(type = 'skill_level', key = 'swing', val = 1)
        self.manager.add_bonus(boon)
        boon = EquipmentBonus(type = 'stat', key = 'grit', val = 1)
        self.manager.add_bonus(boon)
        boon = EquipmentBonus(type = 'stat', key = 'armor', val = 1)
        self.manager.add_bonus(boon)
        """

    def to_dict(self):
        my_dict = {
            "slot": self.slot,
            "equiped": self.equiped,
            "stats": self.stat_manager.stats,
            "requirements": self.stat_manager.reqs,
        } | super().to_dict()

        return my_dict

    def set_stat(self, stat, value):
        self.stat_manager.stats[stat] = value

    def identify(self, identifier=None):
        output = super().identify(identifier)
        output += f"{Color.TOOLTIP}Equipment slot:{Color.NORMAL} {EquipmentSlotType.name[self.slot]}\n"
        output += f"{Color.TOOLTIP}Requirements to equip:{Color.NORMAL}\n"
        t = Table(2, 3)
        ordered_stats = [
            StatType.LVL,
            StatType.HPMAX,
            StatType.PHYARMORMAX,
            StatType.MAGARMORMAX,
            StatType.GRIT,
            StatType.FLOW,
            StatType.MIND,
            StatType.SOUL,
            StatType.INVSLOTS,
        ]
        for stat in ordered_stats:
            if self.stat_manager.reqs[stat] == 0:
                continue
            col = (
                f"{Color.GOOD}"
                if self.stat_manager.reqs[stat] <= identifier.stat_manager.stats[stat]
                else f"{Color.BAD}"
            )
            t.add_data(StatType.name[stat])
            t.add_data(self.stat_manager.reqs[stat], col=col)
        output += t.get_table() + '\n'

        output += f"{Color.TOOLTIP}Stats with Bonuses:{Color.NORMAL}\n"
        t = Table(2, 3)
        ordered_stats = [
            StatType.HPMAX,
            StatType.PHYARMORMAX,
            StatType.MAGARMORMAX,
            StatType.GRIT,
            StatType.FLOW,
            StatType.MIND,
            StatType.SOUL,
            StatType.INVSLOTS,
        ]

        hp_bonus = 0
        pa_bonus = 0
        ma_bonus = 0
        for stat in ordered_stats:
            stat_val = self.stat_manager.stats[stat]
            if stat in StatBonus:
                hp_bonus += stat_val * StatBonus[stat][StatType.HP]
                pa_bonus += stat_val * StatBonus[stat][StatType.PHYARMOR]
                ma_bonus += stat_val * StatBonus[stat][StatType.MAGARMOR]

        for stat in ordered_stats:
            stat_val = self.stat_manager.stats[stat]
            if stat == StatType.HPMAX: stat_val = stat_val + hp_bonus
            if stat == StatType.PHYARMORMAX: stat_val = stat_val + pa_bonus
            if stat == StatType.MAGARMORMAX: stat_val = stat_val + ma_bonus

            if stat_val == 0:
                continue
                    
            t.add_data(StatType.name[stat])
            # t.add_data(self.stat_manager.stats[stat])
            if stat_val < 0:
                t.add_data(f"{stat_val}", Color.BAD)
            else:
                t.add_data(f"+{stat_val}", Color.GOOD)
            # t.add_data(f'({new})')

        output += t.get_table() + '\n'

        if len(self.manager.bonuses.values()) >= 1:
            output += f"{Color.TOOLTIP}Bonuses:{Color.NORMAL}\n"
            for bonus in self.manager.bonuses.values():
                col = f"{Color.GOOD}+" if bonus.val >= 1 else f"{Color.BAD}"
                match bonus.type:
                    case BonusType.REFORGE:
                        output += f'{EQUIPMENT_REFORGES[bonus.key]["name"]} Reforge: '
                        output += f"{EQUIPMENT_REFORGES[bonus.key]['description']}\n"

                    case BonusType.SPECIAL:
                        output += f'{EQUIPMENT_REFORGES[bonus.key]["name"]} Bonus: '
                        output += f"{EQUIPMENT_REFORGES[bonus.key]['description']}\n"

                    case BonusType.SKILL_LEVEL:
                        output += f"Skill Bonus: {SKILLS[bonus.key]['name']} {col}{bonus.val}{Color.BACK}\n"

                    case BonusType.STAT:
                        output += f"Stat Bonus: {StatType.name[bonus.key]} {col}{bonus.val}{Color.BACK}\n"

                    case BonusType.STAT_REQ:
                        output += f"Req Bonus: {StatType.name[bonus.key]} {col}{bonus.val}{Color.BACK}\n"

        if self.equiped == False:
            no_changes = True
            output += f"{Color.TOOLTIP}On equip changes:{Color.NORMAL}\n"
            t = Table(2, 0)
            '''
            output += f"\n{Color.TOOLTIP}On equip changes:{Color.NORMAL}\n"
            eq = None
            if (
                identifier.slots_manager.slots[self.slot] != None
                and identifier.slots_manager.slots[self.slot] != self.id
            ):
                eq = identifier.inventory_manager.items[
                    identifier.slots_manager.slots[self.slot]
                ]

            t = Table(3, 3)
            no_changes = True
            for stat in ordered_stats:
                
                if eq != None:
                    difference = (
                        new_item[stat] - old_item[stat]
                    )

                new_stat = identifier.stat_manager.stats[stat] + difference

                if new_stat == identifier.stat_manager.stats[stat]:
                    continue
                elif new_stat < identifier.stat_manager.stats[stat]:
                    no_changes = False
                    t.add_data(f"{StatType.name[stat]}")
                    t.add_data(difference, col=f"{Color.BAD}")
                    t.add_data(f"({new_stat})")
                elif new_stat > identifier.stat_manager.stats[stat]:
                    no_changes = False
                    t.add_data(f"{StatType.name[stat]}")
                    t.add_data(f"+{difference}", col=f"{Color.GOOD}")
                    t.add_data(f"({new_stat})")
            '''
            eq = None
            if (
                identifier.slots_manager.slots[self.slot] != None
                and identifier.slots_manager.slots[self.slot] != self.id
            ):
                eq = identifier.inventory_manager.items[
                    identifier.slots_manager.slots[self.slot]
                ]
            
            
            no_change_stats= {}
            old_item_stats = {}
            new_item_stats = {}

            for stat in ordered_stats:
                old_item_stats[stat] = identifier.stat_manager.stats[stat]

            if eq != None:
                identifier.inventory_unequip(eq, silent=True)
            for stat in ordered_stats:
                no_change_stats[stat] = identifier.stat_manager.stats[stat]

            identifier.inventory_equip(self, forced=True)
            for stat in ordered_stats:
                new_item_stats[stat] = identifier.stat_manager.stats[stat]

            identifier.inventory_unequip(self, silent=True)
            if eq != None:
                identifier.inventory_equip(eq, forced=True)
            
            

            

            
            for stat in ordered_stats:
                stat_val = new_item_stats[stat] - old_item_stats[stat]
                if stat_val == 0:
                    continue
                no_changes = False
                t.add_data(StatType.name[stat]+'   ')
                # t.add_data(self.stat_manager.stats[stat])
                if new_item_stats[stat] > old_item_stats[stat]:
                    t.add_data(f"+{new_item_stats[stat] - old_item_stats[stat]}", Color.GOOD)
                    '''
                    t.add_data(f" ( ")
                    t.add_data(f"{old_item_stats[stat]}", Color.BAD)
                    t.add_data(f" -> ")
                    t.add_data(f"{new_item_stats[stat]}", Color.GOOD)
                    t.add_data(f" ) ")
                    '''
                else:
                    t.add_data(f"{new_item_stats[stat] - old_item_stats[stat]}", Color.BAD)
                    '''
                    t.add_data(f" ( ")
                    t.add_data(f"{old_item_stats[stat]}", Color.GOOD)
                    t.add_data(f" -> ")
                    t.add_data(f"{new_item_stats[stat]}", Color.BAD)
                    t.add_data(f" ) ")
                    '''

            if no_changes:
                t.add_data(f"No changes")
                t.add_data(f"")
            # output += t.get_table()

            def construct_id(bonus):
                return f"{bonus.type}/{bonus.key}"

            def construct_dict(bonuses, bonus, positive):
                if bonus.type != "skill_level":
                    return bonuses

                if construct_id(bonus) in bonuses:
                    bonuses[construct_id(bonus)]["val"] += bonus.val * (
                        1 if positive else -1
                    )
                else:
                    bonuses[construct_id(bonus)] = {
                        "type": bonus.type,
                        "key": bonus.key,
                        "val": bonus.val * (1 if positive else -1),
                    }
                return bonuses

            bonuses = {}
            for bonus in self.manager.bonuses.values():
                bonuses = construct_dict(bonuses, bonus, positive=True)

            if eq != None:
                for bonus in eq.manager.bonuses.values():
                    bonuses = construct_dict(bonuses, bonus, positive=False)

            for bonus in bonuses.values():
                val = bonus["val"]
                curr = 0
                new = bonus["val"]
                if bonus["key"] in identifier.skill_manager.skills:
                    val = bonus["val"]
                    curr = identifier.skill_manager.skills[bonus["key"]]
                    new = curr + val

                if new == curr:
                    continue

                t.add_data(f"Skill {SKILLS[bonus['key']]['name']}")
                if new < curr:
                    t.add_data(f"{val}", f"{Color.BAD}")
                else:
                    t.add_data(f"+{val}", f"{Color.GOOD}")
                #t.add_data(f"({new})")

            output += t.get_table()
        return output.strip("\n")

    def reforge(self, forced_reforge_id=None):
        item = self
        to_del = []
        for bon in item.manager.bonuses.values():
            if bon.type == BonusType.REFORGE:
                to_del.append(bon)

        for bon in to_del:
            item.manager.remove_bonus(bon)

        reforge_choices = []
        for i in EQUIPMENT_REFORGES:
            # i is the reforge_id
            # systems.utils.debug_print(f"{EQUIPMENT_REFORGES[i]['slot_'+item.slot]} {EQUIPMENT_REFORGES[i]['reforge_id']}")
            if bool(EQUIPMENT_REFORGES[i]["slot_" + item.slot]):
                reforge_choices.append(EQUIPMENT_REFORGES[i])

        reforge_chances = {}
        _chance = 0
        for i in reforge_choices:
            # systems.utils.debug_print('choice')
            reforge_chances[i["reforge_id"]] = {
                "start": _chance + i["roll_chance"],
                "range": i["roll_chance"],
            }
            _chance = _chance + i["roll_chance"]

        rolled_reforge = None

        if forced_reforge_id == None:
            roll = random.randint(0, _chance)
            # systems.utils.debug_print(roll,_chance)
            for i in reforge_chances:
                if (
                    roll <= reforge_chances[i]["start"]
                    and roll >= reforge_chances[i]["range"]
                ):
                    # systems.utils.debug_print(i)
                    rolled_reforge = i
                    break
        else:
            rolled_reforge = forced_reforge_id

        if rolled_reforge != None:
            new_bonus = EquipmentBonus(
                type=BonusType.REFORGE, key=rolled_reforge, val=1, premade_bonus=False
            )
            item.manager.add_bonus(new_bonus)

        return item

    def get_reforge_id(self):
        for i in self.manager.bonuses.values():
            if i.type == BonusType.REFORGE:
                return i.key
        return None

    # called at end of turn
    def finish_turn(self):
        # for i in self.manager.bonuses.values():
        #   systems.utils.debug_print(f'{self.name}, {i.id}: {i.type} {i.key} {i.val}')

        if self.get_reforge_id():
            self.reforge(self.get_reforge_id())

        if not self.equiped:
            # systems.utils.debug_print(self.name,'not equipped')
            return

        reforges_to_apply = []

        for i in self.manager.bonuses.values():
            if i.type == BonusType.SPECIAL:
                # systems.utils.debug_print(f'>>{i.key}')
                reforges_to_apply.append(i.key)
        reforges_to_apply.append(self.get_reforge_id())

        # systems.utils.debug_print(reforges_to_apply)

        obj_id = 0
        for reforge_id in reversed(reforges_to_apply):
            if reforge_id == None:
                continue

            if self.inventory_manager.owner.status == ActorStatusType.DEAD:
                continue

            reforge_obj = None
            affliction_to_create = (
                f"Reforge{EQUIPMENT_REFORGES[reforge_id]['affliction_to_create']}"
            )
            try:
                reforge_obj = getattr(affects, affliction_to_create)
            except AttributeError:
                reforge_obj = affects.AffectReforge
                err = f"cant set affliction object of {affliction_to_create} on {self} of id {self.premade_id} of unique id {self.id} finish_turn()"
                self.inventory_manager.owner.simple_broadcast(err, err)


            # the obj_id is here to make sure that you can have multiple of the same reforge 
            # and they dont override eachother
            
            if reforge_obj:
                obj_id += 1
                reforge_name = EQUIPMENT_REFORGES[reforge_id]["name"]
                # reforge_name = 'Reforged'
                # reforge_description = EQUIPMENT_REFORGES[reforge_id]['description']

                slot_name = EquipmentSlotType.name[self.slot]

                wear_or_wield = (
                    "Wearing" if self.slot != EquipmentSlotType.WEAPON else "Wielding"
                )
                # affliction_name = f'{wear_or_wield} {reforge_name} {slot_name}'
                affliction_name = f"{wear_or_wield} {slot_name} {reforge_id} {obj_id}"
                reforge_description = f"Your {slot_name} item is {reforge_name}"
                if reforge_obj == affects.AffectReforge:
                    reforge_description = (
                        reforge_description + " (Affliction didnt load properly)"
                    )

                aff = reforge_obj(
                    affect_source_actor = self.inventory_manager.owner,
                    affect_target_actor = self.inventory_manager.owner,
                    name = affliction_name,
                    description = reforge_description,
                    turns=3,
                    source_item = self,
                    reforge_variables=EQUIPMENT_REFORGES[reforge_id]["vars"],
                )
                self.inventory_manager.owner.affect_manager.set_affect_object(aff)

        # code to apply a bonus:
        # bonus dirk,special,dmg_phy_bonus,1