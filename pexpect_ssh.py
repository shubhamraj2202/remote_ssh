import pexpect
from logging import getLogger

log = getLogger(__name__)

class OpenSSH:
    """
        Return object of OpenSSH  for linux  server
        Arguments:
            server_name   - Hostname of the connecting server
            server_ip     - Host IP of the connecting server
            user_name     - Username to be used for login
            password      - Password for the user_name
    """

    def __init__(self, server_name, server_ip, user_name, password, user_prompt='\$ '):
        log.info(f'Initializing {server_name} <{server_ip}> object for user {user_name}')
        self.server_name = server_name
        self.server_ip   = server_ip
        self.user_name   = user_name
        self.password    = password
        self.ssh_sess_id = None
        self.user_prompt = user_prompt
    
    def __del__(self):
        try:
            self.__sess_cleanup()
        except:
            pass
        return

    def __sess_cleanup(self):
        if self.ssh_sess_id:
            self.ssh_sess_id.close()
            self.ssh_sess_id.wait()
        self.ssh_sess_id = None
    
    def open_ssh_session(self):
        """
            Opens ssh session to Linux server.
            If already opened, throws warning message and ignores the request!
        """
        if self.ssh_sess_id:
            log.info('Server Session already opened')
            return True

        session = False

        login_expect_strings = ['\(yes\/no\)\?', 'assword:', self.user_prompt, pexpect.TIMEOUT]
        log.info(f'Starting SSH session to {self.user_name}@{self.server_name}  < {self.server_ip} >')
        self.ssh_sess_id = pexpect.spawn (f'ssh -o UserKnownHostsFile=/dev/null {self.user_name}@{self.server_ip}', timeout=30, maxread=999999)

        while True:
            index = self.ssh_sess_id.expect(login_expect_strings)
            if index == 0:
                self.ssh_sess_id.sendline('yes')
            elif index == 1:
                self.ssh_sess_id.sendline(self.password)
            elif index == 2:
                self.ssh_sess_id.sendline()
                session = True
                break
            elif index == 3:
                print(f'Timeout during ssh to {self.server_name} <{self.server_ip}>')
                self.__sess_cleanup()
                break
        return session
    
    def close_ssh_session (self):
        '''
            Closes ssh session to target test server. \n
            If no session is opened previously. ignores the request
        '''

        if not (self.ssh_sess_id):
            return True
        
        close_sesison = False
        expect_for_strings = ['# ', self.user_prompt, 'closed.', pexpect.TIMEOUT]
        log.info(f'Closing Ssh session for {self.server_name} <{self.server_ip}>')

        while True:
            index = self.ssh_sess_id.expect (expect_for_strings)
            if index == 0 or index == 1:
                self.ssh_sess_id.sendline ('exit')
            elif match_index == 2:
                log.info('Ssh Session for ' + self.server_name + ' <' + self.server_ip + '> closed')
                self.sess_cleanup()
                close_sesison = True
                break
            elif match_index == 3:
                self.sess_cleanup()
                close_sesison = False
                log.info(f'Timeout while closing ssh session for {self.server_name}  <{self.server_ip}>')
                break
        return close_sesison

    def do_scp (self, source_path, destination_path, scp_password=None):
        '''
            Performs SCP operation from the server from where the framework scripts are invoked \n
            Returns the scp success state as True / False \n

            Arguments: \n
                source_path         - SCP's source file/directory path \n
                destination_path    - SCP's destination file/directory path \n
                scp_password        - Password (if any) required for scp operation. Default is 'None'
        '''
        scpSuccess   = False
        exp_continue = True
        scp_password = scp_password or self.password

        print('DEBUG', 'Scp %s %s' % (source_path, destination_path))

        scp_command          = 'scp -o UserKnownHostsFile=/dev/null -r %s %s' % (source_path, destination_path)
        login_expect_strings = ['\(yes\/no\)\?', 'assword:', pexpect.EOF, pexpect.TIMEOUT]

        scp_session = pexpect.spawn (scp_command,timeout=600)

        while exp_continue:
            match_index = scp_session.expect (login_expect_strings,timeout=600)
            if match_index == 0:
                scp_session.sendline ('yes')
            elif match_index == 1:
                scp_session.sendline (scp_password)
            elif match_index == 2:
                exp_continue = False
                scpSuccess = True
                logMsg ('DEBUG', 'Scp completed')
            elif match_index == 3:
                logMsg ('ERROR', 'Timeout during scp of ' + source_path)
                exp_continue = False

        scp_session.close()
        scp_session.wait()
        return scpSuccess
