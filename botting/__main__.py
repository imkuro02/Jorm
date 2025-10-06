import telnetlib
import time
import random
HOST = "localhost"
PORT = 4001
COMMANDS = [
"login",
"kuro",
"i love soup",
"say test",
"w","w","w","w","w","w","w","w","w","w","w","w"
]
DELAY = 0.2  # seconds between each run

def send_telnet_command():
    try:
        with telnetlib.Telnet(HOST, PORT, timeout=5) as tn:
            for i in COMMANDS:
                time.sleep(random.randint(100,900)/1000)
                tn.write(i.encode('utf-8'))
            time.sleep(random.randint(100,900)/1000)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    while True:
        send_telnet_command()
        time.sleep(DELAY)