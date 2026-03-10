import copy
import uuid

class FUNC_TAGS:
    MOVEMENT = 'movement'

class DelayedFunctionsManager:
    def __init__(self, factory):
        self.functions = {}
        self.factory = factory

    def run_delayed_function(self,):
        funcs = {}
        for f in self.functions:
            funcs[f] = self.functions[f]
        for func in funcs.values():
            if func['time'] <= int(self.factory.ticks_passed):
                func['func']() 
                del self.functions[func['id']] 

    def remove_delayed_functions_by_caller_and_tag(self, caller, tag):
        funcs = {}
        amount_of_deleted = 0
        for f in self.functions:
            funcs[f] = self.functions[f]
        for func in funcs.values():
            if func['caller'] != caller:
                continue

            if func['tag'] != tag:
                continue

            del self.functions[func['id']] 
            amount_of_deleted += 1

        return amount_of_deleted

    def add_delayed_function(self, caller, func, tag, delay):
        func_id = str(uuid.uuid4())
        self.functions[func_id] = {'id': func_id, 'time': int(int(self.factory.ticks_passed) + int(delay)), 'func': func, 'tag':tag, 'caller': caller}

    def tick(self):
        self.run_delayed_function()