import utils 
from configuration.config import ActorStatusType
party_commands = {
    'create':   'party_create',    # create a party
    'invite':   'party_invite',    # invite to party
    'join':     'party_join',      # accept party invite "party join NAME OF WHO INVITED YOU"
    'kick':     'party_kick',      # kick from party
    'leave':    'party_leave',     # leave current party
    'leader':   'party_leader',    # promote someone else to party leader
    'look':     'party_look'       # get stats for party
    
}

class Party:
    def __init__(self, actor):
        self.actor = actor
        self.participants = {}
        self.invited = {}
        self.add_participant(self.actor)

    def add_participant(self, participant):
        for par in self.participants.values():
            par.sendLine(f'{participant.pretty_name()} joins the party')

        self.participants[participant.id] = participant
        participant.party_manager.party = self

        if self.actor != participant:
            participant.sendLine(f'You join {self.actor.pretty_name()}\'s party')
            

    def remove_participant(self, participant):
        
        if participant.id not in self.participants:
            return

        for par in self.participants.values():
            par.sendLine(f'{participant.pretty_name()} leaves the party')

        if participant == self.actor:
            to_remove = []
            for i in self.participants.values():
                if i == self.actor: 
                    continue
                to_remove.append(i)
            for i in to_remove:
                self.remove_participant(i)

        del self.participants[participant.id]
        participant.party_manager.party = None

class PartyManager:
    def __init__(self, actor):
        self.actor = actor
        self.party = None
        self.invitations = []

    def get_party_id(self):
        if self.party != None:
            return self.party.actor.id
        return self.actor.id
        
    def clear_invites(self):
        self.invitations = []
   
    def party_create(self, line):
        if self.party != None:
            self.actor.sendLine('You are already in a party')
        self.party = Party(self.actor)
        self.actor.sendLine('You create a party')
        self.clear_invites()
    
    def party_invite(self, line):
        
        if self.party == None:
            self.actor.sendLine('You are not in a party')
            return
        if self.party.actor != self.actor:
            self.actor.sendLine('You are not the leader')
            return
        invited = self.actor.get_actor(line)
        
        if invited == None:
            self.actor.sendLine('Invite who?')
            return
        if invited.party_manager.party != None:
            self.actor.sendLine(f'{invited.pretty_name()} is already in a party')
            return
        if invited == self.actor:
            self.actor.sendLine('You can\'t invite yourself')
            return
        if self.party in invited.party_manager.invitations:
            self.actor.sendLine(f'{invited.pretty_name()} already invited.')
            return
        # lazy way of making sure its a player you are inviting
        if type(invited).__name__ != 'Player':
            self.actor.sendLine(f'{invited.pretty_name()} cannot be invited')
            return
        invited.party_manager.invitations.append(self.party)
        self.actor.sendLine(f'{invited.pretty_name()} invited')
        invited.sendLine(f'{self.actor.pretty_name()} invited you to their party, "party join {self.actor.pretty_name()}" to accept')
        
        pass

    def party_join(self, line):
        if self.party != None:
            self.actor.sendLine('You are already in a party')
            return
        
        inviter = self.actor.get_actor(line)
        if inviter == None:
            return

        for i in self.invitations:
            if i.actor == inviter:
                i.add_participant(self.actor)
                self.clear_invites()

    def party_kick(self, line):
        if self.party == None:
            self.actor.sendLine('You are not in a party')
            return
        if self.party.actor != self.actor:
            self.actor.sendLine('You are not the leader')
            return
        best_match, best_score = utils.match_word(line, [par.name for par in self.party.participants.values()], get_score = True)
        if best_score < 75:
            self.actor.sendLine('Kick who from party?')
            return
        if best_match == self.actor.name:
            self.actor.sendLine('You kick yourself in the butt!')
            return
        par = utils.get_match(line, self.party.participants)
        if par in self.party.participants.values():
            self.party.remove_participant(par)


    def party_leave(self, line = ''):
        if self.party == None:
            self.actor.sendLine('You are not in a party')
            return
        self.party.remove_participant(self.actor)
        self.actor.sendLine('You left the party')
        self.clear_invites()

    def party_leader(self, line):
        if self.party == None:
            self.actor.sendLine('You are not in a party')
            return
        pass

    def party_look(self, line):
        if self.party == None:
            self.actor.sendLine('You are not in a party')
            self.actor.command_send_prompt('')
            return

        output = ''
        t = utils.Table(2,1)
        t.add_data('Party')
        t.add_data('Stats')
        #t.add_data('Magicka')
        for i in self.party.participants.values():
            t.add_data(i.pretty_name())
            t.add_data(i.prompt())
        output = t.get_table()
        self.actor.sendLine(output)
    
    def handle_party_message(self, line):
        # empty lines are handled as resend last line
        if not line: 
            line = 'look'

        if self.actor.status != ActorStatusType.NORMAL and line != 'look':
            self.actor.sendLine('You can only do "party" in combat.')
            return
        
        command = line.split()[0]
        line = " ".join(line.split()[1::]).strip()

        best_match, best_score = utils.match_word(command, party_commands.keys(), get_score = True)
        if best_score < 75:
            self.actor.sendLine(f'You wrote "{command}" did you mean "{best_match}"?\nUse "help party" to learn more about this command.')
            return
    
        script = getattr(self, party_commands[best_match])
        script(line)


    