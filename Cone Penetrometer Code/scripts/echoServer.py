import http.server
import socketserver

# Define the request handler class
class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Print request line and headers
        print("Received GET request")
        print(f"Path: {self.path}")
        print(f"Headers:\n{self.headers}")
        
        # Send a simple response back to the client
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"GET request received")

    def do_POST(self):
        # Print request line and headers
        print("Received POST request")
        print(f"Path: {self.path}")
        print(f"Headers:\n{self.headers}")

        # Read and print the body of the POST request
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(f"Body:\n{post_data.decode('utf-8')}")
        
        # Send a simple response back to the client
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"POST request received")

# Set the server address and port
HOST = '192.168.235.1'
PORT = 8080

# Create the server
with socketserver.TCPServer((HOST, PORT), RequestHandler) as httpd:
    print(f"Serving HTTP on {HOST} port {PORT} (http://{HOST}:{PORT}/) ...")
    httpd.serve_forever()
