
#!/usr/bin/env python3
from http import server
import ssl

class MyHTTPRequestHandler(server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        super().end_headers()


if __name__ == "__main__":
    httpd = server.ThreadingHTTPServer(
        ("0.0.0.0", 8000),
        MyHTTPRequestHandler
    )

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("cert.pem", "key.pem")

    httpd.socket = context.wrap_socket(
        httpd.socket,
        server_side=True
    )

    print("HTTPS server running on port 8000")
    httpd.serve_forever()

