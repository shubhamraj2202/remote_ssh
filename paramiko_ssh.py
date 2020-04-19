import paramiko
from logging import getLogger

log = getLogger(__name__)

class ServerSSH:
    """
        Create SSH Object, Used for opening SSH Session and run commands
    """
    def __init__(self, host, username, password, server_type=None, key=None, passphrase=None):
        log.info(f"Initializing Server :{host} with Username: {username}")
        self.host = host
        self.username = username
        self.password = password
        self.server_type = server_type
        self.key = key
        self.passphrase = passphrase
    
    def create_ssh_session(self):
        try:
            log.info(f"Creating SSH Session with username: {self.username} & server: {self.host}")
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.key is not None:
                self.key = paramiko.RSAKey.from_private_key(StringIO(key), password=self.passphrase)
            self.ssh_client.connect(hostname=self.host, username=self.username, password=self.password, pkey=self.key) 
            return True
        except (TimeoutError, paramiko.ssh_exception.AuthenticationException) as e:
            log.error(f"Could not create SSH Session, Reason :  {e}")
            return False

    def close_session(self):
        if self.ssh_client is not None:
            self.ssh_client.close()
            self.ssh_client = None

    def run_command(self, command, sudo_mode=False):
        if not sudo_mode:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
        else:
            stdin, stdout, stderr = self.ssh_client.exec_command("sudo {}".format(command), get_pty=True)
            stdin.write('{}\n'.format(self.password))
            stdin.flush()

        err = stderr.read()
        if err:
            log.error('Error received while running command: {}, Error : {}'.format(command, err))
            return err
        return stdout.readlines() 

    def sftp_download(self, remote_file_path, local_file_path):
        ftp_client = self.ssh_client.open_sftp()
        ftp_client.get(remote_file_path, local_file_path)
        ftp_client.close()
    
    def sftp_upload(self, remote_file_path, local_file_path):
        ftp_client = self.ssh_client.open_sftp()
        ftp_client.put(remote_file_path, local_file_path)
        ftp_client.close()