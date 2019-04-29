# Script to automatically downlaod and remove a folder from raspberry pi

from scp import SCPClient
from paramiko import SSHClient
from paramiko import AutoAddPolicy
import os

HOSTNAME    = ""
USERNAME    = ""
PASSWORD    = ""
REMOTE_PATH = ""
LOCAL_PATH  = os.path.expanduser("~/Desktop")

# https://stackoverflow.com/a/23256181/1440037
def rm(sftp, path):
    files = sftp.listdir(path)
    for f in files:
        filepath = os.path.join(path, f)
        try:
            sftp.remove(filepath)
        except IOError:
            rm(sftp, filepath)
    sftp.rmdir(path)

def download():
    remote_folder_name = REMOTE_PATH.split('/')[-1]
    
    print("INFO - Connecting to Raspberry pi...")
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(hostname=HOSTNAME, username=USERNAME, password=PASSWORD)

    print("INFO - Downloading {} folder on {}...".format(
        remote_folder_name,
        LOCAL_PATH.split('/')[-1]
        ))
    with SCPClient(ssh.get_transport()) as scp:
        scp.get(remote_path=REMOTE_PATH,
                local_path=LOCAL_PATH, 
                recursive=True)
        print("DONE - {} downloaded").format(remote_folder_name)

    print("Removing {} folder on raspberry...").format(remote_folder_name)
    with ssh.open_sftp() as sftp:
        rm(sftp, REMOTE_PATH)
        print("DONE - {} folder deleted remotely.").format(remote_folder_name)

    ssh.close()


if __name__ == "__main__":
    download()
