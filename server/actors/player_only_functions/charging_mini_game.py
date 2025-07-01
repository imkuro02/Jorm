from actors.player_only_functions.checks import check_not_in_combat

import random

class ChargingMiniGame:
    def __init__(self, owner):
        self.owner = owner
        self.ticks_passed = 0
        self.charging = False

        self.ticks_to_seconds = 30
        self.ticks_for_charge = 10 * self.ticks_to_seconds

        self.charges = 0
        self.tries = 0
    
    def fail(self):
        self.owner.sendLine(f'You failed to charge ({self.charges})')

    def success(self):
        self.charges += 1
        self.owner.sendLine(f'You got one charge ({self.charges})')
        

    def stop(self):
        if not self.charging:
            return
        self.owner.sendLine('You stop charging')
        self.charging = False
        self.owner.gain_exp(self.charges)
        

    def start(self):
        self.owner.sendLine('You begin to charge')
        self.charging = True
        self.ticks_passed = 0
        self.charges = 0
        self.tries = 0

    def toggle(self):
        if self.charging:
            self.stop()
        else:
            self.start()

    def charge(self):
        #charge_tick_amount = self.ticks_passed / self.ticks_to_seconds
        
        roll = random.randint(0,10)
        if roll > self.charges:
            self.success()
        else:
            self.fail()
        self.tries += 1

        if self.tries >= 10:
            self.stop()

    def tick(self):
        if not self.charging:
            return
        
        self.ticks_passed += 1
        if self.ticks_passed % self.ticks_for_charge == 0:
            self.charge()
            
@check_not_in_combat
def command_charging_mini_game_toggle(self, line):
    self.charging_mini_game.toggle()