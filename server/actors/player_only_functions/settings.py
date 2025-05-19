from utils import match_word

SETTINGS = ['alias','gmcp']


class Settings:
    def __init__(self, actor, aliases = None, gmcp = False):
        self.actor = actor
        if aliases == None:
            self.aliases = {}
        else:
            self.aliases = aliases
        self.gmcp = gmcp
        
    def command_settings(self, line):
        command = match_word(line, SETTINGS)
        self.actor.sendLine(f'{line}, {command}')
        

def command_settings(self, line):
    self.settings_manager.command_settings(line)