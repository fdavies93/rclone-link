from asyncio.subprocess import PIPE
from cgi import test
from io import FileIO
import sys
import subprocess
import time
import asyncio

config_top = [{
    "local": "/home/frank/Documents/rclone-test/",
    "remote": "GDrive:rclone-test",
    "poll_time": 60.0, # maximum time between syncs if no changes recorded (mostly downloads from cloud source)
    "cooldown_time": 10.0 # minimum time between syncs on change
}] 
# list of settings objects

async def setup_pipes(config):
    source = config[0]
    local = source["local"]

    pipe = await asyncio.create_subprocess_shell(f"inotifywait --recursive --monitor --event modify --event create --event delete --event move --format '%w%f' {local}", stdout=asyncio.subprocess.PIPE)
    # pipe = subprocess.Popen(["inotifywait","--recursive","--monitor","--event", "modify", "--event", "create", "--event", "delete", "--event", "move", "--format", '%w%f', local], stdout=PIPE)
    return pipe

async def main():
    test_pipe = await setup_pipes(config_top)
    last_sync = 0
    config = config_top[0]
    while True:
        
        try:
            ln = await test_pipe.stdout.readline()
            
            print(ln.decode()[:-1])

            if time.time() - last_sync > config["cooldown_time"]:
                subprocess.run(["rclone", "sync", config["local"], config["remote"], "--verbose"])
                last_sync = time.time()
        
        except asyncio.TimeoutError:
            # do bisync
            pass

        # ln : bytes = test_pipe.stdout.readline()
        # print (ln.decode()[:-1])

# subprocess.call() # call inotifywait to set up the sync
# subprocess.call() # call rclone sync

if __name__ == "__main__":
    asyncio.run(main())