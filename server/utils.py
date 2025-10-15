from fuzzywuzzy import process
import logging
import datetime
import time
import re
from configuration.config import IndentType
import math
import weakref
import random

class RefTracker:
    def __init__(self):
        self.refs = []

    def add_ref(self, obj):
        self.refs.append(weakref.ref(obj))

    def show_ref_all(self):
        refs = {}
        for ref in self.refs:
            obj = ref()  # dereference
            if obj is not None:
                t = type(obj).__name__  # get class name as string
                #print(t)
                # count per type
                refs[t] = refs.get(t, 0) + 1
            else:
                pass
                #print("<collected>")

        print("Ref sum:", refs)
            

REFTRACKER = RefTracker()

TOUNLOAD = {}

def unload(obj_to_unload):
    TOUNLOAD[obj_to_unload] = 0

def unload_fr():
    global TOUNLOAD  # <-- This is important

    _unloaded = []
    for obj_to_unload in TOUNLOAD:
        try:
            if type(obj_to_unload) == str:
                continue
            obj_dict = obj_to_unload.__dict__
            for key in obj_dict:
                try:
                    obj_dict[key] = None
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
        _unloaded.append(obj_to_unload)

    for i in _unloaded:
        del TOUNLOAD[i]
       

def generate_name():
    names = [
        "Auxy", "Niymiae", "Tanni", "Rahji", "Rahj", "Rahjii",
        "Redpot", "Kuro", "Christine", "Adne", "Ken",
        "Thomas", "Sandra", "Erling", "Viktor", "Wiktor",
        "Sam", "Dan", 'Xsefe'
    ]
    titles = ['Goon', 'Gamer', 'Gold Farmer', 'Noob', 'Pro', 'Mudder', 'Smelly']
    
    return random.choice(names) + ' The ' + random.choice(titles)


logging.basicConfig(
    filename=   'logs.log',     # Log file name
    level=      logging.DEBUG,  # Log level
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    filemode=   'a'  # 'a' is Append mode; use 'w' to overwrite
)


logging.getLogger("fuzzywuzzy").setLevel(logging.ERROR)

'''
logging.debug("This is a debug message.")
logging.info("This is an info message.")
logging.warning("This is a warning message.")
logging.error("This is an error message.")
logging.critical("This is a critical message.")
'''




colors = {
    '@black':   '\x1b[0;30m', 
    '@red':     '\x1b[0;31m', 
    '@green':   '\x1b[0;32m', 
    '@yellow':  '\x1b[0;33m', 
    '@blue':    '\x1b[0;34m', 
    '@purple':  '\x1b[0;35m', 
    '@cyan':    '\x1b[0;36m', 
    '@white':   '\x1b[0;37m', 

    '@bblack':  '\x1b[1;30m', 
    '@bred':    '\x1b[1;31m', 
    '@bgreen':  '\x1b[1;32m', 
    '@byellow': '\x1b[1;33m', 
    '@bblue':   '\x1b[1;34m', 
    '@bpurple': '\x1b[1;35m', 
    '@bcyan':   '\x1b[1;36m', 
    '@bwhite':  '\x1b[1;37m', 

    '@bgred':   '\x1b[0;41m',
    '@bggreen':   '\x1b[0;42m', 
    '@bgyellow':  '\x1b[0;43m', 
    '@bgblue':    '\x1b[0;44m', 
    '@bgpurple':  '\x1b[0;45m', 
    '@bgcyan':    '\x1b[0;46m', 
    '@bgwhite':   '\x1b[0;47m', 




    '@important':     '\x1b[1;33m',
    '@name_player':   '\x1b[0;46m',
    '@name_enemy':    '\x1b[0;47m',
    '@name_npc':      '\x1b[0;47m',
    '@name_quest':    '\x1b[0;47m',

    '@good':          '\x1b[0;32m',
    '@bad':           '\x1b[0;35m',

    '@normal':        '\x1b[0m', 
    '@back':          '\x1b[0;00x',
    '@tip':       '\x1b[1;33m',

    '@stat':    '\x1b[0;35m',
    '@wall':    '\x1b[100;30m',
    
    '@color':         '\x1b[0;00y',
    
    
}

def match_word(word: str, l: list, get_score = False):
    # dont process empty, return first
    if not word.strip():
        return l[0]
    
    best_match, best_score = process.extractOne(word, l)
    if get_score:
        return best_match, best_score
    else:
        return best_match
    

def get_match(line, things):
    index = 1

    if '.' in line:
        index = line.split('.')[0]
        line = line.split('.')[1]
    
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
    # dont process empty, return first
    if not word.strip(): 
        return [match for match in l]
    
    matches = process.extract(word, l, limit=None)
    best_matches = [match for match in matches]
    return best_matches

 

def remove_color(line):
    for color_code in colors:
        line = line.replace(color_code, '')
    
    
    return line

def print_colors():
    line = ''
    for color_code in colors:
        line = line + f'{colors[color_code]} {colors[color_code].replace("@","@.")}  '
    return line

def add_color(line):
    #return line
    #for color_code in colors:
    #    line = line.replace(color_code, colors[color_code])
    #return line

    split = line.split('@')
    colors_used = []
    for word in split:
        word = '@'+word
        for color_code in colors:
            if (color_code in word):
                colors_used.append(color_code)

    for index, col in enumerate(colors_used):
        if col == '@back':
            if index >= 2:
                colors_used[index] = colors_used[index-2]
            else:
                colors_used[index] = '@normal'
    
    for color_code in colors:
        line = line.replace(color_code, '@color')

    for index, col in enumerate(colors_used):
        line = line.replace('@color',colors[col],1)

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
            #output += add_color(tmp_output)
            
            output += tmp_output
            i += 1
            if i == self.columns:
                output += f'\n'
                index += 1
                i = 0

        #output = output[:-1] if output.endswith("\n") else output
        
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


import re



#  usually use 80
def chunkate(input_string, max_width=800):
    # Regex to match a color code (e.g., @red, @green, etc.) or a word
    color_code_regex = r'@[\w]+'

    # Split the string into chunks of color codes and normal text
    chunks = []
    i = 0
    while i < len(input_string):
        match = re.match(color_code_regex, input_string[i:])
        if match:
            # Found a color code
            chunks.append(match.group(0))
            i += len(match.group(0))
        elif input_string[i] in ' \n':
            # Found whitespace or newline, add it as a separate chunk
            chunks.append(input_string[i])
            i += 1
        else:
            # Found normal text
            start = i
            while i < len(input_string) and input_string[i] not in ' \n' and not re.match(color_code_regex, input_string[i:]):
                i += 1
            chunks.append(input_string[start:i])

    # Now we have a list of chunks, which could be either color codes or regular text.
    output = ''
    line_length = 0
    #print(chunks)
    for chunk in chunks:
        #print(repr(chunk))
        # If it's a color code, we don't add its length to the line length but just append it
        if chunk.startswith('@'):
            word_length = 0
            _chunk = chunk
            for col in colors:
                _chunk = _chunk.replace(col,'')
            word_length = len(_chunk)
            #print(repr(chunk))
            #word_length = len(chunk) - len(colors.get(chunk, ''))  # Subtract the length of the color code itself
        elif chunk == '\n':
            word_length = 0
        else:
            # Normal word length is just the length of the word
            word_length = len(chunk)

        if chunk == '\n':
            #print('RESET CHUNJ')
            #output += str('R'*(max_width-(line_length+word_length)))
            line_length = 0
            

        # Check if the word fits in the current line
        if line_length + word_length > max_width:
            # If it doesn't, add a line break
            #print('NEW LINE')
            #output += str('N'*(max_width-(line_length)))
            output += '\n'
            line_length = 0  # Reset line length

        # Add the chunk (whether it's a color code or normal text) to the output
        output += chunk
        line_length += word_length
    return output

def add_line_breaks(input_string, max_width=100):
    output = ''
    lines = input_string.split('\n')
    for l in lines:
        if len(remove_color(l)) >= max_width:
            output += chunkate(l)+'\n'
        else:
            output += l+'\n'
    return output

def indent(line, indent: IndentType):
    _indent = ''
    match indent:
        case IndentType.NONE:
            pass
        case IndentType.MINOR:
            _indent = '> '
        case IndentType.MAJOR:
            _indent = '>> '
    return (_indent) + line
        
# returns the topmost parent class name
def get_object_parent(obj):
    parent = obj.__class__.__mro__[-2].__name__
    return parent

def progress_bar(size, cur_value, max_value, color = '@white', style=0):
    start = '['
    end = ']'

    bg_color = '@bg'+color[1::]
    
    if max_value == 0:
        percentage = 0
    elif max_value == cur_value:
        percentage = 100
    else:
        percentage = int((cur_value / max_value) * 100)



    match style:
        case 0:
            percentage_text = f'{percentage}%'
        case 1:
            percentage_text = f'{cur_value}/{max_value}'

    percentage_size = len(percentage_text)


    size -= percentage_size

    if max_value == 0:
        scaled_size = 0
    elif max_value == cur_value:
        scaled_size = size + percentage_size
    else:
        scaled_size = round((cur_value / max_value) * size) 


    #output = ' '*(scaled_size+remaining_size)
    #output = bg_color + output
    

    #output = '#'*scaled_size 
    #output = output + '.'*(size-scaled_size)
    output = ' '*(size)
    output = output[:round(size/2)] + percentage_text + output[round(size/2):]
    #print(len(output))
    output = output
    scaled_size += round(percentage_size/2) 
    if percentage == 0:
        scaled_size = 0
    if percentage >= 100:
        scaled_size += round(percentage_size/2) 

    output = bg_color + output[:scaled_size] + '@normal' + output[scaled_size:] 
    
    #output = bg_color + output[:scaled_size-int(percentage_size/2)] + color + output[scaled_size-int(percentage_size/2):] 
    #output = bg_color + output
    
    '''

    output = ('#'*scaled_size) + (','*(size-scaled_size)) 
    middle = math.ceil(len(output)/2)
    output = output[:middle] + percentage_text + output[middle:]
    output = bg_color + output
    output = output[:scaled_size+len(bg_color)] + color + output[scaled_size+len(bg_color):] 
    #output = output[:len(bg_color)+scaled_size] + color
    '''

    output = f'@normal[{output}@normal]'

    #output = '.'*(scaled_size+remaining_size) + percentage_text
    #output = output[int(len(output)):] + percentage_text  
    #output = output[:scaled_size] + color + output[scaled_size:]
    #output = '['+bg_color + output + '@normal]'

    #output = start + bg_color + (' '*scaled_size) + color + (' '*remaining_size) + '@normal' + end

    return output

'''
import random
for i in range(0,101):
    col = random.choice('@red @green @cyan @yellow'.split())
    print(add_color(progress_bar(8,i,100,col)))
'''


if __name__ == '__main__':
    
    line = '@reda@backb@redhello@greenchat@backwhatsup'
    print(add_color(line))

    input_string = "This this is a test @redtest\n of the line breaking @greenwith\n color and @back new ttt lines wo. This is a test @redtest of the line breaking @greenwith color and @back new lines. This is a test @redtest of"
    formatted_string = add_color(add_line_breaks(input_string))

    print(formatted_string)
    strings = formatted_string.split('\n')
    for s in strings:
        print(len(s))


                


