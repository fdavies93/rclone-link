from asyncio.subprocess import PIPE
from io import FileIO
import sys
import subprocess
import time

config_top = [{
    "local": "~/Documents/rclone-test",
    "remote": "GDrive:rclone-test",
    "poll_time": 60.0, # maximum time between syncs if no changes recorded (mostly downloads from cloud source)
    "cooldown_time": 10.0 # minimum time between syncs on change
}] 
# list of settings objects

def setup_pipes(config):
    source = config[0]
    local = source["local"]
    pipe = subprocess.Popen(f"--quiet --recursive --monitor --event modify --format \"%w%f\" { local }", executable="inotifywait", stdout=PIPE)
    return pipe
    # inotifywait --quiet --recursive --monitor --event modify --format "%w%f" /home/frank/Documents/obsidian

def sync():
    pass

def main():
    test_pipe = setup_pipes(config_top)
    while True:
        ln : str = test_pipe.stdout.read()
        if len(ln) > 0:
            print(ln)
    # setup pipe
    # await changes
    # if changes OR poll time is reached, 
    # ignore changes that happen within cooldown period
    pass

# subprocess.call() # call inotifywait to set up the sync
# subprocess.call() # call rclone sync

if __name__ == "__main__":
    main()