# Python Pentesting Toolkit
A collection of basic, modular Python scripts designed for fundamental web application and network penetration testing tasks. This toolkit is built for educational purposes and to demonstrate core concepts of ethical hacking with Python.

`Disclaimer: This toolkit is for educational and authorized testing purposes only. Do NOT use these scripts against any system or network without explicit, written permission from the owner. Unauthorized access and testing are illegal and unethical. The author is not responsible for any misuse or damage caused by these tools.`

🚀 Features
This toolkit currently includes the following scripts, each focusing on a specific pentesting phase or technique:

`port_scanner.py:` Basic network reconnaissance to identify open TCP ports on a target host.

`web_proxy.py:` A simple HTTP proxy to intercept, view, and conceptually modify web traffic.

`sql_injection_tester.py:` Automates basic detection of SQL Injection vulnerabilities by injecting common payloads and analyzing responses.

`xss_exploiter.py:` Demonstrates the crafting and delivery of Cross-Site Scripting (XSS) payloads to vulnerable web application parameters.

`dir_bruteforcer.py:` Discovers hidden directories and files on a web server using a wordlist.

`login_bruteforcer.py:` Attempts to brute-force web login forms using username and password wordlists.

`credential_listener.py:` A simple HTTP server to act as an attacker's listener, capturing exfiltrated data (e.g., cookies from XSS).

`toolkit_updater.py:` A conceptual script to manage and guide the update process for the toolkit (does not perform automatic, insecure updates).

🛠️ Installation
Clone the repository (or download the scripts):

git clone https://github.com/therealmighty/WebTesting-Kit
cd WebTesting-Kit

`Install Dependencies:`
The only external Python library required is requests. All other modules are part of Python's standard library.

`pip install requests`

💡 Usage
Each script is designed to be run independently from your terminal. Navigate to the directory where you saved the scripts.

`port_scanner.py`
Scans a target host for open TCP ports.

python port_scanner.py

Follow the prompts to enter the target host, start port, and end port.

`web_proxy.py`
Starts a basic HTTP proxy server. Configure your browser to use this proxy (e.g., 127.0.0.1:8888).

python web_proxy.py

The proxy will listen on 127.0.0.1:8888 by default.

`sql_injection_tester.py`
Tests a web application parameter for SQL Injection vulnerabilities.

python sql_injection_tester.py

Follow the prompts for the target URL and the vulnerable parameter name.

`xss_exploiter.py`
Demonstrates XSS payload delivery to a vulnerable web application parameter.

python xss_exploiter.py

Follow the prompts for the target URL and the vulnerable parameter name. Remember to manually verify XSS in a browser.

`dir_bruteforcer.py`
Attempts to discover hidden directories and files on a web server. Requires a wordlist.

python dir_bruteforcer.py

Follow the prompts for the target URL and the path to your wordlist file. A dummy common.txt will be created if not found.

`login_bruteforcer.py`
Brute-forces a web login form. Can use built-in dummy wordlists or custom ones.

python login_bruteforcer.py

Follow the prompts for the login URL, form field names, and wordlist choice.

`credential_listener.py`

Starts a simple HTTP server to capture exfiltrated data. Data is logged to harvested_credentials.log.

`python credential_listener.py`

The listener runs on port 8000 by default. Use your machine's IP address in payloads (e.g., from XSS) to direct traffic here.

`toolkit_updater.py`
A conceptual tool for managing and checking for updates to your toolkit.

`python toolkit_updater.py`

Follow the menu options. This script is for guidance on managing your toolkit and does not perform live, insecure updates.

🤝 Contributing & Expanding
this toolkit is meant for beginners to learn,
if planning to fork and release, add credit please
expand on everything if wanted

📄 License
This project is open-source and available under the MIT License. (You'll need to create a LICENSE file in your repo with the MIT license text).

📞 Support
For questions or issues, please open an issue on the GitHub repository.
