#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import threading
import os
import sys
import shutil

import NameTransform
import config



class ThreadRemoteQsub(threading.Thread):
    """
    Thread que fai o traballo necesario para executar un solver remoto
    ou para consultar o estado de execución dun enviado á cola.
    Actualiza a ventá principal con mensaxes
    """
    
    def __init__(self, parent, window, options):
        threading.Thread.__init__(self)
        self.parent = parent
        self.window = window
        self.menus = window.menus
        self.materials = window.materials
        self.appname = self.window.get_appname()
        if not isinstance(self.appname,basestring) or len(self.appname) < 1: # non debera pasar
            self.appname = 'void'
        self.prefix = 'REMOTE RUN'
        self.ssh = None # ssh object
        self.tempdir = None # temporary directory
        self.options = options # dict
        self.serverdirsep = '/' # directory separator of server
        self.dirfiles = u'input' # input file folder
        self.direxec = u'output' # output file folder
        self.datafilebase = None
        self.qcommand = None # Queuing command



    def check_options():
        if self.options is None:
            return False
        if not 'user' in self.options:
            return False
        if not 'host' in self.options:
            return False
        if not 'passw' in self.options:
            return False
        if not 'keyfile' in self.options:
            return False
        if not 'queuing' in self.options:
            return False
        if not 'executables' in self.options:
            return False
        return True



    def stop(self):
        pass



    def run(self):
        self.send(self.prefix + ': starting ThreadRemoteQsub\n')
        
        print 'TR pid', os.getpid()

        if self.ssh is not None:
            self.close_connection()

        self.tempdir = None

        self.qcommand = self.options.get('queuing').split(None,1)
        if self.qcommand[0] == 'qsub':
            runret = self.run_qsub()
        elif self.qcommand[0] == 'qstat':
            runret = self.run_qstat()
        elif self.qcommand[0] == 'get':
            runret = self.run_get()
        else:
            runret = self.run2()
        
        # self.tempdir = None

        if self.ssh is not None:
            self.close_connection()

        if runret is False:
            self.send(self.prefix + ': ending ThreadRemoteQsub (with error)\n')
        else:
            self.send(self.prefix + ': ending ThreadRemoteQsub\n')
        
        # for deleting from window
        wx.CallAfter(self.window.finished_thread, self)



    def run2(self):
        # ssh: open connection
        ret = self.open_connection()
        if ret is not True:
            return False

        # ssh: create temporary directory in remote server and copy file(s) to it
        ret = self.copy_to_tempdir()
        if ret is not True:
            return False

        # ssh: exec solver(s)
        ret = self.exec_solver()
        if ret is not True:
            return False

        # ssh: copy file(s) from remote server
        ret = self.copy_from_tempdir()
        if ret is not True:
            return False

        # ssh: remove temporary directory in remote server
        ret = self.remove_tempdir()
        if ret is not True:
            return False

        # ssh: close connection
        ret = self.close_connection()
        if ret is not True:
            return False
        return True



    def run_qsub(self):
        # ssh: open connection
        ret = self.open_connection()
        if ret is not True:
            return False

        # ssh: create temporary directory in remote server and copy file(s) to it
        ret = self.copy_to_tempdir()
        if ret is not True:
            return False

        # ssh: exec solver(s)
        ret = self.exec_solver2()
        if ret is not True:
            return False

        # save run status
        ret = self.save_runstatus()
        if ret is not True:
            return False

        # ssh: close connection
        ret = self.close_connection()
        if ret is not True:
            return False
        return True



    def run_qstat(self):
        # ssh: open connection
        ret = self.open_connection()
        if ret is not True:
            return False

        # ssh: exec qstat
        ret = self.check_status()
        if ret is not True:
            return False

        # save run status
        ret = self.save_runstatus()
        if ret is not True:
            return False

        # refresh state
        self.parent.set_state()

        # ssh: close connection
        ret = self.close_connection()
        if ret is not True:
            return False
        return True



    def run_get(self):
        # ssh: open connection
        ret = self.open_connection()
        if ret is not True:
            return False

        # ssh: copy file(s) from remote server
        ret = self.copy_from_tempdir(self.options.get('remote_dir'))
        if ret is not True:
            return False

        # ssh: remove temporary directory in remote server
        ret = self.remove_tempdir(self.options.get('remote_dir'))
        if ret is not True:
            return False

        # ssh: close connection
        ret = self.close_connection()
        if ret is not True:
            return False
        return True



    def send(self, msg):
        wx.CallAfter(self.window.add_text, msg)



    def open_connection(self):
        # ssh: Open connection
        import SSHoper

        warning_list = []
        self.send(self.prefix+': Opening SSH connection\n')
        self.ssh = SSHoper.SSHoper(self)
        self.ssh.set_params(self.options.get('host'),self.options.get('user'), \
            self.options.get('passw'),self.options.get('keyfile'))
        ret = self.ssh.open(True, True, warning_list)
        if len(warning_list) > 0:
            string = '; '.join(warning_list)
            self.send(self.prefix+': Warning: ' + string + '\n')
        if ret is not True:
            self.send(self.prefix+': Error opening SSH: ' + ret + '\n')
            return False
        return True



    def close_connection(self):
        # ssh: Close connection
        if self.ssh is not None:
            ret = self.ssh.close()
            self.ssh = None
            if ret is not True:
                self.send(self.prefix+': Error closing SSH: ' + ret + '\n')
                return False
        return True



    def copy_to_tempdir(self):
        # Create and copy files to remote temporary directory

        # create data file: menu.dat.xml...
        datafile = self.menus.get_datafile()
        self.datafilebase = os.path.basename(datafile)
        newdatafile = self.datafilebase + '.temp-remote.xml'
        
        extra = [ self.window.get_extra('..'+self.serverdirsep+self.dirfiles+self.serverdirsep) ]
        names = NameTransform.NameTransform('..'+self.serverdirsep+self.dirfiles+self.serverdirsep) # / porque é para o solver
        self.menus.save_data(newdatafile,extras=extra,transform=names) # transformextra=names
        
        #Modificacion: copia de ficheros desde la base de datos de materiales.
        if self.window.MaterialsDB_exists:
            matfile = config.FILE_MATERIALS_DAT
            matfilebase = os.path.basename(matfile)
            newmatfile = matfilebase + '.temp-remote.xml'
            self.materials.save_data(newmatfile, force=True ,transform=names)

        # ssh: create remote directory
        self.send(self.prefix+': Creating temporary directory in server\n')
        # . ou $HOME
        # self.tmpdir relativo
        ret = self.ssh.exec_command_out_read('mktemp -d -p . -t ' + self.appname + '.XXXXXXXXXX') # quitar u
        if ret[0] is not True:
            self.send(self.prefix+\
                ': Error creating temporary directory in server: ' + ret[0] + '\n')
            return False
        if len(ret[1])<10 or ' ' in ret[1]: # arbitrario
            self.send(self.prefix+': Error creating temporary directory in server: \''+ret[1]+'\'\n')
            return False
        self.tempdir = ret[1]
        if self.tempdir[-1] == '\n':
            self.tempdir = self.tempdir[:-1]
        self.send(self.prefix+': Temporary directory \''+self.tempdir+'\' has been created\n')


        # ssh: create subdirectories
        self.send(self.prefix+': Creating subdirectories in server\n')
        ret = self.ssh.exec_command_out_read(
            'mkdir '+self.tempdir+self.serverdirsep+self.dirfiles+' && mkdir '+self.tempdir+self.serverdirsep+self.direxec+' && echo okok')
        if ret[0] is not True:
            self.send(self.prefix+\
                ': Error creating temporary subdirectories in server: ' + ret[0] + '\n')
            self.remove_tempdir()
            return False
        if ret[1] != 'okok\n':
            self.send(self.prefix+\
                ': Error creating temporary subdirectories in server: mkdir failed\n')
            self.remove_tempdir()
            return False

        # scp: copy files to remote directory
        self.send(self.prefix+': Copying files to remote directory\n')
        tocopy = []
        for origin, destiny in names.get_cache().items():
            src = origin
            dst = self.serverdirsep.join([self.tempdir,self.dirfiles,destiny[0]])
            tocopy.append((src, dst))
        # copying menu file
        tocopy.append( (newdatafile,
                self.serverdirsep.join([self.tempdir,self.dirfiles,self.datafilebase]))
                    )
        # copying materials file only if exists
        if self.window.MaterialsDB_exists:
            tocopy.append( (newmatfile,
                    self.serverdirsep.join([self.tempdir,self.dirfiles,config.FILE_MATERIALS_DAT]))
                     )
        
        for one in tocopy:
            self.send(self.prefix+': Copying \''+one[0]+'\' -> \''+one[1]+'\'\n')
            ret = self.ssh.file_put(one[0],one[1])
            
            if ret is not True:
                self.send(self.prefix+\
                    ': Error copying file \''+one[0]+'\' to \''+one[1]+'\': ' + ret + '\n')
                self.remove_tempdir()
                return False

        return True



    def copy_from_tempdir(self, tempdir=None):
        # Copy files from remote temporary directory
        if tempdir is None:
            if self.tempdir is not None:
                tempdir = self.tempdir
            else:
                self.send(self.prefix+': Files can not be copied from remote server. Temporary directory has not been specified\n')
                return False

        # listing remote files
        filelist = []
        ret = self.ssh.file_list(self.serverdirsep.join([tempdir,self.direxec]))
        if not isinstance(ret,list):
            self.send(self.prefix+\
                ': Error listing remote files\n')
            self.remove_tempdir()
            return False
        else:
            filelist = ret

        # scp: copy files to local directory
        self.send(self.prefix+': Copying files to local directory\n')
        tocopy = []
        for f in filelist:
            tocopy.append( (self.serverdirsep.join([tempdir,self.direxec,f]), f ) )
        for one in tocopy:
            self.send(self.prefix+': Copying \''+one[0]+'\' -> \''+one[1]+'\'\n')
            ret = self.ssh.file_get(one[0],one[1])

            if ret is not True:
                self.send(self.prefix+\
                    ': Error copying file \''+one[0]+'\' to \''+one[1]+'\': ' + ret + '\n')
                self.remove_tempdir()
                return False
        return True



    def exec_solver(self):
        for executable in self.options.get('executables'):
            command = executable.get('text')
            args = executable.get('attrib').get('args')
            if command is None or command == '':
                continue
            if args is None:
                args = ''
            else:
                args = ' ' + args


            datafilepath = self.serverdirsep.join(['..',self.dirfiles,self.datafilebase])
            execute = command + args + ' ' + datafilepath

            temp = ''

            string =  'export PATH=$HOME/.' + self.appname + '/solvers:$PATH &&'
            string += ' cd '+self.tempdir+self.serverdirsep+self.direxec+' &&'
            if self.options.get('queuing') is not None and len(self.options.get('queuing'))>0:
                string += ' ' + self.options.get('queuing')
                temp += ' ' + self.options.get('queuing')
            string += ' "' + execute + '"'
            temp += ' "' + execute + '"'
            # 'cd' non necesario porque cada comando é independente en paramiko
            
            self.send(self.prefix+': Executing solver: '+temp+'\n')

            ret = self.ssh.exec_command_ioe_call(string,
                None, # input
                self.send) # callback
            if ret[0] is not True:
                self.send(self.prefix+\
                    ': Error executing solver in server: ' + ret[0] + '\n')
                self.remove_tempdir()
                return False
        return True



    def exec_solver2(self):
        for executable in self.options.get('executables'):
            command = executable.get('text')
            args = executable.get('attrib').get('args')
            if command is None or command == '':
                continue
            if args is None:
                args = ''
            else:
                args = ' ' + args


            datafilepath = self.serverdirsep.join(['..',self.dirfiles,self.datafilebase])
            execute = command + args + ' ' + datafilepath

            temp = ''

            string =  'export PATH=$HOME/.' + self.appname + '/solvers:$PATH &&'
            string += ' cd '+self.tempdir+self.serverdirsep+self.direxec+' &&'
            if self.options.get('queuing') is not None and len(self.options.get('queuing'))>0:
                string += ' ' + self.options.get('queuing')
                temp += ' ' + self.options.get('queuing')
            string += ' ' + execute
            temp += ' ' + execute
            # 'cd' non necesario porque cada comando é independente en paramiko
            
            self.send(self.prefix+': Sending job to the queue: '+temp+'\n')

            ret = self.ssh.exec_command_out_read(string)
            if ret[0] is not True:
                self.send(self.prefix+': Error sending job to the queue: '+ret[0]+'\n')
                self.remove_tempdir()
                return False

            out = ret[1]
            if out[-1] == '\n':
                out = out[:-1]
            self.send(self.prefix+': ' + out + '\n')
            out = out[9:]  # Omit 'Your job ' in 'Your job <job ID> <job name> has been submitted'
            pos = out.find(' ')  # Find the first blank after the job ID
            self.options['state'] = u'Submitted'
            self.options['exec_command'] = temp
            self.options['local_dir'] = os.path.abspath(unicode(os.getcwd(), sys.getfilesystemencoding()))
            self.options['remote_dir'] = self.tempdir
            self.options['job_id'] = out[:pos]
        return True



    def check_status(self):
        if self.options.get('job_id') is None or self.options.get('job_id') == '':
            self.send(self.prefix+': Error checking remote run status: Unknown job ID\n')
            return False

        temp = ''
        string = ''

        if self.options.get('queuing') is not None and len(self.options.get('queuing'))>0:
            string = self.options.get('queuing')
            temp = self.options.get('queuing')

        string += ' -j ' + self.options.get('job_id')
        temp += ' -j ' + self.options.get('job_id')

        self.send(self.prefix+': Checking remote run status: '+temp+'\n')

        ret = self.ssh.exec_command_out_read(string)
        if ret[0] is not True:
            self.send(self.prefix+': Error checking remote run status: '+ret[0]+'\n')
            return False

        out = ret[1].split('\n')
        if out[0] is not None and out[0] != '':
            self.options['state'] = u'Not finished'
        else:
            string = 'qacct -j ' + self.options.get('job_id')
            temp = 'qacct -j ' + self.options.get('job_id')
    
            self.send(self.prefix+': Checking remote run status: '+temp+'\n')
    
            ret = self.ssh.exec_command_out_read(string)
            if ret[0] is not True:
                self.send(self.prefix+': Error checking remote run status: '+ret[0]+'\n')
                return False
    
            out = ret[1].split('\n')
            for line in out:
                parts = line.split(None,1)
                if len(parts) < 2:
                    continue
                if parts[0].strip() == 'exit_status':
                    parts[1] = parts[1].strip()
                    if parts[1].strip() == '0':
                        self.options['state'] = u'Finished'
                        return True
                    else:
                        self.options['state'] = u'Finished (with error)'
                        return True
        return True



    def remove_tempdir(self, tempdir=None):
        # ssh: remove remote directory
        if tempdir is None:
            if self.tempdir is not None:
                tempdir = self.tempdir
            else:
                self.send(self.prefix+': Temporary directory can not be removed in server. It has not been specified\n')
                return False

        if '*' in tempdir:
            self.send(self.prefix+': Temporary directory '+tempdir+' can not be removed in server. An asterisk \'*\' is present\n')
            return False

        self.send(self.prefix+': Removing temporary directory '+tempdir+' in server\n')

        ret = self.ssh.exec_command_out_read('rm -rf '+tempdir+'; echo -n $?')
        if ret[0] is not True:
            self.send(self.prefix+\
                ': Error removing temporary directory in server: ' + ret[0] + '\n')
            return False
        if ret[1] != '0':
            self.send(self.prefix+\
                ': Error removing temporary directory in server: exit code: ' + ret[1] + '\n')
            return False
        return True



    def save_runstatus(self):
        if config.FILE_RUNSTATUS is None:
            return False

        try:
            file = open(config.FILE_RUNSTATUS,'wb')
        except Exception, why:
            self.errormsg('Error saving run status data: ' + repr(why))
            return False

        state = self.options.get('state')
        if state is None:
            state = ''
        host = self.options.get('host')
        if host is None:
            host = ''
        user = self.options.get('user')
        if user is None:
            user = ''
        exec_command = self.options.get('exec_command')
        if exec_command is None:
            exec_command = ''
        local_dir = self.options.get('local_dir')
        if local_dir is None:
            local_dir = ''
        remote_dir = self.options.get('remote_dir')
        if remote_dir is None:
            remote_dir = ''
        job_id = self.options.get('job_id')
        if job_id is None:
            job_id = ''

        file.write('state: ' + state + '\n')
        file.write('-------------------------------\n')
        file.write('host: ' + host + '\n')
        file.write('user: ' + user + '\n')
        file.write('exec_command: ' + exec_command + '\n')
        file.write('local_dir: ' + local_dir + '\n')
        file.write('remote_dir: ' + remote_dir + '\n')
        file.write('job_id: ' + job_id + '\n')
        file.close()
        return True
