#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paramiko
import os
import getpass
from binascii import hexlify # mywarningpolicy

paramiko.util.log_to_file('paramiko.log.txt')

# make return string on error ?
# exceptions: capture !!!

class SSHoper():


    def __init__(self,parent):
        self.ssh = None
        self.sftp = None

        self.host = None
        self.user = None
        self.passw = None
        self.keyfile = None
        self.thread = parent


    def __del__(self):
        """Attempt to clean up if not explicitly closed."""
        self.close()


    def set_params(self, host, user, passw=None, keyfile=None):
        """set parameters for future SSH connections"""
        self.host = host
        self.user = user
        #if passw is None:
        #    passw = getpass.getpass('Password: ')
        self.passw = passw
        self.keyfile = keyfile



    def open(self, ssh=True, sftp=True, warnings=None):
        """if not open, open ssh or ssh+sftp. returns True or error string"""
        if ( sftp or ssh ) and self.ssh is None: # sftp depends from ssh
            
            mywp = MyWarningPolicy()
            try:
                self.ssh = paramiko.SSHClient()
                self.ssh.load_system_host_keys() # posix # policy [só hosts conocidos]
                self.ssh.set_missing_host_key_policy(mywp)
                # (AutoAddPolicy / RejectPolicy / WarningPolicy / custom)
                # AuthenticationException
                key = self.keyfile
                if key == '':
                    key = None
                self.ssh.connect(self.host, username=self.user, password=self.passw, key_filename=key)
                if mywp.get_msg() is not None and warnings is not None:
                    warnings.append(mywp.get_msg())
            except Exception, why:
                if mywp.get_msg() is not None and warnings is not None:
                    warnings.append(mywp.get_msg())
                return 'Error connecting: ' + repr(why)
        
            
        if sftp and self.sftp is None and self.ssh is not None:
            try:
                self.sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
            except Exception, why:
                return 'Error creating SFTPClient: ' + repr(why)

        return True


    def close(self, ssh=True, sftp=True):
        """if open, close sftp or ssh+sftp"""
        if ( ssh or sftp ) and self.sftp is not None: # sftp depends from ssh
            try:
                self.sftp.close()
            except Exception, why:
                return 'Error closing SFTPClient: ' + repr(why)
            self.sftp = None
        
        if ssh and self.ssh is not None:
            try:
                self.ssh.close()
            except Exception, why:
                return 'Error closing SSHClient: ' + repr(why)
            self.ssh = None

        return True


    # error, where?
    def exec_command_out_read(self, command):
        ret = [True, None] # error, output

        if self.ssh is None:
            ret[0] = 'Error executing SSH command: ssh not open'
            return ret
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
        except Exception, why:
            ret[0] = 'Error executing SSH command: ' + repr(why)
            return ret
        stdin.close()
        stdin.channel.shutdown_write() # se non, colga con 'cat'
        
        ret[1] = stdout.read()
        return ret



    def exec_command_out_call(self, command, log):
        ret = [True, None] # error, output

        if self.ssh is None:
            ret[0] = 'Error executing SSH command: ssh not open'
            return ret
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
        except Exception, why:
            ret[0] = 'Error executing SSH command: ' + repr(why)
            return ret
        stdin.close()
        stdin.channel.shutdown_write() # se non, colga con 'cat'

        out = stdout.readline()
        while out:
            if out:
                log(out)
            out = stdout.readline()

        return ret



    def exec_command_ioe_call(self, command, input, log):
        ret = [True, None] # error, output

        if self.ssh is None:
            ret[0] = 'Error executing SSH command: ssh not open'
            return ret
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
        except Exception, why:
            ret[0] = 'Error executing SSH command: ' + repr(why)
            return ret
        if input is not None:
            stdin.write(input)
        stdin.close()
        stdin.channel.shutdown_write() # se non, colga con 'cat'

        # mellorar: usar select ? agora imprime desordenado: primeiro saída, despois erro
        out = stdout.readline()
        while out:
            log(out)
            out = stdout.readline()

        err = stderr.readline()
        while err:
            log(err)
            err = stderr.readline()

        return ret


#copia de directorios enteros
    def folder_get(self, remote, local):
        sep = '/'
        if self.sftp is None:
            return 'Error executing SFTP command: sftp not open'
        try:
            dir = self.sftp.listdir(remote)
            folder = os.path.basename(remote)
            if not os.path.exists(local):
                try:
                    os.mkdir(local)
                    #while not os.path.exists(local):
                        #pass
                except OSError, e:
                    print 'Error creating ' + folder + ' directory:', e
            for file in dir:
                self.thread.send(self.thread.prefix+': Copying \''
                +sep.join([remote,file])+'\' -> \''+sep.join([local,file])+'\'\n')
                self.file_get(sep.join([remote,file]),sep.join([local,file]))
        except Exception, e1:
            return 'SFTPget error: ' + repr(e1)
        return True


    def file_get(self, remote, local):
        if self.sftp is None:
            return 'Error executing SFTP command: sftp not open'
        try:
            #comprobacion de directorio, temporal
            if str(self.sftp.lstat(remote))[0] == 'd':
                self.folder_get(remote,local)
            else:
                self.sftp.get(remote,local)
        except Exception, e:
            return 'SFTPget error: ' + repr(e)
        return True



    def file_put(self, local, remote):
        if self.sftp is None:
            return 'Error executing SFTP command: sftp not open'
        try:
            self.sftp.put(local,remote)
        except Exception, e:
            return 'SFTPput error: ' + repr(e)
        return True



    def file_list(self, path='.'):
        if self.sftp is None:
            return 'Error executing SFTP command: sftp not open'
        try:
            list = self.sftp.listdir(path)
        except Exception, e:
            return 'SFTPlist error: ' + repr(e)
        return list

        
        
        
        
class MyWarningPolicy(paramiko.MissingHostKeyPolicy):
    
    msg = None
    
    def missing_host_key(self, client, hostname, key):
        self.msg ='Unknown %s host key for %s: %s' % \
            (key.get_name(), hostname, hexlify(key.get_fingerprint()))
        print self.msg

    def get_msg(self):
        return self.msg
