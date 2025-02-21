def command_talk(self, line):
    entity = self.get_entity(line)
    if entity == None:
        self.sendLine('Talk to who?')
        return
    entity.talk_to(self)
    