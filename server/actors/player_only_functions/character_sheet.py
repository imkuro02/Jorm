from actors.player_only_functions.checks import check_not_in_combat, check_alive
from configuration.config import StatType, SKILLS, SkillScriptValuesToNames
from skills.manager import get_skills, get_user_skill_level_as_index
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
    
    hp_bonus = 20000000000000000000
    mp_bonus = 20
    match stat.lower():
        case 'grit':
            stat = StatType.GRIT
            hp_bonus = 12
            mp_bonus = 3
        case 'flow':
            stat = StatType.FLOW
            hp_bonus = 10
            mp_bonus = 5
        case 'mind':
            stat = StatType.MIND
            hp_bonus = 3
            mp_bonus = 12
        case 'soul':
            stat = StatType.SOUL
            hp_bonus = 7
            mp_bonus = 8
        case _:
            self.sendLine('You can only level up Grit, Flow, Mind and Soul')
            return

    
    self.stats[StatType.LVL] += 1
    self.stats[stat] += 1
    self.stats[StatType.PP] += 20

    #hp_bonus = 0 + 0 + round(self.stats[StatType.GRIT] * 2) + round(self.stats[StatType.SOUL]*1) + round(self.stats[StatType.FLOW]*1) - 20
    #mp_bonus = 0 + 0 + round(self.stats[StatType.MIND] * 2) + round(self.stats[StatType.SOUL]*1) + round(self.stats[StatType.FLOW]*1) - 20
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
            t.add_data(int(SKILLS[skill_id]['level_req']))
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
        
        #print(SKILLS[skill_id])
        minimum_practice_req = SKILLS[skill_id]['script_values']['levels'][0]
        current_prac_level = 0

        if skill_id in self.skills:
            current_prac_level = self.skills[skill_id]

        #pp_to_spend = #new_prac_level - current_prac_level
        new_prac_level = current_prac_level + pp_to_spend
        
        if pp_to_spend <= 0:
            self.sendLine('@redYou can\'t spend negative amount of Practice Points@normal')
            return
        
        if pp_to_spend < minimum_practice_req and current_prac_level == 0:
            self.sendLine(f'@redYou must practice {skill_name} to a minium of {minimum_practice_req}@normal')
            return
        
        if new_prac_level > SKILLS[skill_id]['script_values']['levels'][-1]:
            self.sendLine(f'@redYou can\'t practice {skill_name} beyond level {SKILLS[skill_id]["script_values"]["levels"][-1]}@normal')
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
        output += f'@yellow{skill["name"]}\n@normal'
        output += f'@cyan{skill["description"]}@normal'

        skill_learned = skill_id in self.skills
        if skill_learned:
            users_skill_level = get_user_skill_level_as_index(self, skill_id)
        else:
            users_skill_level = 0

        t = utils.Table(2,1)
        t.add_data('Practiced:')
        if skill_learned:
            t.add_data(self.skills[skill_id],'@green')
        else:
            t.add_data('No','@red')

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

        output += t.get_table()
        if skill['can_be_practiced'] == False:
            output += f'@redThis skill cannot be practied!@normal\n'

        if 'script_values' in skill:
            t = utils.Table(len(skill['script_values']['levels']) + 1 ,4)

            
            for val_nam in SkillScriptValuesToNames:
                dic = SkillScriptValuesToNames
                if val_nam in skill['script_values']:
                    t.add_data(dic[val_nam]+':')
                    index = 0
                    for val in skill['script_values'][val_nam]:
                        # floats are most likely percentages
                        # so convert them to string and add "%"
                        if isinstance(val, int):
                            pass
                        if isinstance(val, float):
                            val = int(val*100)
                            val = str(val)+'%'

                        if index == users_skill_level and skill_learned:
                            t.add_data(val, col = '@green') 
                        else:
                            t.add_data(val) 
                        index += 1

            output += t.get_table()


        self.sendLine(output)
    else:
        if len(self.skills) == 0:
            self.sendLine('You do not know any skills...')
            return

        t = utils.Table(3, spaces = 2)
        t.add_data('Skill')
        t.add_data('R')
        t.add_data('Lvl')

        for skill_id in SKILLS:
            if skill_id not in self.skills:
                continue # skip unknown skills
                
            t.add_data(id_to_name[skill_id])
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
    #output += f'{StatType.name[StatType.LVL]} {self.stats[StatType.LVL]}\n'
    output += f'{StatType.name[StatType.EXP]}: {self.stats[StatType.EXP]}/{self.get_exp_needed_to_level()}\n'
    output += f'{StatType.name[StatType.PP]}: {self.stats[StatType.PP]}\n'

    self.sendLine(output)

@check_alive
def command_affects(self, line):
    def get_affects():
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
        return output
    output = get_affects()
    self.sendLine(output)

def get_exp_needed_to_level(self):
    l = self.stats[StatType.LVL]
    exp_needed = int(3 + ( l ** 3.5 )) #int(2 ** self.stats[StatType.LVL]) + (self.stats[StatType.LVL]*self.stats[StatType.LVL])
    return exp_needed
