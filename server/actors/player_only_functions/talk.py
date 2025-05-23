def command_talk(self, line):
    actor = self.get_actor(line)
    if actor == None:
        self.sendLine('Talk to who?')
        return
    
    actor.talk_to(self)
       

    