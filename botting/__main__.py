'''
import telnetlib3 as telnetlib
import time
import random
HOST = "jorm.kurowski.xyz"
#HOST = "localhost"
PORT = 4001
COMMANDS = [
"guest",

"guest","guest","guest","guest","guest","guest","guest","guest","guest","guest","guest","guest","guest","guest","guest",
"go _",
"set gmcp on",
"set godot on",
"set map on",
"set room on"
"set brief off"
"shout set!"
]
for i in range(0,1000):
    #COMMANDS.append('n')

    #continue
    
    COMMANDS.append('n')
    COMMANDS.append('e')
    COMMANDS.append('s')
    COMMANDS.append('w')
    COMMANDS.append('inv')
    COMMANDS.append('say hello')

    #COMMANDS.append('set log')
    #COMMANDS.append('guest')
    #COMMANDS.append('l')
    
DELAY = 0.1  # seconds between each run

def send_telnet_command():
    try:
        with telnetlib.Telnet(HOST, PORT, timeout=5) as tn:
            for i in COMMANDS:
                time.sleep(DELAY)
                tn.write((i+'\r\n').encode('utf-8'))
            time.sleep(5)
    except Exception as e:
        print(f"Error: {e}")
3
if __name__ == "__main__":
    while True:
        send_telnet_command()
        time.sleep(DELAY)


# seq 100 | xargs -n1 -P100 python3 .
'''
import telnetlib3 as telnetlib
import time
import threading

HOST = "jorm.kurowski.xyz"
# HOST = "localhost"
PORT = 4001

COMMANDS = [
    "guest",
    "guest", "guest", "guest", "guest", "guest", "guest", "guest",
    "guest", "guest", "guest", "guest", "guest", "guest", "guest",
    "go _",
    "set gmcp on",
    "set godot on",
    "set map on",
    "set room on",
    "set brief off",
    "shout set!",
]

for _ in range(1000):
    COMMANDS.append("n")
    COMMANDS.append("e")
    COMMANDS.append("s")
    COMMANDS.append("w")
    COMMANDS.append("inv")
    COMMANDS.append("say hello")

DELAY = 0.1


def reader(tn):
    """Continuously read everything the server sends."""
    try:
        while True:
            data = tn.read_some()

            if not data:
                break

            #print(data.decode("utf-8", errors="replace"), end="", flush=True)

    except Exception as e:
        print(f"\nReader error: {e}")


def send_telnet_command():
    try:
        with telnetlib.Telnet(HOST, PORT, timeout=5) as tn:

            # Start reading immediately.
            reader_thread = threading.Thread(
                target=reader,
                args=(tn,),
                daemon=True,
            )
            reader_thread.start()

            for command in COMMANDS:
                time.sleep(DELAY)

                #print(f">>> {command}")

                tn.write(
                    (command + "\r\n").encode("utf-8")
                )

            # Give the server time to respond.
            time.sleep(5)

    except Exception as e:
        print(f"Connection error: {e}")


if __name__ == "__main__":
    while True:
        send_telnet_command()
        time.sleep(DELAY)
