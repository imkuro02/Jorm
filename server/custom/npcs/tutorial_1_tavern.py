from actors.npcs import Npc
from configuration.constants.room_constant import RoomConstant

class CustomTutorial1Tavern(Npc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self):
        if self.room == None:
            return
        from scripts.greet_message import greet_message
        
        send_to = [i for i in self.room.actors.values() if type(i).__name__ == 'Player']
        greet_message(
            self = self, 
            message = f'{self.id} coughs',
            send_to = send_to
            )

     