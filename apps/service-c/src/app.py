from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

SERVICE = os.getenv("SERVICE_NAME", "service-a")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body = {"status": "healthy", "service": SERVICE}
            self.send_response(200)
        else:
            body = {
                "service": SERVICE,
                "message": "Kubernetes GitOps Platform"
            }
            self.send_response(200)

        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

server = HTTPServer(("0.0.0.0", 8080), Handler)
server.serve_forever()