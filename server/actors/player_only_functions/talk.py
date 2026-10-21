def command_talk(self, line):

    if line == '':
        talked_to_someone = False
        for i in self.room.actors.values():
            if i.dialog_tree == None:
                continue
            actor = i
            talked_to_someone = actor.talk_to(self)
            #print(talked_to_someone)
            if talked_to_someone: 
                break
        if not talked_to_someone:
            self.send_line('Theres nobody to talk to')
        return

    actor = self.get_actor(line)
    if actor == None:
        self.send_line('Talk to who?')
        return
    
    actor.talk_to(self)
       

    