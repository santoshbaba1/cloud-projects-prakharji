#!/usr/bin/env python3
"""A tiny web server using only the Python standard library (no pip install).

It answers every request with the machine's hostname and internal IP so you can
prove which VM served a page. Run it on a VM with:

    sudo python3 hello_server.py

It listens on port 80, which is why it needs sudo. Stop it with Ctrl+C.
"""
import http.server
import socket

PORT = 80


class HelloHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        hostname = socket.gethostname()
        internal_ip = socket.gethostbyname(hostname)
        body = f"Hello from {hostname} ({internal_ip})\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, *args):
        # Keep the console quiet; comment this out to see every request.
        pass


if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), HelloHandler)
    print(f"Serving on port {PORT} — press Ctrl+C to stop")
    server.serve_forever()
