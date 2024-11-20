from fuzzywuzzy import process

def match_word(word: str, l: list):
    best_match, best_score = process.extractOne(word, l)
    #print(best_match, best_score)
    return best_match

def remove_color(line):
    line = line.replace('@red','')
    line = line.replace('@green','')
    line = line.replace('@brown','')
    line = line.replace('@yellow','')
    line = line.replace('@blue','')
    line = line.replace('@pink','')
    line = line.replace('@cyan','')
    line = line.replace('@gray','')
    line = line.replace('@normal','')
    return line

def add_color(line):
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
    return line