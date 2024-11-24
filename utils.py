from fuzzywuzzy import process

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

def match_word(word: str, l: list):
    best_match, best_score = process.extractOne(word, l)
    #print(best_match, best_score)
    return best_match
    

def match_word_get_list(word: str, l: list):
    
    matches = process.extract(word, l, limit=None)
    best_matches = [match for match in matches]
    return best_matches
    
def match_word_indexed(word: str, l: dict):
    process.extract(target, my_list, limit=5)
 

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