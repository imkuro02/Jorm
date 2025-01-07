# ttyd -p 8080 client.py
# ttyd -t 'theme={"background": "black"}' -p 8080 python3 client.py 
import socket
import threading

# Define the server host and port
SERVER_HOST = '127.0.0.1'  # Localhost (change if you need a different host)
SERVER_PORT = 4001        # Port number

# Function to handle receiving messages
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')  # Receive message from server
            if message:
                print(f"{message}", end='')
            else:
                break  # Server closed the connection
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# Function to handle sending messages
def send_messages(client_socket):
    while True:
        message = input("")
        if message.lower() == 'exit':  # Close the connection if 'exit' is typed
            print("Exiting client...")
            client_socket.close()
            break
        client_socket.send(message.encode('utf-8'))  # Send the message to the server

def main():
    # Set up the TCP client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")

        # Start the thread to receive messages from the server
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.daemon = True  # Daemon thread will exit when the main program exits
        receive_thread.start()

        # Handle sending messages in the main thread
        send_messages(client_socket)
        
    except Exception as e:
        print(f"Error connecting to server: {e}")
    except KeyboardInterrupt:
        client_socket.send('*Interrupt*'.encode('utf-8')) 
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
