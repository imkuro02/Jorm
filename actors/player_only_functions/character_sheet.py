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
    self.stats[StatType.PP] += 1

    self.stats[StatType.HPMAX] += 5
    self.stats[StatType.MPMAX] += 5

    self.stats[StatType.HPMAX] += self.stats[StatType.BODY] + round(self.stats[StatType.SOUL]*.5)
    self.stats[StatType.MPMAX] += self.stats[StatType.MIND] + round(self.stats[StatType.SOUL]*.5) 

    #self.stats['armor'] += round(self.stats['dex']*.4)
    #self.stats['marmor'] += round(self.stats['dex']*.4)
    
    self.sendLine(f'@green{stat} {self.stats[stat]-1} -> {self.stats[stat]}. You gained a practice point!@normal')
        
@check_not_in_combat
def command_practice(self, line):
    
    #print(name_to_id[skill_name])
    if len(line) <= 1:
        output = f'You have {self.stats[StatType.PP]} practice points left.\n'
        output += f'{"Skill":<20} | {"Learned":<8} | {"Level Req":<5}\n'
        for skill_id in SKILLS.keys():
            if skill_id not in self.skills.keys():
                learned = 0
            else:
                learned = self.skills[skill_id]
            level = SKILLS[skill_id]['level_req']
            output += (f'{SKILLS[skill_id]["name"]:<20} | {str(learned) + "":<8} | {str(level):<5} \n')
        self.sendLine(f'{output}')
    else:
        id_to_name, name_to_id = get_skills()
        skill_name = utils.match_word(line, [name for name in name_to_id.keys()])
        skill_id = name_to_id[skill_name]

        if self.stats[StatType.PP] <= 0:
            self.sendLine('@redYou do not have enough points to practice@normal')
            return

        if skill_id not in SKILLS.keys():
            self.sendLine('This skill does not exist')
            return

        if skill_id in self.skills:
            # do not level beyond 6
            if self.skills[skill_id] >= 10:
                self.sendLine(f'@redYou are already a master at "{skill_name}"@normal')
                return
            #if self.skills[skill_id] > self.stats[StatType.PP]:
            #    self.sendLine(f'@redYou need {self.skills[skill_id]} practice points to practice this.@normal')
            #    return

            if 0 >= self.stats[StatType.PP]:
                self.sendLine(f'@redYou need don\'t have any practice points left@normal')
                return
            #self.stats[StatType.PP] -= self.skills[skill_id]
            #self.sendLine(f'@greenYou spend {self.skills[skill_id]} practice point(s) on "{skill_name}"@normal')
            self.stats[StatType.PP] -= 1
            self.sendLine(f'@greenYou spend one practice pointon "{skill_name}"@normal')
            self.skills[skill_id] += 1
            
        else:
            if self.stats[StatType.LVL] < SKILLS[skill_id]['level_req']:
                self.sendLine('@redYou are not high enough level to practice this skill@normal')
                return
            self.skills[skill_id] = 1
            self.sendLine(f'@greenYou learned the skill "{skill_name}"@normal')
            self.stats[StatType.PP] -= 1

        
def command_skills(self, line):
    id_to_name, name_to_id = get_skills()
    if len(line) > 0:
        skill_name = utils.match_word(line, [name for name in name_to_id.keys()])
        skill_id = name_to_id[skill_name]
        skill = SKILLS[skill_id]
        output = ''
        output += f'{skill["name"]}\n'
        output += f'{skill["description"]}\n'
        self.sendLine(output)
    else:
        if len(self.skills) == 0:
            self.sendLine('You do not know any skills...')
            return

        output = 'SKILLS:\n'
        max_length = max(len(skill) for skill in self.skills) + 1
        for skill_id in self.skills:
            output = output + f'{id_to_name[skill_id] + ":":<{max_length}} {self.skills[skill_id]}\n'
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
    temp_player = Player(None, self.name, None)
    self.stats = temp_player.stats
    self.skills = temp_player.skills
    #print(temp_player)
    del temp_player

    #self.stats = self.create_new_stats()
    #self.skills = self.create_new_skills()
    self.stats[StatType.EXP] = exp
    self.sendLine('@greenYou have reset your stats, experience is kept.@normal')

def command_stats(self, line):
    output = f'You are {self.get_character_sheet()}'
    output += f'\n'
    exp_needed = self.get_exp_needed_to_level() - self.stats[StatType.EXP]
    output += f'Level: {self.stats[StatType.LVL]}\n'
    if exp_needed > 0:
        output += f'@redYou need {exp_needed} exp to level up@normal\n'
    else:
        output += f'@greenYou have enough exp to level up@normal\n'
    output += f'Experience:      {self.stats[StatType.EXP]}\n'
    output += f'Practice Points: {self.stats[StatType.PP]}\n'
    self.sendLine(output)

def command_affects(self, line):
    if len(self.affect_manager.affects) == 0:
        output = 'You are not affected by anything'
    else:
        output = 'You are affected by:\n' 
        output += f'{"Affliction":<15} {"For":<3} {"Info"}\n'
        for aff in self.affect_manager.affects.values():
            output += f'{aff.info()}'
    self.sendLine(output)
    '''
    output = ''
    if line == '':
        if len(self.affect_manager.affects) == 0:
            output = 'You are not affected by anything'
        else:
            output = 'You are affected by:\n' 
            output += f'{"Affliction":<15} {"For":<3} {"Info"}\n'
            for aff in self.affect_manager.affects.values():
                output += f'{aff.info()}'
    else:
        output = self.affect_manager.load_affect(line)
        if output == None:
            self.sendLine('Could not load affect')
            return
        self.affect_manager.set_affect(output)
    self.sendLine(output)
    '''

def get_exp_needed_to_level(self):
    exp_needed = 2 ** self.stats[StatType.LVL]
    return exp_needed
