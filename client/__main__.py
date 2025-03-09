import asyncio
import websockets
import ssl
import telnetlib3


# Configuration
MUD_SERVER = "127.0.0.1"  # Replace with your MUD server address
MUD_PORT = 4001  # Standard Telnet port
WEBSOCKET_PORT = 8001  # Port for the WebSocket server
SSL_CERT_FILE = "../server/server.crt"  # Path to your SSL certificate file
SSL_KEY_FILE = "../server/server.key"  # Path to your SSL private key file


async def handle_websocket(websocket):
    # Connect to the Telnet server
    reader, writer = await telnetlib3.open_connection(MUD_SERVER, MUD_PORT, encoding='utf8', force_binary=True)
    
    # Handle communication
    async def read_from_telnet():
        try:
            async for line in reader:
                await websocket.send(line)
        except Exception as e:
            print(f"Telnet read error: {e}")
            await websocket.close()

    async def write_to_telnet():
        try:
            async for message in websocket:
                writer.write(message + '\n')
        except Exception as e:
            print(f"WebSocket read error: {e}")
            writer.close()
        finally:
            # Close the MUD connection when the WebSocket connection is closed
            writer.close()

    # Run reading and writing tasks concurrently
    await asyncio.gather(read_from_telnet(), write_to_telnet())

async def main():
    # SSL context setup
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=SSL_CERT_FILE, keyfile=SSL_KEY_FILE)

    # Start the WebSocket server with SSL
    print(f"WebSocket server running on wss://0.0.0.0:{WEBSOCKET_PORT}")
    async with websockets.serve(handle_websocket, "0.0.0.0", WEBSOCKET_PORT):
        await asyncio.Future()  # Keep the server running indefinitely

# Start the server
asyncio.run(main())

