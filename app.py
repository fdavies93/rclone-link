from asyncio.subprocess import PIPE
import time
import asyncio
import datetime
from enum import IntEnum

sources = [{
    "label": "Test",
    "local": "/home/frank/Documents/rclone-test/",
    "remote": "GDrive:rclone-test",
    "poll_time": 60.0, # maximum time between syncs if no changes recorded (mostly downloads from cloud source)
    "cooldown_time": 15.0 # minimum time between syncs on change
},
{
    "label": "Obsidian",
    "local": "/home/frank/Documents/obsidian/",
    "remote": "GDrive:Obsidian",
    "poll_time": 60.0, # maximum time between syncs if no changes recorded (mostly downloads from cloud source)
    "cooldown_time": 15.0 # minimum time between syncs on change
}] 
# list of settings objects

class SYNC_MODE(IntEnum):
    NONE = 0
    UPDATE = 1 # push local directory to remote, overwriting remote
    SYNC = 2 # try to merge local and remote, preserving changes to both

async def setup_pipe(source):
    local = source["local"]

    pipe = await asyncio.create_subprocess_shell(f"inotifywait --quiet --recursive --monitor --event modify --event create --event delete --event move --format '%w%f' {local}", stdout=asyncio.subprocess.PIPE)
    return pipe

async def monitor(config):
    test_pipe = await setup_pipe(config)
    last_sync = 0
    label = config["label"]
    next_wait = config["poll_time"]
    cur_time = time.time()
    time_label = datetime.datetime.fromtimestamp(cur_time).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{label} | {time_label}] Watching {config['local']} for changes.")
    while True:
        try:
            ln = await asyncio.wait_for( test_pipe.stdout.readline(), next_wait )
            cur_time = time.time()
            time_label = datetime.datetime.fromtimestamp(cur_time).strftime("%Y-%m-%d %H:%M:%S")
            if cur_time - last_sync > config["cooldown_time"]:
                print(f"[{label} | {time_label}] Updating remote {config['remote']} from changed local directory {config['local']}.")
                await asyncio.create_subprocess_shell(f"rclone sync {config['local']} {config['remote']} --quiet")
                print(f"[{label} | {time_label}] Update complete.")
                last_sync = time.time()
            else:
                next_wait = config["cooldown_time"] - (cur_time - last_sync) # wait for cooldown to expire then do a sync
                print(f"[{label} | {time_label}] Waiting for {round(next_wait, 2)} seconds for cooldown to end.")
        
        except asyncio.TimeoutError:
            # do bisync
            cur_time = time.time()
            time_label = datetime.datetime.fromtimestamp(cur_time).strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{label} | {time_label}] Synchronising local {config['local']} and remote {config['remote']}.")
            await asyncio.create_subprocess_shell(f"rclone bisync {config['local']} {config['remote']} --quiet --resync")
            print(f"[{label} | {time_label}] Sync complete.")
            next_wait = config["poll_time"]
            last_sync = time.time()
        

async def main():
    await asyncio.gather(*[monitor(config) for config in sources], return_exceptions=False)

if __name__ == "__main__":
    asyncio.run(main())