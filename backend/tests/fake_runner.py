"""Stand-in for game_runner.py so the API can be tested without pygame.
Sends a 'frame' every 50 ms and echoes every input line it receives as a frame."""
import struct
import sys
import threading
import time

out = sys.stdout.buffer
lock = threading.Lock()


def send(payload):
    data = b"\xff\xd8" + payload
    with lock:
        out.write(struct.pack(">I", len(data)) + data)
        out.flush()


def reader():
    for line in sys.stdin:
        send(b"ECHO:" + line.strip().encode())
    import os
    os._exit(0)


threading.Thread(target=reader, daemon=True).start()
while True:
    send(b"tick")
    time.sleep(0.05)
