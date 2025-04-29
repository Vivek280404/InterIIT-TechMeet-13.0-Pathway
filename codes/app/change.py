# import time
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# import websockets
# import asyncio

# class  MyHandler(FileSystemEventHandler):
#     def  on_modified(self,  event):
#         # print(f'event type: {event.event_type} path : {event.src_path}')
#         event_data = {
#         "type": "agents",
#         "response": f'Event type: {event.event_type} path: {event.src_path}'
#     }
#         if(event.src_path == ".\ProcessLogs.md"):
#             print(f'Pizza lelo')
#             print(f'event type: {event.event_type} path : {event.src_path}')
#             # self.websocket.send(json.dumps(event_data))
#             # self.message_queue.put(event_data)
#     def  on_created(self,  event):
#         print(f'event type: {event.event_type} path : {event.src_path}')
#     def  on_deleted(self,  event):
#         print(f'event type: {event.event_type} path : {event.src_path}')

# if __name__ ==  "__main__":
#     event_handler = MyHandler()
#     observer = Observer()
#     observer.schedule(event_handler,  path='.',  recursive=False)
#     observer.start()

#     try:
#         while  True:
#             time.sleep(0.5)
#     except  KeyboardInterrupt:
#         observer.stop()
#     observer.join()

import os
import time
import json
import threading
import asyncio
import websockets

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import queue



class MyHandler(FileSystemEventHandler):
    def __init__(self, websocket, message_queue):
        super().__init__()
        self.websocket = websocket
        self.message_queue = message_queue  # Queue to pass messages to the main async loop

    def on_modified(self, event):
        # Generate event details
        event_data = {
            "type": "agents",
            "response": f'Event type: {event.event_type} path: {event.src_path}'
        }
        print(f'event type: {event.event_type} path : {event.src_path}')
        if(event.src_path == ".\ProcessLogs.md"):
            print(f'Pizza lelo')
            # self.websocket.send(json.dumps(event_data))
            text = open("ProcessLogs.md", 'r').read()
            event_data = {
                "type": "agents",
                "response": text
            }
            # with open("ProcessLogs.md", 'r') as f:
            #     f.read()
            self.message_queue.put(event_data)

    def  on_created(self,  event):
         print(f'event type: {event.event_type} path : {event.src_path}')
    def  on_deleted(self,  event):
         print(f'event type: {event.event_type} path : {event.src_path}')


async def handle_connection(websocket):
    message_queue = queue.Queue()
    async def process_events():
        while True:
            if not message_queue.empty():
                print("Sending event data to client")
                event_data = message_queue.get()
                
                # Schedule the send operation on the main event loop
                asyncio.run_coroutine_threadsafe(
                    websocket.send(json.dumps(event_data)),
                    asyncio.get_event_loop()
                )
            await asyncio.sleep(0.5)  # Prevent busy-waiting

    def run_process_events_in_thread():
        # Run the asyncio loop for process_events in a new thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_events())
    try:
        observer_thread = threading.Thread(target=start_observer, args=(websocket, message_queue), daemon=True)
        observer_thread.start()
        # event_task = asyncio.create_task(process_events())
        # events_thread = threading.Thread(target=run_process_events_in_thread, daemon=True)
        # events_thread.start()
        await process_events()
    except websockets.exceptions.ConnectionClosed:
        print("Client connection closed")
    except Exception as e:
        print(f"Error handling connection: {e}")
    # finally:
    #     # Cancel the event task if the WebSocket connection closes
    #     event_task.cancel()
    #     await event_task

async def main():
    print("WebSocket server starting on ws://0.0.0.0:8090")
    async with websockets.serve(handle_connection, "localhost", 8090):
        await asyncio.Future()  # run forever

def start_observer(websocket, message_queue):
    event_handler = MyHandler(websocket, message_queue)
    observer = Observer()
    observer.schedule(event_handler,  path='.',  recursive=False)
    observer.start()

    try:
        while  True:
            time.sleep(0.5)
            # print("Running")
    except  KeyboardInterrupt:
        observer.stop()
    observer.join()




if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutdown by user")