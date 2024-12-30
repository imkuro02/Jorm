from actors.player_only_functions.checks import check_not_in_combat, check_alive
from config import StatType, SKILLS
from skills.manager import get_skills
import utils

@check_not_in_combat
def command_name_change(self, line):
    if len(line) < 3:
        self.sendLine('@redName is too short@normal')
        return
    self.sendLine(f'Name changed from "{self.name}" to "{line}"')
    self.name = line

@check_not_in_combat
def command_level_up(self, stat):
    stat = stat.replace('up', '').strip() # cant trust nobody
    stat = stat.lower().capitalize()

    exp_needed = self.get_exp_needed_to_level()
    if self.get_exp_needed_to_level() > self.stats[StatType.EXP]:
        self.sendLine(f'You need {exp_needed-self.stats[StatType.EXP]}EXP to level up')
        return
    
    match stat.lower():
        case 'grit':
            stat = StatType.GRIT
        case 'flow':
            stat = StatType.FLOW
        case 'mind':
            stat = StatType.MIND
        case 'soul':
            stat = StatType.SOUL
        case _:
            self.sendLine('You can only level up Grid, Mind and Soul')
            return

    
    self.stats[StatType.LVL] += 1
    self.stats[stat] += 1
    self.stats[StatType.PP] += 20

    hp_bonus = 0 + 0 + round(self.stats[StatType.GRIT] * 2) + round(self.stats[StatType.SOUL]*1) + round(self.stats[StatType.FLOW]*1)
    mp_bonus = 0 + 0 + round(self.stats[StatType.MIND] * 2) + round(self.stats[StatType.SOUL]*1) + round(self.stats[StatType.FLOW]*1)
    self.stats[StatType.HPMAX]  += hp_bonus
    self.stats[StatType.MPMAX]  += mp_bonus
    self.stats[StatType.HP]     += hp_bonus
    self.stats[StatType.MP]     += mp_bonus
   

    #self.stats['armor'] += round(self.stats['dex']*.4)
    #self.stats['marmor'] += round(self.stats['dex']*.4)
    
    self.sendLine(f'@green{stat} {self.stats[stat]-1} -> {self.stats[stat]}. @normal')

@check_alive
@check_not_in_combat
def command_practice(self, line):
    if len(line) <= 1:
        output = f'You have {self.stats[StatType.PP]} practice points left.\n'
        t = utils.Table(3)
        t.add_data('Skill')
        t.add_data('Lvl')
        t.add_data('Req')
        for skill_id in SKILLS.keys():
            if SKILLS[skill_id]['can_be_practiced'] == False:
                continue
            if SKILLS[skill_id]['level_req'] > self.stats[StatType.LVL]:
                continue

            col = '@red'
            if skill_id not in self.skills.keys():
                learned = 0
            else:
                learned = self.skills[skill_id]
            if learned >= 1:
                col = '@yellow'
            if learned >= 50:
                col = '@green'
            if learned >= 95:
                col = '@bgreen'

            t.add_data(SKILLS[skill_id]["name"])
            t.add_data(learned, col)
            t.add_data(SKILLS[skill_id]['level_req'])
        self.sendLine(t.get_table() + output)
    else:
        line = line.split()
        if len(line) < 2:
            self.sendLine('@redWrong syntax for practicing@normal')
            return
        
        try:
            pp_to_spend = int(''.join(line[-1::1]))
            line = " ".join(line[:-1:])
        except ValueError as e:
            self.sendLine('@redWrong syntax for practicing@normal')
            return

        id_to_name, name_to_id = get_skills()
        skill_name = utils.match_word(line, [name for name in name_to_id.keys()])
        skill_id = name_to_id[skill_name]

        if skill_id not in SKILLS.keys():
            self.sendLine('This skill does not exist')
            return

        if not SKILLS[skill_id]['can_be_practiced']:
            self.sendLine(f'@red{skill_name} cannot be practiced@normal')
            return

        if self.stats[StatType.LVL] < SKILLS[skill_id]['level_req']:
            self.sendLine(f'@redYou are not high enough level to practice {skill_name}@normal')
            return

        current_prac_level = 0

        if skill_id in self.skills:
            current_prac_level = self.skills[skill_id]

        #pp_to_spend = #new_prac_level - current_prac_level
        new_prac_level = current_prac_level + pp_to_spend
        
        if pp_to_spend <= 0:
            self.sendLine('@redYou can\'t spend negative amount of Practice Points@normal')
            return
        
        if new_prac_level > 95:
            self.sendLine('@redYou can\'t practice a skill beyond level 95@normal')
            return

        if pp_to_spend > self.stats[StatType.PP]:
            self.sendLine('@redYou don\'t have enough Practice Points@normal')
            return

        
        self.stats[StatType.PP] -= pp_to_spend
        self.sendLine(f'@greenYou spend {pp_to_spend} Practice Points on "{skill_name}"@normal')
        self.skills[skill_id] = new_prac_level
       
def command_skills(self, line):
    id_to_name, name_to_id = get_skills()
    if len(line) > 0:
        skill_name = utils.match_word(line, [name for name in name_to_id.keys()])
        skill_id = name_to_id[skill_name]
        skill = SKILLS[skill_id]
        output = ''
        output += f'{skill["name"]}\n'
        output += f'{skill["description"]}\n'
        output += f'\n'
        output += f'{StatType.name[StatType.MP]} Cost: {skill["mp_cost"]} | {StatType.name[StatType.HP]} Cost: {skill["hp_cost"]} | Cooldown: {skill["cooldown"]}\n'
        output += f'{"@greenYou can use this skill on yourself.@normal" if skill["target_self_is_valid"] else "@redYou cannot use this skill on yourself.@normal"}\n'
        output += f'{"@greenYou can use this skill on others.@normal" if skill["target_others_is_valid"] else "@redYou cannot use this skill on others.@normal"}\n'
        output += f'{"@greenYou can use this skill out of combat.@normal" if not skill["must_be_fighting"] else "@redYou can only use this skill in combat.@normal"}\n'
        if skill['can_be_practiced'] == False:
            output += f'@redThis skill cannot be practied!@normal\n'
        

        self.sendLine(output)
    else:
        if len(self.skills) == 0:
            self.sendLine('You do not know any skills...')
            return

        t = utils.Table(5, spaces = 2)
        t.add_data('Skill')
        t.add_data('HP')
        t.add_data('MP')
        t.add_data('R')
        t.add_data('Lvl')

        for skill_id in SKILLS:
            if skill_id not in self.skills:
                continue # skip unknown skills
                
            t.add_data(id_to_name[skill_id])
            t.add_data(SKILLS[skill_id]["hp_cost"], '@red')
            t.add_data(SKILLS[skill_id]["mp_cost"], '@cyan')

           
            if skill_id not in self.cooldown_manager.cooldowns:
                t.add_data('Y','@green')
            else: 
                t.add_data(f'{self.cooldown_manager.cooldowns[skill_id]}', '@red')

            #t.add_data(self.skills[skill_id])
            col = '@red'
            if skill_id not in self.skills.keys():
                learned = 0
            else:
                learned = self.skills[skill_id]
            if learned >= 1:
                col = '@yellow'
            if learned >= 50:
                col = '@green'
            if learned >= 95:
                col = '@bgreen'
            t.add_data(self.skills[skill_id], col)
        
        self.sendLine(t.get_table())

@check_not_in_combat
@check_alive
def command_respec(self, line):
    Player = type(self)
    for i in self.slots_manager.slots.values():
        if i != None:
            self.sendLine('@redYou must unequip everything to respec@normal')
            return

    exp = self.stats[StatType.EXP]
    temp_player = Player(None, self.name, None)
    self.stats = temp_player.stats
    self.skills = temp_player.skills
    #print(temp_player)
    del temp_player


    self.stats[StatType.EXP] = exp
    self.sendLine('@greenYou have reset your stats, experience is kept.@normal')

def command_stats(self, line):
    output = f'You are {self.get_character_sheet()}'
    #output += f'\n'
    #exp_needed = self.get_exp_needed_to_level() - self.stats[StatType.EXP]
    output += f'{StatType.name[StatType.LVL]} {self.stats[StatType.LVL]}\n'
    output += f'{StatType.name[StatType.EXP]}: {self.stats[StatType.EXP]}/{self.get_exp_needed_to_level()}\n'
    output += f'{StatType.name[StatType.PP]}: {self.stats[StatType.PP]}\n'

    self.sendLine(output)

@check_alive
def command_affects(self, line):
    if len(self.affect_manager.affects) == 0:
        output = 'You are not affected by anything'
    else:
        output = 'You are affected by:\n' 
        t = utils.Table(3,1)
        t.add_data('Aff')
        t.add_data('x')
        t.add_data('Description')
        #output += f'{"Affliction":<15} {"For":<3} {"Info"}\n'
        
        for aff in self.affect_manager.affects.values():
            #output += f'{aff.info()}'
            t.add_data(aff.name)
            t.add_data(aff.turns)
            t.add_data(aff.description)
        output = output + t.get_table()

    self.sendLine(output)

def get_exp_needed_to_level(self):
    exp_needed = 2 ** self.stats[StatType.LVL]
    return exp_needed
