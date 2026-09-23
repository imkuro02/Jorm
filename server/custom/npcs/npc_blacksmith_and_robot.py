from actors.npcs import Npc


class CustomNpcRobot(Npc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def tick(self):
        from scripts.greet_message import greet_message
        greet_message(self, f'{self.id}\'s mechanical arm waves at you "Hell-o"')

from systems.dialog import Dialog
class blacksmith_dialog(Dialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def answer(self, line):
        _answer = super().answer(line)
        if self.current_line != 'scrap':
            return _answer
        for i in self.npc.room.actors.values():
            if type(i) == CustomNpcRobot:
                self.player.send_line('...')
                i.talk_to(self.player, they_talk_to_you = True)
                return True
        

class CustomNpcBlacksmith(Npc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dialog_manager = blacksmith_dialog
      