import logging
import paramiko
import sys
import getpass

class SSHManager(object):
    def __init__(self, **kwargs):
        self.login          = kwargs.get('login', getpass.getuser())
        self.port           = kwargs.get('port', '22')
        self.host           = kwargs.get('host', None)
        self.privatekeyfile = kwargs.get('keyfile', None) # paramiko defaults to the usual places
        self.log            = logging.getLogger(__name__)
        
        if self.privatekeyfile is not None:
            try:
                k = paramiko.RSAKey.from_private_key_file(self.privatekeyfile)
            except PasswordRequiredException as e:
                self.log.debug("Private key seems to have a password.. aborting")
                raise
            except IOError as e:
                self.log.debug("Cannot open private key file.. aborting")
                raise
        else:
            k = None

        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(hostname=self.host,port=int(self.port),username=self.login,pkey=k)
            self.sftp = self.client.open_sftp()
        except Exception as e:
            self.log.debug(e)
            self.log.error("Failed to establish SSH connection")
            sys.exit(1)

    def remote_cmd(self,cmd):
        """
        Wraps around exec_command for a bit nicer output
        """
        self.log.debug("Executing command %s" % cmd)
        (_,stdout,stderr) = self.client.exec_command(cmd)
        out = "".join(stdout.readlines()).rstrip()
        err = "".join(stderr.readlines()).rstrip()

        return out, err

    def cleanup(self):
        """
        Close SSH, SFTP connnections
        """
        self.sftp.close()
        self.client.close()
