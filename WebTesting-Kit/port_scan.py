import socket
import threading
import time

# --- Configuration ---
# Default target host and port range for scanning
DEFAULT_TARGET_HOST = "scanme.nmap.org" # A legal target provided by Nmap for testing
DEFAULT_START_PORT = 1
DEFAULT_END_PORT = 1000
DEFAULT_TIMEOUT = 1.0 # seconds

# --- Helper Function for Single Port Scan ---
def scan_port(host, port, timeout, open_ports):
    """
    Attempts to connect to a single port on the target host.
    If successful, the port is considered open and added to the list.
    """
    try:
        # Create a new socket. AF_INET for IPv4, SOCK_STREAM for TCP.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set a timeout for the connection attempt. This prevents the script
        # from hanging indefinitely on filtered or closed ports.
        s.settimeout(timeout)

        # Attempt to connect to the host and port.
        # connect_ex() returns 0 if successful, otherwise an error code.
        result = s.connect_ex((host, port))

        if result == 0:
            # If connect_ex returns 0, the connection was successful, meaning the port is open.
            print(f"Port {port} is OPEN")
            open_ports.append(port) # Add to the shared list of open ports
        else:
            # For debugging, you could print closed/filtered ports too:
            # print(f"Port {port} is CLOSED/FILTERED (Error: {result})")
            pass # Suppress output for closed/filtered ports for cleaner output

    except socket.gaierror:
        # Handle cases where the hostname cannot be resolved.
        print(f"Hostname '{host}' could not be resolved. Exiting.")
        return
    except socket.error as e:
        # Handle other socket-related errors (e.g., network unreachable).
        print(f"Socket error on port {port}: {e}")
    finally:
        # Ensure the socket is closed after each attempt.
        s.close()

# --- Main Port Scanner Function ---
def run_port_scanner():
    """
    Prompts the user for target details and initiates a multi-threaded port scan.
    """
    print("--- Basic Port Scanner ---")
    print(f"Default target: {DEFAULT_TARGET_HOST}")
    print(f"Default port range: {DEFAULT_START_PORT}-{DEFAULT_END_PORT}")
    print(f"Default timeout per port: {DEFAULT_TIMEOUT} seconds\n")

    target_host = input(f"Enter target host (e.g., {DEFAULT_TARGET_HOST}): ").strip()
    if not target_host:
        target_host = DEFAULT_TARGET_HOST

    try:
        start_port = int(input(f"Enter start port ({DEFAULT_START_PORT}): ") or DEFAULT_START_PORT)
        end_port = int(input(f"Enter end port ({DEFAULT_END_PORT}): ") or DEFAULT_END_PORT)
        scan_timeout = float(input(f"Enter timeout per port in seconds ({DEFAULT_TIMEOUT}): ") or DEFAULT_TIMEOUT)
    except ValueError:
        print("Invalid input for ports or timeout. Using default values.")
        start_port = DEFAULT_START_PORT
        end_port = DEFAULT_END_PORT
        scan_timeout = DEFAULT_TIMEOUT

    print(f"\nScanning {target_host} from port {start_port} to {end_port} with timeout {scan_timeout}s...")

    # List to store open ports found by threads
    open_ports = []
    # List to hold all thread objects
    threads = []

    start_time = time.time()

    # Create and start a thread for each port in the range
    for port in range(start_port, end_port + 1):
        thread = threading.Thread(target=scan_port, args=(target_host, port, scan_timeout, open_ports))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    end_time = time.time()
    duration = end_time - start_time

    print("\n--- Scan Results ---")
    if open_ports:
        print(f"Open ports found on {target_host}: {sorted(open_ports)}")
    else:
        print(f"No open ports found on {target_host} in the range {start_port}-{end_port}.")
    print(f"Scan completed in {duration:.2f} seconds.")

# Entry point for the script
if __name__ == "__main__":
    run_port_scanner()