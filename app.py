from asyncio.subprocess import PIPE
import time
import asyncio

config_top = [{
    "local": "/home/frank/Documents/rclone-test/",
    "remote": "GDrive:rclone-test",
    "poll_time": 20.0, # maximum time between syncs if no changes recorded (mostly downloads from cloud source)
    "cooldown_time": 10.0 # minimum time between syncs on change
},
{
    "local": "/home/frank/Documents/obsidian/",
    "remote": "GDrive:Obsidian",
    "poll_time": 60.0, # maximum time between syncs if no changes recorded (mostly downloads from cloud source)
    "cooldown_time": 10.0 # minimum time between syncs on change
}] 
# list of settings objects

async def setup_pipe(source):
    local = source["local"]

    pipe = await asyncio.create_subprocess_shell(f"inotifywait --recursive --monitor --event modify --event create --event delete --event move --format '%w%f' {local}", stdout=asyncio.subprocess.PIPE)
    return pipe

async def monitor(config):
    test_pipe = await setup_pipe(config)
    last_sync = 0
    print(f"Watching {config['local']} for changes.")
    while True:
        try:
            ln = await asyncio.wait_for( test_pipe.stdout.readline(), config["poll_time"] )

            if time.time() - last_sync > config["cooldown_time"]:
                print(f"Updating remote {config['remote']} from changed local directory {config['local']}.")
                await asyncio.create_subprocess_shell(f"rclone sync {config['local']} {config['remote']} --quiet")
                print(f"Update complete.")
        
        except asyncio.TimeoutError:
            # do bisync
            print(f"Synchronising local {config['local']} and remote {config['remote']}.")
            await asyncio.create_subprocess_shell(f"rclone bisync {config['local']} {config['remote']} --quiet --resync")
            print("Sync complete.")
        
        last_sync = time.time()

async def main():
    await asyncio.gather(*[monitor(config) for config in config_top], return_exceptions=False)

if __name__ == "__main__":
    asyncio.run(main())