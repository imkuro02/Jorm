from config import ActorStatusType, StatType
class Combat:
    def __init__(self, room, participants):
        self.room = room
        self.participants = participants
        self.order = []
        self.current_actor = None
        self.time_since_turn_finished = 0
        self.round = 1
        self.initiative()
        
    def tick(self):
        if self.current_actor == None:
            return

        self.time_since_turn_finished += 1

        if len(self.participants) == 0:
            self.combat_over()

        #print(self.time_since_turn_finished, len(self.participants))
        if self.time_since_turn_finished == 30*20:
            if type(self.current_actor).__name__ == "Player":
                self.current_actor.simple_broadcast(
                    '@yellowYour turn is over in 10 seconds.@normal',
                    f'{self.current_actor.name}\'s turn is over in 10 seconds.'
                )

        if self.time_since_turn_finished >= 30*30:
            if type(self.current_actor).__name__ == "Player":
                self.current_actor.simple_broadcast(
                    '@yellowYou missed your turn.@normal',
                    f'{self.current_actor.name} missed their turn.'
                )

            self.time_since_turn_finished = 0
            self.next_turn()


        '''
        team1_died = True
        team2_died = True
        for i in self.participants.values():
            if i.status != 'dead' and type(i).__name__ == "Player":
                team1_died = False
            if i.status != 'dead' and type(i).__name__ == "Enemy":
                team2_died = False
            i.tick()
        '''
        for i in self.participants.values():
            i.tick()

        #if team1_died or team2_died:
        #    self.combat_over()

        if self.current_actor.room != self.room:
            print(self.current_actor.name, 'removed from combat')
            if self.current_actor.id in self.participants: del self.participants[self.current_actor.id]
            self.next_turn()
            return

        if self.current_actor.status == ActorStatusType.DEAD:
            self.next_turn()
            return      

    def combat_over(self):
        for i in self.participants.values():
            if i.status == ActorStatusType.FIGHTING: i.status = ActorStatusType.NORMAL
            if type(i).__name__ == "Player":
                i.sendLine('@yellowCombat over!@normal')

        self.participants = {}
        self.room.combat = None

    def next_turn(self):
        team1_died = True
        team2_died = True
        for i in self.participants.values():
            if i.status != ActorStatusType.DEAD and type(i).__name__ == "Player":
                team1_died = False
            if i.status != ActorStatusType.DEAD and type(i).__name__ == "Enemy":
                team2_died = False
        if team1_died or team2_died:
            self.combat_over()
            return

        self.time_since_turn_finished = 0
        if len(self.order) == 0:
            self.initiative()
            return
        
        self.current_actor = self.order[0]
        self.order.pop(0)
        self.current_actor.set_turn()

    def initiative(self):
        for i in self.participants.values():
            if i.status != ActorStatusType.DEAD:
                self.order.append(i)

        for i in self.order:
            if type(i).__name__ == "Player":
                combat_stats = f'\n@yellowCombat overview (Round {self.round})@normal:'
                for participant in self.order:
                    combat_stats = combat_stats + f'\n{participant.pretty_name()} [@red{participant.stats[StatType.HP]}@normal/@red{participant.stats[StatType.HPMAX]}@normal]'
                i.sendLine(combat_stats)
                #i.sendLine(f'@yellowTurn order: {[actor.name for actor in self.order]}@normal')
                
        self.round += 1
        for i in self.order:
            i.status = ActorStatusType.FIGHTING

        if len(self.order) == 0:
            self.combat_over()
            return

        self.next_turn()
        #self.current_actor = self.order[0]
        #self.current_actor.set_turn()

        
