from actors.npcs import Npc


class npc_robot(Npc):
    @classmethod
    def compare_replace(self, npc_object):
        # return False
        if "npc_robot" not in npc_object.npc_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def tick(self):
        from custom.npcs import _utils
        _utils.greet_message(self, f'{self.id}\'s mechanical arm waves at you "Hell-o"')

from systems.dialog import Dialog
class blacksmith_dialog(Dialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def answer(self, line):
        _answer = super().answer(line)
        if self.current_line != 'scrap':
            return _answer
        for i in self.npc.room.actors.values():
            if type(i) == npc_robot:
                self.player.send_line('...')
                i.talk_to(self.player, they_talk_to_you = True)
                return True
        

class npc_blacksmith(Npc):
    @classmethod
    def compare_replace(self, npc_object):
        # return False
        if "npc_blacksmith" not in npc_object.npc_id.lower():
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dialog_manager = blacksmith_dialog
      