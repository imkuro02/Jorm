from fuzzywuzzy import process
import logging
import datetime
import time

logging.basicConfig(
    filename=   'logs.log',     # Log file name
    level=      logging.DEBUG,  # Log level
    format=     '%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    filemode=   'a'  # Append mode; use 'w' to overwrite
)

'''
logging.debug("This is a debug message.")
logging.info("This is an info message.")
logging.warning("This is a warning message.")
logging.error("This is an error message.")
logging.critical("This is a critical message.")
'''

colors = {
    '\x1b[0;30m': 	'@black',
    '\x1b[0;31m': 	'@red',
    '\x1b[0;32m': 	'@green',
    '\x1b[0;33m': 	'@yellow',
    '\x1b[0;34m': 	'@blue',
    '\x1b[0;35m': 	'@purple',
    '\x1b[0;36m': 	'@cyan',
    '\x1b[0;37m': 	'@white',

    #'\x1b[0;40m': 	'@bgblack',
    #'\x1b[1;41m': 	'@bgred',
    #'\x1b[1;42m': 	'@bggreen',
    #'\x1b[1;43m': 	'@bgyellow',
    #'\x1b[1;44m': 	'@bgblue',
    #'\x1b[1;45m': 	'@bgpurple',
    #'\x1b[1;46m': 	'@bgcyan',
    #'\x1b[1;47m': 	'@bgwhite',

    '\x1b[1;30m': 	'@bblack',
    '\x1b[1;31m': 	'@bred',
    '\x1b[1;32m': 	'@bgreen',
    '\x1b[1;33m': 	'@byellow',
    '\x1b[1;34m': 	'@bblue',
    '\x1b[1;35m': 	'@bpurple',
    '\x1b[1;36m': 	'@bcyan',
    '\x1b[1;37m': 	'@bwhite',

    '\x1b[0m':      '@normal'
}

def match_word(word: str, l: list, get_score = False):
    best_match, best_score = process.extractOne(word, l)
    #print(best_match, best_score)
    if get_score:
        return best_match, best_score
    else:
        return best_match
    

def get_match(line, things):
    index = 1

    if '.' in line:
        index, line = line.split('.')
    
    line = line.strip()
    #index = index.strip()
    try:
        index = int(index)
    except ValueError:
        index = 1

    if index == 0:
        index = 1

    thing_names = []

    # reverse the dictionary so you can search from last order
    if index <= -1:
        things_reversed = {} 
        for i in reversed(things):
            things_reversed[i] = things[i]
        things = things_reversed
        # set the index to a positive value again
        index = abs(index)

    # create a list of names for fuzzy wuzzy
    for thing in things.values():
        thing_names.append(remove_color(thing.name))

    # get a list of matches
    matches = match_word_get_list(line, thing_names)

    # loop thru the matches, if the "line" is in the "things" name, add 1 to i, if i == index, then that is the "thing" you are looking for
    i = 1
    for val in things.values():
        #print(index, matches[index-1][0].lower(),'----------', i, val.name)
        
        if line.lower() in remove_color(val.name).lower(): 
            if i == index:
                return val
            i += 1

def match_word_get_list(word: str, l: list):
    
    matches = process.extract(word, l, limit=None)
    best_matches = [match for match in matches]
    return best_matches

 

def remove_color(line):
    for color_code in colors:
        line = line.replace(colors[color_code], '')
    '''
    line = line.replace('@red','')
    line = line.replace('@green','')
    line = line.replace('@brown','')
    line = line.replace('@yellow','')
    line = line.replace('@blue','')
    line = line.replace('@pink','')
    line = line.replace('@cyan','')
    line = line.replace('@gray','')
    line = line.replace('@normal','')
    '''
    return line

def print_colors():
    line = ''
    for color_code in colors:
        line = line + f'{colors[color_code]} {colors[color_code].replace("@","@.")}  '
    return line

def add_color(line):
    for color_code in colors:
        line = line.replace(colors[color_code], color_code)
    '''
    line = line.replace('@red','\x1b[1;31m')
    line = line.replace('@green','\x1b[1;32m')
    line = line.replace('@brown','\x1b[1;33m')
    line = line.replace('@yellow','\x1b[1;93m')
    line = line.replace('@blue','\x1b[1;34m')
    line = line.replace('@pink','\x1b[1;35m')
    line = line.replace('@cyan','\x1b[1;36m')
    line = line.replace('@gray','\x1b[1;90m')
    line = line.replace('@normal','\x1b[0m')
    line = line + '\x1b[0m'
    '''
    return line

class Table:
    def __init__(self, columns = 0, spaces = 5):
        self.columns = columns
        self.data = []
        self.SPACE = spaces

    def add_data(self, val, col='@normal'):
        data = {'val': str(val), 'col': str(col)}
        self.data.append(data)

    def get_table(self):
        if not self.data:
            #print("No data available to display.")
            return ''
        
        index = 0
        i = 0
        widths = {}
        for i in range(0,len(self.data)):
            widths[i] = 0

        i = 0
        for elem in self.data:
            #print(widths[i], len(elem['val']))
            if widths[i] < len(remove_color(elem['val'])) + self.SPACE:
                widths[i] = len(remove_color(elem['val'])) + self.SPACE
            #print(index)
            #print(i,index,elem,widths[index])
            i += 1
            if i == self.columns:
                index += 1
                i = 0

        output = ''
        i = 0
        index = 0
        for elem in self.data:
            #print(i,index,elem,widths[i])
            tmp_output = f'{remove_color(elem["val"]):<{widths[i]}}'
            tmp_output = tmp_output.replace(remove_color(elem['val']),elem['col']+elem['val']+f'@normal')
            output += add_color(tmp_output)
            i += 1
            if i == self.columns:
                output += f'\n'
                index += 1
                i = 0
        
        return output

        
def get_unix_timestamp():
    return int(time.time())

def get_datetime_from_unix(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

def get_datetime_ago_from_unix(timestamp):
    curr_time = get_unix_timestamp()
    # timestamp is the same as date_of_last_login 

    ago = curr_time - timestamp
    ago = seconds_to_dhms(int(ago), return_as_dict = True)

    for i in ago:
        if not ago[i] == 0:
            return(f'{ago[i]} {i} ago')

def seconds_to_dhms(seconds, return_as_dict = False):
    seconds_in_day = 86400
    seconds_in_hour = 3600
    seconds_in_minute = 60

    days = seconds // seconds_in_day
    seconds = seconds - (days * seconds_in_day)

    hours = seconds // seconds_in_hour
    seconds = seconds - (hours * seconds_in_hour)

    minutes = seconds // seconds_in_minute
    seconds = seconds - (minutes * seconds_in_minute)

    if not return_as_dict:
        return(f'{days:0>{2}}:{hours:0>{2}}:{minutes:0>{2}}:{seconds:0>{2}}')
    else:
        return({
            'days':days,
            'hours':hours,
            'minutes':minutes,
            'seconds':seconds
        })
    #return("{0:.0f}:{1:.0f}:{2:.0f}:{3:.0f}".format(
    #    days, hours, minutes, seconds))

if __name__ == '__main__':
    t = Table(3)
    t.add_data('a','@red')
    t.add_data('bc','@green')
    t.add_data('def','@yellow')
    t.add_data('12d34','@red')
    t.add_data('5678','@red')
    t.add_data('z','@green')
    t.add_data('xx','@yellow')
    t.add_data('l','@red')
    t.get_table()

    t = Table(3)
    t.add_data('NAME','@red')
    t.add_data('ADDRESS','@green')
    t.add_data('POO','@yellow')
    t.add_data('Charles','@red')
    t.add_data('Klyve','@red')
    t.add_data('PE','@green')
    t.add_data('ADAM OG EVA','@yellow')
    t.add_data('GJOVIK','@red')
    t.get_table()

    t = Table(4)
    t.add_data('SKILL','@yellow')
    t.add_data('MP COST','@bcyan')
    t.add_data('HP COST','@bred')
    t.add_data('COOLDOWN','@green')

    t.add_data('Slash','@red')
    t.add_data('12','@bcyan')
    t.add_data('11','@bred')
    t.add_data('NONE','@green')

    t.add_data('Become Ethereal','@red')
    t.add_data('1','@bcyan')
    t.add_data('NONE','@bred')
    t.add_data('12','@red')



    t.get_table()


                


