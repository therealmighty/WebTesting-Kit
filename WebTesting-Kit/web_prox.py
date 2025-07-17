import socket
import threading
import select
import sys
import re # For simple URL parsing

# --- Configuration ---
# Default host and port for the proxy to listen on
DEFAULT_PROXY_HOST = '127.0.0.1'
DEFAULT_PROXY_PORT = 8888
BUFFER_SIZE = 4096 # Size of the buffer for sending/receiving data

# --- Helper Function for Handling Client Connections ---
def handle_client(client_socket, client_address):
    """
    Handles a single client connection to the proxy.
    It receives the client's request, parses it to determine the target server,
    forwards the request, and then relays the response back to the client.
    """
    try:
        # Receive the client's request
        request = client_socket.recv(BUFFER_SIZE)
        if not request:
            return # No data received, close connection

        # Decode the request to a string to parse HTTP headers
        first_line = request.split(b'\n')[0].decode('latin-1')
        
        # Use regex to extract the method, URL, and HTTP version
        # Example: GET http://example.com/path HTTP/1.1
        match = re.match(r"([A-Z]+)\s+(.+?)\s+(HTTP/\d\.\d)", first_line)
        
        if not match:
            print(f"[{client_address[0]}:{client_address[1]}] Invalid request line: {first_line}")
            client_socket.close()
            return

        method, url, http_version = match.groups()
        print(f"[{client_address[0]}:{client_address[1]}] Request: {method} {url}")

        # Parse the URL to get host and port
        # For HTTP, default port is 80. For HTTPS, it's 443 (though this basic proxy won't handle CONNECT for HTTPS)
        target_host = ""
        target_port = 80
        
        # Extract host from URL
        if url.startswith("http://"):
            url_parts = url[7:].split('/', 1)
            target_host = url_parts[0]
            if ':' in target_host:
                target_host, port_str = target_host.split(':')
                try:
                    target_port = int(port_str)
                except ValueError:
                    pass # Keep default 80 if port is invalid
        else:
            # If it's not a full URL (e.g., for direct proxy requests like "GET /path HTTP/1.1" with Host header)
            # Find the Host header
            for line in request.split(b'\n'):
                if line.lower().startswith(b'host:'):
                    target_host = line[5:].strip().decode('latin-1').split(':')[0]
                    if ':' in line.decode('latin-1'):
                        try:
                            target_port = int(line.decode('latin-1').split(':')[1])
                        except ValueError:
                            pass
                    break
            if not target_host:
                print(f"[{client_address[0]}:{client_address[1]}] Could not determine target host from request.")
                client_socket.close()
                return

        # Create a socket to connect to the target server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.settimeout(5) # Set a timeout for connecting to the target server

        try:
            server_socket.connect((target_host, target_port))
            # Send the original request to the target server
            server_socket.sendall(request)
        except socket.gaierror:
            print(f"[{client_address[0]}:{client_address[1]}] Could not resolve target host: {target_host}")
            client_socket.close()
            server_socket.close()
            return
        except socket.error as e:
            print(f"[{client_address[0]}:{client_address[1]}] Error connecting to target {target_host}:{target_port}: {e}")
            client_socket.close()
            server_socket.close()
            return

        # --- Relay Data Between Client and Server ---
        # This loop continuously relays data until one side closes the connection
        while True:
            # Use select to wait for data on either socket
            rlist, _, _ = select.select([client_socket, server_socket], [], [], 1) # 1 second timeout

            if client_socket in rlist:
                # Data from client to server
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break # Client closed connection
                server_socket.sendall(data)

            if server_socket in rlist:
                # Data from server to client
                data = server_socket.recv(BUFFER_SIZE)
                if not data:
                    break # Server closed connection
                client_socket.sendall(data)

    except Exception as e:
        print(f"[{client_address[0]}:{client_address[1]}] An error occurred: {e}")
    finally:
        # Ensure both sockets are closed
        if 'client_socket' in locals() and client_socket:
            client_socket.close()
        if 'server_socket' in locals() and server_socket:
            server_socket.close()
        # print(f"[{client_address[0]}:{client_address[1]}] Connection closed.")


# --- Main Proxy Server Function ---
def run_web_proxy():
    """
    Initializes and runs the basic HTTP proxy server.
    """
    print("--- Basic HTTP Proxy Server ---")
    print(f"Proxy will listen on {DEFAULT_PROXY_HOST}:{DEFAULT_PROXY_PORT}")
    print("This proxy only supports HTTP (not HTTPS 'CONNECT' method).")
    print("Configure your browser to use this proxy (e.g., 127.0.0.1:8888).\n")

    try:
        # Create the main proxy listening socket
        proxy_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reusing the address immediately after closing
        proxy_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_server_socket.bind((DEFAULT_PROXY_HOST, DEFAULT_PROXY_PORT))
        proxy_server_socket.listen(5) # Max 5 pending connections
        print(f"Proxy server listening on {DEFAULT_PROXY_HOST}:{DEFAULT_PROXY_PORT}...")

        while True:
            # Accept incoming client connections
            client_socket, client_address = proxy_server_socket.accept()
            print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
            # Handle each client connection in a new thread
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.daemon = True # Allow main program to exit even if threads are running
            client_handler.start()

    except KeyboardInterrupt:
        print("\nProxy server shutting down...")
    except Exception as e:
        print(f"Error starting proxy server: {e}")
    finally:
        if 'proxy_server_socket' in locals() and proxy_server_socket:
            proxy_server_socket.close()
            print("Proxy server socket closed.")

# Entry point for the script
if __name__ == "__main__":
    run_web_proxy()
