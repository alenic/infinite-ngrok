from discordwebhook import Discord
import argparse
import subprocess
import time
import json
import os
import signal
from pyngrok import ngrok

with open("ngrok_token.txt", "r") as fp:
    token = fp.readline()

ngrok.set_auth_token(token)

class InfiniteNgrok:
    def __init__(self, discord_webhook, seconds=1800, restart_ngrok=True):
        self.discord_webhook = discord_webhook
        self.seconds = seconds
        self.discord = Discord(url=discord_webhook)
        self.restart_ngrok = restart_ngrok
    
    def start(self):
        
        while True:
            if self.restart_ngrok:
                ssh_tunnel = ngrok.connect(22, "tcp")

            ngrok_info_proc = subprocess.Popen("curl -s localhost:4040/api/tunnels", shell=True, stdout=subprocess.PIPE)
            stdout = ngrok_info_proc.communicate()[0].decode("utf-8")
            if len(stdout) > 0:
                try:
                    json_out = json.loads(stdout)
                    public_url = json_out["tunnels"][0]["public_url"]
                    print(public_url, public_url.split(":"))
                    protocol, public_url, port = public_url.split(":")
                    public_url = public_url[2:]
                    print(public_url, os.getlogin(), port)
                    comment = f"ssh -o TCPKeepAlive=yes {os.getlogin()}@{public_url} -p {port}"
                    print(comment)
                except:
                    comment = "Error to load json"
            else:
                comment = ""

            self.discord.post(content=comment)

            time.sleep(self.seconds)
            ngrok_info_proc.terminate()
            ngrok_info_proc.wait()

            if self.restart_ngrok:
                ngrok.disconnect(ssh_tunnel.public_url)
                time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-wh", "--webhook", type=str)
    parser.add_argument("-s", "--seconds", type=int, default=1800)
    parser.add_argument("--no-restart", action="store_true")
    args = parser.parse_args()

    rc = InfiniteNgrok(args.webhook, seconds=args.seconds, restart_ngrok=not args.no_restart)
    rc.start()
