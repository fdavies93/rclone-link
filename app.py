from asyncio.subprocess import PIPE
import time
import asyncio
import datetime
from enum import IntEnum

sources = [{
    "label": "Code Notes",
    "local": "/home/frank/code/notes/",
    "remote": "GDrive:code-notes",
    "poll_time": 20.0, # maximum time between syncs if no changes recorded (mostly downloads from cloud source)
    "cooldown_time": 15.0 # minimum time between syncs on change
},
{
    "label": "Obsidian",
    "local": "/home/frank/Documents/obsidian/",
    "remote": "GDrive:Obsidian",
    "poll_time": 20.0, # maximum time between syncs if no changes recorded (mostly downloads from cloud source)
    "cooldown_time": 15.0 # minimum time between syncs on change
}] 
# list of settings objects

class SYNC_MODE(IntEnum):
    NONE = 0
    PUSH = 1 # push local directory to remote, overwriting remote
    SYNC = 2 # try to merge local and remote, preserving changes to both
    PULL = 3 # pull remote to local directory, overwriting local (this seems rare)

def timestamp():
    cur_time = time.time()
    time_label = datetime.datetime.fromtimestamp(cur_time).strftime("%Y-%m-%d %H:%M:%S")
    return time_label

async def push(config):
    label = config["label"]

    print(f"[{label} | {timestamp()}] Pushing local {config['local']} to remote {config['remote']}.")
    await asyncio.create_subprocess_shell(f"rclone sync {config['local']} {config['remote']} --quiet")

    print(f"[{label} | {timestamp()}] Push complete.")

async def pull(config):
    label = config["label"]

    print(f"[{label} | {timestamp()}] Pulling from remote {config['remote']} to local {config['local']}.")
    await asyncio.create_subprocess_shell(f"rclone sync {config['remote']} {config['local']} --quiet")

    print(f"[{label} | {timestamp()}] Pull complete.")

async def sync(config):
    label = config["label"]

    print(f"[{label} | {timestamp()}] Synching local {config['local']} and remote {config['remote']}.")
    await asyncio.create_subprocess_shell(f"rclone bisync {config['local']} {config['remote']} --quiet --resync")

    print(f"[{label} | {timestamp()}] Sync complete.")

async def setup_pipe(source):
    local = source["local"]

    pipe = await asyncio.create_subprocess_shell(f"inotifywait --quiet --recursive --monitor --event modify --event create --event delete --event move --format '%w%f' {local}", stdout=asyncio.subprocess.PIPE)
    return pipe

async def monitor(config):
    test_pipe = await setup_pipe(config)
    last_sync = 0
    label = config["label"]
    next_wait = config["poll_time"]

    mode : SYNC_MODE = SYNC_MODE.PULL
    
    last_sync = time.time()

    print(f"[{label} | {timestamp()}] Watching {config['local']} for changes.")
    while True:
        try:
            next_wait = config["poll_time"] - (time.time() - last_sync)

            if next_wait > 0:
                ln = await asyncio.wait_for( test_pipe.stdout.readline(), next_wait )
                # if we never reach here (no local changes since last sync), it will pull from remote
                # if we do reach here (local changes since last sync), it will push to remote
                mode = SYNC_MODE.PUSH
        
        except asyncio.TimeoutError:
            # leave this block to make it a bit clearer what's happening
            # / add possible trigger events later 
            if mode == SYNC_MODE.PULL:
                await pull(config)
            elif mode == SYNC_MODE.PUSH:
                await push(config)

            mode = SYNC_MODE.PULL
            last_sync = time.time()

async def main():
    await asyncio.gather(*[monitor(config) for config in sources], return_exceptions=False)

if __name__ == "__main__":
    asyncio.run(main())