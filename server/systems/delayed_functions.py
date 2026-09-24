import copy
import uuid

class FUNC_TAGS:
    ALL = 'all'
    MOVEMENT = 'movement'

class DelayedFunctionsManager:
    def __init__(self, factory):
        self.functions = {}
        self.functions_by_caller = {}
        self.factory = factory
        self.cancels = {}

    def add_delayed_function(self, caller, func, tag, delay):
        timestamp_rec = int(self.factory.ticks_passed)
        timestamp_run = int(int(self.factory.ticks_passed) + int(delay))

        func = {'timestamp_rec': timestamp_rec, 'timestamp_run': timestamp_run, 'func': func, 'tag': tag, 'caller': caller, 'run': True}
        if timestamp_run not in self.functions:
            self.functions[timestamp_run] = []
        self.functions[timestamp_run].append(func)

        if caller not in self.functions_by_caller:
            self.functions_by_caller[caller] = []
        self.functions_by_caller[caller].append(func)

    def remove_delayed_functions_by_caller_and_tag(self, caller, tag):
        amount_of_deleted = 0
        if caller not in self.functions_by_caller:
            return 0
        for func in self.functions_by_caller[caller]:
            if func['tag'] != tag and tag != FUNC_TAGS.ALL:
                continue
            if func['run']:
                amount_of_deleted += 1
                func['run'] = False
        return amount_of_deleted

    def run_delayed_function(self):
        timestamp = int(self.factory.ticks_passed-1)
        _list_to_run = []

        if timestamp in self.functions:
            _list_to_run = self.functions[timestamp].copy()

        for func in _list_to_run:
            if func['run']:
                func['func']() 
            self.functions_by_caller[func['caller']].remove(func)
            self.functions[func['timestamp_run']].remove(func)

            if self.functions[func['timestamp_run']] == []:
                del self.functions[func['timestamp_run']]

            if self.functions_by_caller[func['caller']] == []:
                del self.functions_by_caller[func['caller']]

        

    def tick(self):
        self.run_delayed_function()


'''     

class DelayedFunctionsManager:
    def __init__(self, factory):
        self.functions = {}
        self.factory = factory

    def run_delayed_function(self):
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

            if func['tag'] != tag and tag != FUNC_TAGS.ALL:
                continue

            del self.functions[func['id']] 
            amount_of_deleted += 1

        return amount_of_deleted

    def add_delayed_function(self, caller, func, tag, delay):
        func_id = str(uuid.uuid4())
        self.functions[func_id] = {'id': func_id, 'time': int(int(self.factory.ticks_passed) + int(delay)), 'func': func, 'tag':tag, 'caller': caller}

    def tick(self):
        self.run_delayed_function()
'''