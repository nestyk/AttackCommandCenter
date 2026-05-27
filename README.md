# PentestLab - Vulnerable Web Application

## 📋 Description

This web application has been developed **exclusively for educational purposes** for cybersecurity training and penetration testing. The application **intentionally contains** numerous vulnerabilities that can be exploited in a controlled environment to learn attack and defense techniques.

## ⚠️ IMPORTANT NOTICE
THIS SOFTWARE IS INTENTIONALLY INSECURE!
DO NOT USE IN PRODUCTION ENVIRONMENT!
DO NOT EXPOSE TO THE INTERNET!
USE ONLY IN ISOLATED LABORATORIES!
## 🎯 Purpose

This project is a **Vulnerability Lab** designed to be attacked. Security students and professionals can:
- Practice penetration testing techniques
- Identify common vulnerabilities
- Practice exploits in a legal and controlled environment
- Understand the impact of real-world vulnerabilities

## 🛠️ Technologies

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML/CSS (Jinja2 Templating)

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/nestyk/attackcommandcenter.git
cd vulnerable-lab

# Install dependencies
pip install -r requirements.txt

# Start the application
python app.py
```

The application will be available at http://localhost:5000

🔐Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| mario_rossi | password123 | User |
| luca_bianchi | luca123 | User |

## 🚨 Vulnerabilities Present

| Vulnerability | Endpoint | Description |
|---------------|----------|-------------|
| SQL Injection | `/do_login` | Login vulnerable to SQL injection |
| SQL Injection | `/profile/<id>` | Unsanitized path parameter |
| SQL Injection | `/acc/profile/<id>` | Unsanitized path parameter |
| Command Injection | `/do_ping` | Ping command vulnerable to command injection |
| Path Traversal | `/files` | `file` parameter allows directory traversal |
| Path Traversal | `/acc/files` | `file` parameter allows directory traversal |
| IDOR | `/profile/<id>` | Unauthorized access to other users' profiles |
| IDOR | `/acc/profile/<id>` | Unauthorized access to other users' profiles |
| Information Disclosure | `/debug_check` | Debug endpoint exposes sensitive data |
| Hardcoded Credentials | `app.secret_key` | Secret key hardcoded in the code |
| Clear Text Passwords | Database | Passwords stored in plain text |

## 🎯 Pentesting Objectives

1. Log in without valid credentials (SQL Injection)
2. View other users' profiles (IDOR)
3. Read arbitrary files from the server (Path Traversal)
4. Execute arbitrary commands on the system (Command Injection)
5. Obtain sensitive information (Information Disclosure)
6. Escalate privileges (Role manipulation)

🛡️ Disclaimer
This software is provided exclusively for educational purposes. The author is not responsible for any misuse or damage caused by this application. Use only in authorized testing environments.

📚 Useful Resources

[OWASP Top 10](https://owasp.org/www-project-top-ten/)

[PortSwigger Web Security Academy](https://portswigger.net/web-security)

[VulnHub](https://www.vulnhub.com/)

📄 License
This project is distributed for educational purposes.