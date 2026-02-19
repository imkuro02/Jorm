def command_talk(self, line):
    actor = self.get_actor(line)
    if actor == None:
        self.send_line('Talk to who?')
        return
    
    actor.talk_to(self)
       

    