import asyncio
import websockets
import ssl
from contextlib import AsyncExitStack

# Configuration
MUD_SERVER = "127.0.0.1"      # MUD server address
MUD_PORT = 4001               # Telnet port (raw TCP)
WEBSOCKET_PORT = 8001         # WebSocket port
SSL_CERT_FILE = "../server/server.crt"  # SSL certificate
SSL_KEY_FILE = "../server/server.key"   # SSL private key

async def handle_websocket(websocket):
    try:
        # Connect to MUD server via raw TCP
        reader, writer = await asyncio.open_connection(MUD_SERVER, MUD_PORT)

        async def relay_from_mud():
            try:
                while True:
                    data = await reader.read(1024*32)
                    if not data:
                        break
                    # Send as binary to preserve all byte sequences
                    await websocket.send(data)
            except Exception as e:
                print(f"Error reading from MUD: {e}")
            finally:
                await websocket.close()

        async def relay_to_mud():
            try:
                async for message in websocket:
                    if isinstance(message, str):
                        message = message.encode('utf-8') + b'\n'
                    writer.write(message)
                    await writer.drain()
            except Exception as e:
                print(f"Error writing to MUD: {e}")
            finally:
                writer.close()
                await writer.wait_closed()

        await asyncio.gather(relay_from_mud(), relay_to_mud())

    except Exception as e:
        print(f"Connection error: {e}")
        await websocket.close()

async def main():
    # SSL setup
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=SSL_CERT_FILE, keyfile=SSL_KEY_FILE)

    print(f"WebSocket server running on wss://0.0.0.0:{WEBSOCKET_PORT}")
    #async with websockets.serve(handle_websocket, "0.0.0.0", WEBSOCKET_PORT):

    #async with websockets.serve(handle_websocket, "0.0.0.0", WEBSOCKET_PORT, ssl=ssl_context):
    #    await asyncio.Future()  # run forever

    async with AsyncExitStack() as stack:
        await stack.enter_async_context(websockets.serve(handle_websocket, "0.0.0.0", WEBSOCKET_PORT + 1))  # plain
        await stack.enter_async_context(websockets.serve(handle_websocket, "0.0.0.0", WEBSOCKET_PORT, ssl=ssl_context))  # SSL

        print(f"Servers running on ports {WEBSOCKET_PORT} (wss) and {WEBSOCKET_PORT + 1} (ws)")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
