def command_talk(self, line):
    entity = self.get_entity(line)
    entity.talk_to(self)
    