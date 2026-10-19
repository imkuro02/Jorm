def command_talk(self, line):

    if line == '':
        for i in self.room.actors.values():
            if i.dialog_tree == None:
                continue
            actor = i
            actor.talk_to(self)
        self.send_line('Theres nobody to talk to')
        return

    actor = self.get_actor(line)
    if actor == None:
        self.send_line('Talk to who?')
        return
    
    actor.talk_to(self)
       

    