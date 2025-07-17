import requests
import os

# --- Configuration ---
# IMPORTANT: Use a known vulnerable test application or a controlled environment.
# DO NOT use this script against live, production websites without explicit permission.
DEFAULT_TARGET_URL = "http://testphp.vulnweb.com/" # Example target URL
DEFAULT_WORDLIST_PATH = "common.txt" # Default wordlist file

# Common HTTP status codes to consider as "found" or "interesting"
# 200 OK: Content found
# 204 No Content: Request successful, but no content to return
# 301 Moved Permanently / 302 Found: Redirection, might indicate existence
# 401 Unauthorized / 403 Forbidden: Resource exists but access is denied, still interesting
INTERESTING_STATUS_CODES = [200, 204, 301, 302, 401, 403]

# --- Main Directory/File Brute-Forcer Function ---
def run_dir_bruteforcer():
    """
    Prompts the user for a target URL and a wordlist, then attempts to
    discover hidden directories and files.
    """
    print("--- Basic Directory/File Brute-Forcer ---")
    print(f"Default target URL: {DEFAULT_TARGET_URL}")
    print(f"Default wordlist: {DEFAULT_WORDLIST_PATH}\n")
    print("WARNING: Only use this script on targets you have explicit permission to test.")
    print("This script can generate a lot of traffic; use responsibly.\n")

    target_url = input(f"Enter target URL (e.g., {DEFAULT_TARGET_URL}): ").strip()
    if not target_url:
        target_url = DEFAULT_TARGET_URL
    
    # Ensure URL ends with a slash for consistent path joining
    if not target_url.endswith('/'):
        target_url += '/'

    wordlist_path = input(f"Enter wordlist path (e.g., {DEFAULT_WORDLIST_PATH}): ").strip()
    if not wordlist_path:
        wordlist_path = DEFAULT_WORDLIST_PATH

    if not os.path.exists(wordlist_path):
        print(f"Error: Wordlist file '{wordlist_path}' not found.")
        print("Please ensure the wordlist exists in the same directory or provide a full path.")
        return

    print(f"\nStarting directory/file brute-force on {target_url} using '{wordlist_path}'...")

    found_items = []
    total_attempts = 0

    try:
        with open(wordlist_path, 'r') as f:
            wordlist = [line.strip() for line in f if line.strip()] # Read and clean each line

        for item in wordlist:
            total_attempts += 1
            test_url = f"{target_url}{item}"
            
            try:
                response = requests.get(test_url, timeout=5) # 5-second timeout per request
                print(f"  Testing: {test_url} -> Status: {response.status_code}")

                if response.status_code in INTERESTING_STATUS_CODES:
                    found_items.append((test_url, response.status_code))
                    print(f"    [+] Found: {test_url} (Status: {response.status_code})")

            except requests.exceptions.ConnectionError:
                print(f"  [!] Connection error to {test_url}. Target might be down or blocked.")
                break # Stop if connection errors occur frequently
            except requests.exceptions.Timeout:
                print(f"  [!] Timeout accessing {test_url}. Skipping.")
            except requests.exceptions.RequestException as e:
                print(f"  [!] An error occurred for {test_url}: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    print("\n--- Brute-Force Scan Summary ---")
    print(f"Total URLs attempted: {total_attempts}")
    if found_items:
        print(f"Found {len(found_items)} interesting items:")
        for url, status in found_items:
            print(f"- {url} (Status: {status})")
    else:
        print("No interesting directories or files found with the provided wordlist.")
    print("Consider using a larger wordlist or different target parameters for more comprehensive results.")

# Entry point for the script
if __name__ == "__main__":
    # Create a dummy wordlist file if it doesn't exist for easy testing
    if not os.path.exists(DEFAULT_WORDLIST_PATH):
        with open(DEFAULT_WORDLIST_PATH, 'w') as f:
            f.write("admin/\n")
            f.write("robots.txt\n")
            f.write("sitemap.xml\n")
            f.write("backup.zip\n")
            f.write("test/\n")
            f.write("login.php\n")
            f.write("index.html\n")
            f.write("config.php\n")
            f.write(".git/\n")
            f.write(".env\n")
        print(f"Created a dummy wordlist file: {DEFAULT_WORDLIST_PATH}")

    run_dir_bruteforcer()
