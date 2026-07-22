import telnetlib3 as telnetlib
import time
import random
HOST = "jorm.kurowski.xyz"
#HOST = "localhost"
PORT = 4001
COMMANDS = [
"guest",
"go _",
"set gmcp on",
"set godot on",
"set map on",
"shout set!"
]
for i in range(0,1000):
    COMMANDS.append('stats')
    #COMMANDS.append('e')
    #COMMANDS.append('s')
    #COMMANDS.append('w')
    
DELAY = 0.2  # seconds between each run

def send_telnet_command():
    try:
        with telnetlib.Telnet(HOST, PORT, timeout=5) as tn:
            for i in COMMANDS:
                time.sleep(3)
                tn.write(i.encode('utf-8'))
            time.sleep(3)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    while True:
        send_telnet_command()
        time.sleep(DELAY)


# seq 100 | xargs -n1 -P100 python3 .