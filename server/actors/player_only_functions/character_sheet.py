import systems.utils
from actors.player_only_functions.checks import check_alive, check_not_in_combat
from configuration.config import (
    SKILLS,
    Audio,
    Color,
    SkillScriptValuesToNames,
    StatType,
)
from skills.manager import get_skills, get_user_skill_level_as_index

"""
@check_not_in_combat
def command_name_change(self, line):
    if len(line) < 3:
        self.sendLine(f'{Color.NORMAL}Name is too short{Color.NORMAL}')
        return
    self.sendLine(f'Name changed from "{self.name}" to "{line}"')
    self.name = line
"""


@check_not_in_combat
def command_level_up(self, stat):
    stat = stat.replace("up", "").strip()  # cant trust nobody
    stat = stat.lower().capitalize()

    exp_needed = self.get_exp_needed_to_level()
    if self.get_exp_needed_to_level() > self.stat_manager.stats[StatType.EXP]:
        self.sendLine(
            f"You need {exp_needed - self.stat_manager.stats[StatType.EXP]}EXP to level up"
        )
        return

    match stat.lower():
        case "grit":
            stat = StatType.GRIT
        case "flow":
            stat = StatType.FLOW
        case "mind":
            stat = StatType.MIND
        case "soul":
            stat = StatType.SOUL
        case _:
            self.sendLine("You can only level up Grit, Flow, Mind and Soul")
            return

    increase_by = 1
    self.stat_manager.gain_stat_points(stat, increase_by)
    self.stat_manager.stats[StatType.LVL] += 1

    # if self.stat_manager.stats[StatType.LVL]
    self.gain_practice_points(1)
    # self.stat_manager.stats[StatType.PP] += 1

    # self.actor.inventory_equip(item, forced = True)
    # hp_bonus = 0 + 0 + round(self.stat_manager.stats[StatType.GRIT] * 2) + round(self.stat_manager.stats[StatType.SOUL]*1) + round(self.stat_manager.stats[StatType.FLOW]*1) - 20
    # mp_bonus = 0 + 0 + round(self.stat_manager.stats[StatType.MIND] * 2) + round(self.stat_manager.stats[StatType.SOUL]*1) + round(self.stat_manager.stats[StatType.FLOW]*1) - 20

    # self.stat_manager.stats['armor'] += round(self.stat_manager.stats['dex']*.4)
    # self.stat_manager.stats['marmor'] += round(self.stat_manager.stats['dex']*.4)

    self.sendLine(
        f"{Color.GOOD}{stat} {self.stat_manager.stats[stat] - increase_by} -> {self.stat_manager.stats[stat]}. {Color.NORMAL}"
    )


@check_alive
@check_not_in_combat
def command_practice(self, line):
    if len(line) <= 1:
        # output = f'You have {self.stat_manager.stats[StatType.PP]} practice points left.\n'
        t = systems.utils.Table(4, 1)
        # t.add_data('C')
        # t.add_data('R')
        # t.add_data('L')
        # t.add_data('Skill')

        last_lvl_req = -1
        # t.add_data('Req')
        sorted_data = sorted(
            SKILLS, key=lambda x: (SKILLS[x]["level_req"], SKILLS[x]["practice_cost"])
        )
        for skill_id in sorted_data:
            if SKILLS[skill_id]["can_be_practiced"] == False:
                continue

            override_color = None
            if SKILLS[skill_id]["level_req"] > self.stat_manager.stats[StatType.LVL]:
                override_color = "@bblack"

            lvl_req = int(SKILLS[skill_id]["level_req"])
            if lvl_req > last_lvl_req:
                last_lvl_req = lvl_req
                t.add_data(f"Requires Level {last_lvl_req}:", filler=" ")
                for i in range(0, 3):
                    t.add_data("___", filler="_")

            equips = []
            for item in self.slots_manager.slots.values():
                if item == None:
                    continue
                equips.append(self.inventory_manager.items[item])

            for item in equips:
                self.inventory_unequip(item, silent=True)
            # systems.utils.debug_print(self.skill_manager.skills)
            ##
            skill_cost = (
                SKILLS[skill_id]["practice_cost"]
                + (sum(self.skill_manager.skills.values()))
                - (
                    self.skill_manager.skills[skill_id]
                    if skill_id in self.skill_manager.skills
                    else 0
                )
                - 2
            )  # -2 since you start with two skills
            if skill_cost <= 0:
                skill_cost = 1
            ##

            skill_level = 0
            if skill_id in self.skill_manager.skills:
                skill_level = self.skill_manager.skills[skill_id]

            skill_name = SKILLS[skill_id]["name"]

            skill_level_req = int(SKILLS[skill_id]["level_req"])

            can_afford = skill_cost <= self.stat_manager.stats[StatType.PP]
            meets_lvl_req = skill_level_req <= self.stat_manager.stats[StatType.LVL]
            skill_max_level = int(SKILLS[skill_id]["script_values"]["levels"][-1])

            col = Color.NORMAL
            if override_color != None:
                col = override_color
            t.add_data(
                f"{'' if skill_level <= 0 else f'{Color.GOOD}Practice Level{Color.NORMAL} {Color.IMPORTANT}{skill_level}{Color.NORMAL}:'}",
                col=col,
            )
            t.add_data(f"{skill_name}", col=col, filler=".")
            t.add_data(
                f" Costs {skill_cost} PP"
                if skill_level < skill_max_level
                else " Max Level",
                col=col,
            )
            t.add_data(
                f"(can practice)"
                if (can_afford and meets_lvl_req and skill_level < skill_max_level)
                else f"",
                col=col,
            )
            # t.add_data(f'Requires Level {skill_level_req}.')

            for item in equips:
                self.inventory_equip(item, forced=True)

        output = ""
        output += f"*All skills go up in cost by 1 PP, except the skill you practice.\n"
        output += f"You are Level {Color.IMPORTANT}{self.stat_manager.stats[StatType.LVL]}{Color.NORMAL}.\n"
        output += f"You have {Color.IMPORTANT}{self.stat_manager.stats[StatType.PP]}{Color.NORMAL} practice points left.\n"

        self.sendLine(t.get_table() + output)

    else:
        id_to_name, name_to_id = get_skills()
        skill_name = systems.utils.match_word(
            line, [name for name in name_to_id.keys()]
        )
        skill_id = name_to_id[skill_name]

        equips = []
        for item in self.slots_manager.slots.values():
            if item == None:
                continue
            equips.append(self.inventory_manager.items[item])

        for item in equips:
            self.inventory_unequip(item, silent=True)

        if skill_id in self.skill_manager.skills:
            if (
                self.skill_manager.skills[skill_id]
                >= SKILLS[skill_id]["script_values"]["levels"][-1]
            ):
                self.sendLine(f"{skill_name} is already max level")
                for item in equips:
                    self.inventory_equip(item, forced=True)
                return

        # systems.utils.debug_print(self.skill_manager.skills)
        ##
        pp_to_spend = (
            SKILLS[skill_id]["practice_cost"]
            + (sum(self.skill_manager.skills.values()))
            - (
                self.skill_manager.skills[skill_id]
                if skill_id in self.skill_manager.skills
                else 0
            )
            - 2
        )  # -2 since you start with two skills
        if pp_to_spend <= 0:
            pp_to_spend = 1
        ##

        for item in equips:
            self.inventory_equip(item, forced=True)

        if skill_id not in SKILLS.keys():
            self.sendLine(f"{Color.BAD}This skill does not exist{Color.NORMAL}")
            return

        if not SKILLS[skill_id]["can_be_practiced"]:
            self.sendLine(f"{Color.BAD}{skill_name} cannot be practiced{Color.NORMAL}")
            return

        if self.stat_manager.stats[StatType.LVL] < SKILLS[skill_id]["level_req"]:
            self.sendLine(
                f"{Color.BAD}You are not high enough level to practice {skill_name}{Color.NORMAL}"
            )
            return

        # systems.utils.debug_print(SKILLS[skill_id])
        # minimum_practice_req = SKILLS[skill_id]['script_values']['levels'][0]
        # current_prac_level = 0

        # if skill_id in self.skill_manager.skills:
        #    if self.skill_manager.skills[skill_id] >= 1:
        #        self.sendLine(f'{skill_name} is learned.')
        #    else:
        #        self.sendLine(f'{skill_name} is forgotten.')
        #    return

        # pp_to_spend = #new_prac_level - current_prac_level
        if skill_id in self.skill_manager.skills:
            new_prac_level = self.skill_manager.skills[skill_id] + 1
        else:
            new_prac_level = 1

        if pp_to_spend <= 0:
            self.sendLine(
                f"{Color.BAD}You can't spend negative amount of Practice Points{Color.NORMAL}"
            )
            return

        # if pp_to_spend < minimum_practice_req and current_prac_level == 0:
        #    self.sendLine(f'@redYou must practice {skill_name} to a minium of {minimum_practice_req}@normal')
        #    return

        # if new_prac_level > SKILLS[skill_id]['script_values']['levels'][-1]:
        #    self.sendLine(f'@redYou can\'t practice {skill_name} beyond level {SKILLS[skill_id]["script_values"]["levels"][-1]}@normal')
        #    return

        if pp_to_spend > self.stat_manager.stats[StatType.PP]:
            self.sendLine(
                f"{Color.BAD}You don't have enough Practice Points{Color.NORMAL}"
            )
            return

        self.stat_manager.stats[StatType.PP] -= pp_to_spend
        if pp_to_spend == 1:
            self.sendLine(
                f'{Color.GOOD}You spend {pp_to_spend} Practice Point on "{skill_name}"{Color.NORMAL}'
            )
        else:
            self.sendLine(
                f'{Color.GOOD}You spend {pp_to_spend} Practice Points on "{skill_name}"{Color.NORMAL}'
            )
        self.skill_manager.skills[skill_id] = new_prac_level


def command_skills(self, line):
    id_to_name, name_to_id = get_skills()
    if len(line) > 0:
        skill_name = systems.utils.match_word(
            line, [name for name in name_to_id.keys()]
        )
        skill_id = name_to_id[skill_name]
        skill = SKILLS[skill_id]
        output = ""
        output += f"{Color.IMPORTANT}{skill['name']}\n{Color.NORMAL}"
        output += f"{Color.DESCRIPTION}{skill['description']}{Color.NORMAL}"

        skill_learned = skill_id in self.skill_manager.skills
        if skill_learned:
            users_skill_level = get_user_skill_level_as_index(self, skill_id)
        else:
            users_skill_level = 0

        _target_self = skill["target_self_is_valid"]
        _target_others = skill["target_others_is_valid"]
        _target_items = skill["target_item_is_valid"]
        _can_use_in_combat = skill["can_use_in_combat"]
        _can_use_out_of_combat = skill["can_use_out_of_combat"]
        _can_practice = skill["can_be_practiced"]
        _is_offensive = skill["is_offensive"]
        _is_aoe = 0 if not "aoe" in skill["script_values"] else 1
        _bounces = 0 if not "bounce_amount" in skill["script_values"] else 1
        _bounce_bonus = 0 if not "bounce_bonus" in skill["script_values"] else 1
        _ends_turn = skill["end_turn"]
        _has_delay = "delay" in skill["script_values"]
        _name = skill["name"]
        _target = ""
        _targets = [_target_self, _target_others, _target_items]
        match _targets:
            case [0, 0, 0]:
                _target = "cannot be used on anything (what)"
            case [1, 0, 0]:
                _target = "can be used on yourself only"
            case [0, 1, 0]:
                _target = "can be used on others only"
            case [0, 0, 1]:
                _target = "can be used on items only"
            case [1, 1, 0]:
                _target = "can be used on anyone"
            case [0, 1, 1]:
                _target = "can be used on others and items"
            case [1, 0, 1]:
                _target = "can be used on yourself and items"

        _combat = ""
        _combat = [_can_use_in_combat, _can_use_out_of_combat]
        match _combat:
            case [0, 0]:
                _combat = "cannot be used at all"
            case [1, 0]:
                _combat = "can only be used in combat"
            case [0, 1]:
                _combat = "can only be used out of combat"
            case [1, 1]:
                _combat = "can be used any time"

        extra_info = ""
        if not _ends_turn:
            extra_info += f"{_name} does not end your turn in combat." + "\n"
            if _has_delay:
                extra_info += f" * {_name} delay will override this behaviour" + "\n"
        if _is_aoe:
            others = "enemies" if _is_offensive else "allies"
            extra_info += (
                f"{_name} affects your chosen target, but also AOE amount of {others}."
                + "\n"
            )
        if _bounces >= 1:
            others = "enemies" if _is_offensive else "allies"
            extra_info += f"{_name} affects your chosen target first," + "\n"
            extra_info += f" but then bounces BOUNCES times to {others}," + "\n"
            extra_info += f" the power is amplified by BOUNCE BONUS each bounce," + "\n"
            extra_info += f" * if there are no valid targets, the bounce stops." + "\n"
        if _has_delay:
            extra_info += f"The use of {_name} will be delayed and" + "\n"
            extra_info += f"no other actions can be taken until finished." + "\n"
            extra_info += f" * No delay out of combat." + "\n"
        extra_info += f"{_name} {_combat}." + "\n"
        if not _can_practice:
            extra_info += f"{_name} CANNOT be learned via practices." + "\n"

        """(
            f'{_name} is {"a offensive" if _is_offensive else "an non-offensive" } skill that {_target}.'
            f'It {_combat}, and '
            f'it {"can" if _can_practice else "cannot"} be practiced. '
            f'{f"{_name} can bounce up to BOUNCES times." if _bounces >= 1 else ""  }{f"The strength of {_name} will be amplified by BOUNCE BONUS each bounce." if _bounce_bonus > 0 else ""}'
            f'{f"{_name} will target up to AOE targets, the character you use it on will always be targeted first." if _is_aoe else ""  }'
            f'{_name} {"does" if _ends_turn else "does not"} end your turn after use.'
        )"""

        extra_info = f"{Color.DESCRIPTION}{extra_info}{Color.NORMAL}"

        t = systems.utils.Table(2, 1)
        # t.add_data(':')
        # if skill_learned:
        #    t.add_data(self.skill_manager.skills[skill_id],'@green')
        # else:
        #    t.add_data('No','@red')
        """
        t.add_data('Target self:')
        if skill["target_self_is_valid"]:
            t.add_data('Yes','@yellow')
        else:
            t.add_data('No','@red')

        t.add_data('Target others:')
        if skill["target_others_is_valid"]:
            t.add_data('Yes','@yellow')
        else:
            t.add_data('No','@red')

        t.add_data('Combat only:')
        if skill["must_be_fighting"]:
            t.add_data('Yes','@yellow')
        else:
            t.add_data('No','@red')
        """

        output += t.get_table()
        # if skill['can_be_practiced'] == False:
        #    output += f'@redThis skill cannot be practied!@normal\n'

        if "script_values" in skill:
            t = systems.utils.Table(len(skill["script_values"]["levels"]) + 1, 4)

            for val_nam in SkillScriptValuesToNames:
                # systems.utils.debug_print(val_nam)
                if val_nam == "levels":
                    continue
                dic = SkillScriptValuesToNames
                if val_nam in skill["script_values"]:
                    t.add_data(dic[val_nam] + ":")
                    index = 0
                    for val in skill["script_values"][val_nam]:
                        # floats are most likely percentages
                        # so convert them to string and add "%"
                        if isinstance(val, int):
                            if val_nam == "hp_cost":
                                val = systems.utils.calculate_skill_hp_cost(
                                    actor=self,
                                    base_value=skill["script_values"]["hp_cost"][index],
                                )
                            pass
                        # if isinstance(val, int):
                        #    if val_nam == 'mp_cost':
                        #        val = systems.utils.calculate_skill_mp_cost(actor = self, base_value = skill['script_values']['mp_cost'][index])
                        #    pass
                        if isinstance(val, float):
                            val = int(val * 100)
                            val = str(val) + "%"

                        if index == users_skill_level and skill_learned:
                            t.add_data(val, col=Color.GOOD)
                        else:
                            t.add_data(val)
                        index += 1

            output += t.get_table()

        self.sendLine(output + extra_info.strip())
    else:
        if len(self.skill_manager.skills) == 0:
            self.sendLine("You do not know any skills...")
            return

        t = systems.utils.Table(3, spaces=2)
        t.add_data("Skill")
        t.add_data("Ready")
        t.add_data("Level")

        for skill_id in SKILLS:
            equips = []
            for item in self.slots_manager.slots.values():
                if item == None:
                    continue
                equips.append(self.inventory_manager.items[item])

            cur_lvl = 0
            if skill_id in self.skill_manager.skills:
                cur_lvl = self.skill_manager.skills[skill_id]

            for item in equips:
                self.inventory_unequip(item, silent=True)

            nat_lvl = 0
            if skill_id in self.skill_manager.skills:
                nat_lvl = self.skill_manager.skills[skill_id]

            for item in equips:
                self.inventory_equip(item, forced=True)

            # if skill_id not in self.skill_manager.skills:
            #    continue # skip unknown skills
            # if self.skill_manager.skills[skill_id] <= 0:
            #    continue

            if nat_lvl == 0 and cur_lvl == 0:
                continue

            diff = cur_lvl - nat_lvl

            t.add_data(id_to_name[skill_id])
            if skill_id not in self.cooldown_manager.cooldowns and diff >= 0:
                t.add_data("Ready", Color.GOOD)
            elif skill_id in self.cooldown_manager.cooldowns and diff >= 0:
                t.add_data(f"In {self.cooldown_manager.cooldowns[skill_id]}", Color.BAD)
            elif diff <= 0:
                t.add_data(f"Never", Color.BAD)

            if diff == 0:
                diff = ""
            elif diff < 0:
                diff = f"{Color.NORMAL}({Color.BAD}{diff}{Color.NORMAL})"
            elif diff > 0:
                diff = f"{Color.NORMAL}({Color.GOOD}+{diff}{Color.NORMAL})"

            if cur_lvl >= 1:
                cur_lvl = f"{Color.GOOD}{cur_lvl}{Color.NORMAL}"
            else:
                cur_lvl = f"{Color.BAD}{cur_lvl}{Color.NORMAL}"

            t.add_data(f"{cur_lvl} {diff}")
        self.sendLine(t.get_table())


@check_not_in_combat
@check_alive
def command_respec(self, line):
    Player = type(self)
    # for i in self.slots_manager.slots.values():
    #    if i != None:
    #        self.sendLine('@redYou must unequip everything to respec@normal')
    #        return

    if not self.room.can_be_recall_site:
        self.sendLine(f"{Color.BAD}It is not safe to respec here{Color.BACK}")
        self.sendSound(Audio.ERROR)
        return

    list_of_requips = []
    for i in self.slots_manager.slots.values():
        if i != None:
            list_of_requips.append(i)
            self.inventory_unequip(self.inventory_manager.items[i], silent=True)

    exp = self.stat_manager.stats[StatType.EXP]
    temp_player = Player(None, self.name, None)
    self.stat_manager.stats = temp_player.stat_manager.stats
    self.skill_manager.skills = temp_player.skill_manager.skills
    # systems.utils.debug_print(temp_player)
    del temp_player

    self.stat_manager.stats[StatType.EXP] = exp
    self.sendLine(
        f"{Color.GOOD}You have reset your stats, experience is kept{Color.NORMAL}"
    )

    for i in list_of_requips:
        self.inventory_equip(self.inventory_manager.items[i], forced=True)


def command_stats(self, line):
    output = f"You are {self.get_character_sheet()}"
    self.sendLine(output)


# @check_alive
def command_affects(self, line):
    target = self
    if line == "":
        target = self
    else:
        target = self.get_actor(line)

    if target == None:
        self.sendLine("Check the afflictions of who?")
        return

    output = self.get_affects(target)
    self.sendLine(output)


def get_exp_needed_to_level(self):
    l = self.stat_manager.stats[StatType.LVL]
    exp_needed = int(
        3 + (l**3.5)
    )  # int(2 ** self.stat_manager.stats[StatType.LVL]) + (self.stat_manager.stats[StatType.LVL]*self.stat_manager.stats[StatType.LVL])
    return exp_needed
