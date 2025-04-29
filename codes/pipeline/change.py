"""
This file sets up a WebSocket server to monitor file changes and send updates to connected clients.
"""
import time
import json
import threading
import asyncio
import websockets
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import queue
import difflib
from pathlib import Path

class MyHandler(FileSystemEventHandler):
    """
    MyHandler is a custom event handler class for monitoring file system changes and processing modifications to a specific file.
    """

    def __init__(self, websocket, message_queue):
        super().__init__()
        self.websocket = websocket
        self.message_queue = message_queue  # Queue to pass messages to the main async loop
        self.previous_content = ""

    def on_modified(self, event):
        """
         Handles the event when a monitored file is modified. Reads the file, computes the diff, and sends the diff through the message queue.
        """
        event_data = {
            "type": "agents",
            "response": f'Event type: {event.event_type} path: {event.src_path}'
        }
        print(f'event type: {event.event_type} path : {event.src_path}')
        if(Path(event.src_path) == Path("./ProcessLogs.md")):
            print(f'Running')
            with open("ProcessLogs.md", 'r') as file:
                current_content = file.read()

            diff = difflib.unified_diff(
                self.previous_content.splitlines(keepends=True),
                current_content.splitlines(keepends=True),
                lineterm=''
            )

            diff_text = ''.join(diff)

            if diff_text:
                event_data = {
                    "type": "agents",
                    "response": diff_text
                }
                self.message_queue.put(event_data)

            self.previous_content = current_content

    def  on_created(self,  event):
        """
         Handles the event when a new file is created. Prints the event type and path.
        """
        print(f'event type: {event.event_type} path : {event.src_path}')

    def  on_deleted(self,  event):
        """
         Handles the event when a file is deleted. Prints the event type and path.
        """
        print(f'event type: {event.event_type} path : {event.src_path}')


async def handle_connection(websocket):
    """
    Handle the WebSocket connection with the client.
    Args:
        websocket (websockets.WebSocketServerProtocol): The WebSocket connection to the client.
    Raises:
        websockets.exceptions.ConnectionClosed: If the client connection is closed.
        Exception: For any other errors that occur during connection handling.
    """

    message_queue = queue.Queue()
    async def process_events():
        while True:
            if not message_queue.empty():
                print("Sending event data to client")
                event_data = message_queue.get()
                
                asyncio.run_coroutine_threadsafe(
                    websocket.send(json.dumps(event_data)),
                    asyncio.get_event_loop()
                )
            await asyncio.sleep(0.5)

    try:
        observer_thread = threading.Thread(target=start_observer, args=(websocket, message_queue), daemon=True)
        observer_thread.start()
        await process_events()
    except websockets.exceptions.ConnectionClosed:
        print("Client connection closed")
    except Exception as e:
        print(f"Error handling connection: {e}")

async def main():
    print("WebSocket server starting on ws://0.0.0.0:8090")
    async with websockets.serve(handle_connection, "localhost", 8090):
        await asyncio.Future() 

def start_observer(websocket, message_queue):
    """
    Starts a file system observer to monitor changes in the current directory.
    Args:
        websocket: The websocket connection to send messages to.
        message_queue: The queue to store messages for processing.
    Raises:
        KeyboardInterrupt: If the observer is manually stopped by a keyboard interrupt.
    """
    event_handler = MyHandler(websocket, message_queue)
    observer = Observer()
    observer.schedule(event_handler,  path='.',  recursive=False)
    observer.start()

    try:
        while  True:
            time.sleep(0.5)
    except  KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutdown by user")