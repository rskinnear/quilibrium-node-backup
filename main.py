import os
import json

import paramiko
from paramiko import SSHClient
from paramiko.ssh_exception import SSHException
from scp import SCPClient

# These paths will vary based on your setup
LOCAL_DIRECTORY_PATH = (
    "C:/Users/user/OneDrive/Desktop/Quilibrium/backups/Q{node_number}_backup"
)
REMOTE_DIRECTORY_PATH = "/root/ceremonyclient/node/.config/"

# Creates a temporary directory to transfer config files when using non-root user
TEMP_REMOTE_DIRECTORY_PATH = "/home/{user}/temp_ceremonyclient_config/"

# File storing all hosts/server details
HOSTS_FILE = "hosts.json"


def load_hosts(filename: str) -> list[dict[str, str | int]]:
    """Loads a list of hosts from a JSON file."""
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def create_ssh_client(server: str, port: str, user: str, password: str) -> SSHClient:
    """Created an SSHClient to connect to the host machine"""
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password, timeout=30)
    return client


def get_config_file_paths(directory_path: str) -> tuple[str, str]:
    """Constructs the absolute paths to the keys.yml and config.yml files."""
    keys_file = os.path.join(directory_path, "keys.yml")
    config_file = os.path.join(directory_path, "config.yml")
    return keys_file, config_file


def prepare_non_root_user_environment(
    ssh_client: SSHClient, temp_directory: str, user: str
) -> None:
    """Prepares environment for non-root user by copying necessary files in case of permission conflicts."""
    keys_file, config_file = get_config_file_paths(REMOTE_DIRECTORY_PATH)
    temp_keys_file, temp_config_file = get_config_file_paths(temp_directory)
    # Create the temp directory and copy the files with sudo, then change ownership of the copies
    commands = [
        f"mkdir -p {temp_directory}",
        f"sudo cp {keys_file} {temp_keys_file}",
        f"sudo cp {config_file} {temp_config_file}",
        f"sudo chown {user}:{user} {temp_keys_file}",
        f"sudo chown {user}:{user} {temp_config_file}",
    ]

    for command in commands:
        _, stdout, stderr = ssh_client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            error_message = stderr.read().decode().strip()
            print(
                f"Error executing command: '{command}' with exit status {exit_status}. Error message: {error_message}"
            )


def main(start_index: int = 0) -> None:
    """Main function to transfer config files from remote to local"""
    hosts = load_hosts(HOSTS_FILE)  # List of hosts connection details

    for index, host in enumerate(hosts[start_index:]):
        hostname = host["hostname"]
        try:
            print(f"Connecting to {hostname}")
            ssh_client = create_ssh_client(
                hostname, host["port"], host["user"], host["password"]
            )
            with SCPClient(ssh_client.get_transport()) as scp:
                local_directory = LOCAL_DIRECTORY_PATH.format(
                    node_number=str(index + start_index + 1)
                )
                os.makedirs(
                    local_directory, exist_ok=True
                )  # Ensure the local directory path exists

                if host["user"] == "root":
                    keys_file, config_file = get_config_file_paths(
                        REMOTE_DIRECTORY_PATH
                    )
                else:
                    temp_directory = TEMP_REMOTE_DIRECTORY_PATH.format(
                        user=host["user"]
                    )
                    prepare_non_root_user_environment(
                        ssh_client, temp_directory, host["user"]
                    )
                    keys_file, config_file = get_config_file_paths(temp_directory)

                scp.get(keys_file, local_directory, recursive=True)
                scp.get(config_file, local_directory, recursive=True)

                print(f"Files copied to {local_directory} from {hostname}")
            ssh_client.close()
        except SSHException:
            print(f"Failed to connect the server: {hostname}")
            paramiko.util.log_to_file("paramiko.log")
        except Exception as e:
            print(f"Failed to connect or transfer from {hostname}. Error: {e}")


if __name__ == "__main__":
    main()
