import subprocess
import time
import re
import sys
import os

CLOUDFLARED_BIN = r"C:\Users\dell\cloudflared.exe"

def run_tunnel():
    if not os.path.exists(CLOUDFLARED_BIN):
        print(f"Error: cloudflared not found at {CLOUDFLARED_BIN}")
        sys.exit(1)

    print("🌐 Connecting CareerBridge AI to public internet via Cloudflare Tunnel...")
    cmd = [CLOUDFLARED_BIN, "tunnel", "--url", "http://127.0.0.1:8000"]
    
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    tunnel_url = None
    for line in proc.stderr:
        print(line, end="")
        match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if match:
            tunnel_url = match.group(0)
            print("\n" + "="*70)
            print("🚀 CAREERBRIDGE AI ĐÃ ĐƯỢC DEPLOY ONLINE THÀNH CÔNG!")
            print(f"🔗 URL TRUY CẬP CÔNG KHAI (PUBLIC URL): {tunnel_url}")
            print("="*70 + "\n")
            with open("public_url.txt", "w", encoding="utf-8") as f:
                f.write(tunnel_url)
            break

    # Keep tunnel alive
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()

if __name__ == "__main__":
    run_tunnel()
