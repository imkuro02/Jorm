import asyncio
import websockets
import telnetlib3

# Configuration
MUD_SERVER = "127.0.0.1"  # Replace with your MUD server address
MUD_PORT = 4001                       # Standard Telnet port
WEBSOCKET_PORT = 8001               # Port for the WebSocket server

async def handle_websocket(websocket):
    # Connect to the Telnet server
    reader, writer = await telnetlib3.open_connection(MUD_SERVER, MUD_PORT)
    
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
    # Start the WebSocket server
    print(f"WebSocket server running on ws://0.0.0.0:{WEBSOCKET_PORT}")
    async with websockets.serve(handle_websocket, "0.0.0.0", WEBSOCKET_PORT):
        await asyncio.Future()  # Keep the server running indefinitely

if __name__ == "__main__":
    asyncio.run(main())
