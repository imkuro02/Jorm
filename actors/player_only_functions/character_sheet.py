from actors.player_only_functions.checks import check_not_in_combat, check_alive
from config import StatType, SKILLS
from skills.manager import get_skills
import utils

@check_not_in_combat
def command_level_up(self, stat):
    stat = stat.lower().capitalize()
    exp_needed = self.get_exp_needed_to_level()
    if self.get_exp_needed_to_level() > self.stats[StatType.EXP]:
        self.sendLine(f'You need {exp_needed-self.stats[StatType.EXP]}EXP to level up')
        return



    match stat.lower():
        case 'body':
            #self.stats[StatType.BODY] += 1
            stat = StatType.BODY
        case 'mind':
            #self.stats[StatType.MIND] += 1
            stat = StatType.MIND
        case 'soul':
            #self.stats[StatType.SOUL] += 1
            stat = StatType.SOUL
        case _:
            self.sendLine('You can only level up Body Mind or Soul')
            return

    
    self.stats[StatType.LVL] += 1
    self.stats[stat] += 1
    self.stats[StatType.PP] += 20

    hp_bonus = 0 + 5 + self.stats[StatType.BODY] + round(self.stats[StatType.SOUL]*.5)
    mp_bonus = 0 + 5 + self.stats[StatType.MIND] + round(self.stats[StatType.SOUL]*.5) 
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
    #print(name_to_id[skill_name])
    if len(line) <= 1:
        output = f'You have {self.stats[StatType.PP]} practice points left.\n'
        output += f'{"Skill":<20} | {"Learned":<8} | {"Level Req":<5}\n'
        for skill_id in SKILLS.keys():
            if not SKILLS[skill_id]['can_be_practiced']:
                continue
            if self.stats[StatType.LVL] < SKILLS[skill_id]['level_req'] :
                continue
            if skill_id not in self.skills.keys():
                learned = 0
            else:
                learned = self.skills[skill_id]
            level = SKILLS[skill_id]['level_req']
            output += (f'{SKILLS[skill_id]["name"]:<20} | {str(learned):<8} | {str(level):<5} \n')
        self.sendLine(f'{output}')
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
        output += f'MP cost: {skill["mp_cost"]} | HP cost: {skill["hp_cost"]} | Cooldown: {skill["cooldown"]}\n'
        output += f'{"You can use this skill on yourself." if skill["target_self_is_valid"] else "You cannot use this skill on yourself."}\n'
        output += f'{"You can use this skill out of combat." if not skill["must_be_fighting"] else "You can only use this skill in combat."}\n'
        output += f'{"You can use this skill on others." if skill["target_others_is_valid"] else "You cannot use this skill on others."}\n'
        

        self.sendLine(output)
    else:
        if len(self.skills) == 0:
            self.sendLine('You do not know any skills...')
            return

        output = 'SKILLS:\n'
        max_length = max(len(skill) for skill in self.skills) + 1
        output += f'{"Skill":<20} {"LVL":<4} {"MP":<4} {"HP":<4} {"Ready":<4}\n'
        for skill_id in self.skills:
            #cooldown = ""
            #if skill_id in self.cooldown_manager.cooldowns:
            #    cooldown = f'({self.cooldown_manager.cooldowns[skill_id]})'
            #output = output + f'{id_to_name[skill_id] + ":":<20} {self.skills[skill_id]} {cooldown}\n'
            output += f'{id_to_name[skill_id]:<20} '
            output += f'{self.skills[skill_id]:<4} '
            output += f'{SKILLS[skill_id]["mp_cost"]:<4} '
            output += f'{SKILLS[skill_id]["hp_cost"]:<4} '
            if skill_id not in self.cooldown_manager.cooldowns:
                cooldown = "Yes"
            else: 
                cooldown = f'{self.cooldown_manager.cooldowns[skill_id]}'
            output += f'{cooldown:<4} '
            output += '\n'
        self.sendLine(output)

@check_not_in_combat
@check_alive
def command_respec(self, line):
    Player = type(self)
    for i in self.slots.values():
        if i != None:
            self.sendLine('@redYou must unequip everything to respec@normal')
            return

    exp = self.stats[StatType.EXP]
    #money = self.stats[StatType.MONEY]
    temp_player = Player(None, self.name, None)
    self.stats = temp_player.stats
    self.skills = temp_player.skills
    #print(temp_player)
    del temp_player

    #self.stats = self.create_new_stats()
    #self.skills = self.create_new_skills()
    self.stats[StatType.EXP] = exp
    #self.stats[StatType.EXP] = money
    self.sendLine('@greenYou have reset your stats, experience is kept.@normal')

def command_stats(self, line):
    output = f'You are {self.get_character_sheet()}'
    output += f'\n'
    exp_needed = self.get_exp_needed_to_level() - self.stats[StatType.EXP]
    output += f'{StatType.name[StatType.LVL]} {self.stats[StatType.LVL]}\n'
    if exp_needed > 0:
        output += f'@redYou need {exp_needed} exp to level up@normal\n'
    else:
        output += f'@greenYou have enough exp to level up@normal\n'
    output += f'{StatType.name[StatType.EXP]}: {self.stats[StatType.EXP]}\n'
    output += f'{StatType.name[StatType.PP]}: {self.stats[StatType.PP]}\n'
    
    
    
    self.sendLine(output)

@check_alive
def command_affects(self, line):
    if len(self.affect_manager.affects) == 0:
        output = 'You are not affected by anything'
    else:
        output = 'You are affected by:\n' 
        output += f'{"Affliction":<15} {"For":<3} {"Info"}\n'
        for aff in self.affect_manager.affects.values():
            output += f'{aff.info()}'
    self.sendLine(output)


def get_exp_needed_to_level(self):
    exp_needed = 2 ** self.stats[StatType.LVL]
    return exp_needed
