# run.py  (replace whole file)
from app import create_app
import socket

def find_open_port(start=5100, end=5200):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No open ports found in 5100-5200")

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

app = create_app()

if __name__ == "__main__":
    port = find_open_port()
    print(f"\n🚀 Leaky Meatbag running – open http://127.0.0.1:{port}  "
          f"or http://{get_local_ip()}:{port}\n")
    app.run(host="0.0.0.0", port=port)
