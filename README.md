# Quilibrium Node Backup Tool

This script is designed to facilitate the backup of configuration files from Quilibrium nodes deployed on various hosts. It automates the process of securely connecting to each host, retrieving specified configuration files (keys.yml and config.yml), and storing them in a designated local directory.

## Prerequisites

Before you can use this script, ensure you have the following prerequisites installed and configured:

- Python 3.10 or higher
- `paramiko` and `scp` Python libraries
- Access to the VPS or remote hosts via SSH
- SSH credentials (hostname, port, user, password) for each remote host

## Installation

1. Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

2. Clone this repository or download the script to your local machine:

   ```bash
   git clone https://github.com/rskinnear/quilibrium-node-backup
   pip install requirements.txt
   ```

## Configuration

1. Create a hosts.json file and fill it with your server credentials including the hostname/IP address, user (e.g., root), port number, and password. You can refer to the provided example in hosts-example.json. Alternative forms of authentication, such as via private keys, are not supported.
    
2. In main.py, locate and modify the two constant variables at the top of the file: LOCAL_DIRECTORY_PATH and REMOTE_DIRECTORY_PATH. Adjust LOCAL_DIRECTORY_PATH to specify where you want to store your configuration files locally. Modify REMOTE_DIRECTORY_PATH to indicate the location of your .config file on the host machines. This assumes a uniform directory structure across all host machines.
   
3. Navigate to the root of the repository and execute `python main.py` to initiate the backup process.