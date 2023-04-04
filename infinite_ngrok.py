from discordwebhook import Discord
import argparse
import subprocess
import time

class InfiniteNgrok:
    def __init__(self, discord_webhook, seconds=1800, restart_ngrok=True):
        self.discord_webhook = discord_webhook
        self.seconds = seconds
        self.discord = Discord(url=discord_webhook)
        self.restart_ngrok = restart_ngrok
    
    def start(self):
        while True:
            if self.restart_ngrok:
                ngrok_proc = subprocess.Popen("ngrok tcp 22", shell=True)
                time.sleep(5)
            
            ngrok_info_proc = subprocess.Popen("curl -s localhost:4040/api/tunnels", shell=True, stdout=subprocess.PIPE)
            stdout = ngrok_info_proc.communicate()[0].decode("utf-8")
            self.discord.post(content=stdout)

            time.sleep(self.seconds)
            ngrok_info_proc.terminate()
            ngrok_info_proc.wait()

            if self.restart_ngrok:
                ngrok_proc.terminate()
                ngrok_proc.wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-wh", "--webhook", type=str)
    parser.add_argument("-s", "--seconds", type=int, default=1800)
    parser.add_argument("--no-restart", action="store_true")
    args = parser.parse_args()

    rc = InfiniteNgrok(args.webhook, seconds=args.seconds, restart_ngrok=not args.no_restart)
    rc.start()
