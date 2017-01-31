#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import threading
import os
import shutil

import NameTransform
import config



class ThreadRemote(threading.Thread):
    """
    Thread que fai o traballo necesario para executar un solver remoto.
    Copiar os datos e executar o solver por SSH/SFTP/SCP.
    Actualiza a ventá principal con mensaxes
    """
    
    def __init__(self, window, options):
        threading.Thread.__init__(self)
        self.window = window
        self.menus = window.menus
        self.materials = window.materials
        self.appname = self.window.get_appname()
        if not isinstance(self.appname,basestring) or len(self.appname) < 1: # non debera pasar
            self.appname = 'void'
        self.prefix = 'REMOTE SOLVER'
        self.ssh = None # ssh object
        self.tempdir = None
        self.options = options # dict



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
        print 'TR pid', os.getpid()

        if self.ssh is not None:
            ret = self.ssh.close()
            if ret is not True:
                self.send(self.prefix+': run: Error closing SSH: ' + ret + '\n')
            self.ssh = None

        self.tempdir = None

        runret = self.run2()
        
        self.tempdir = None

        if self.ssh is not None:
            ret = self.ssh.close()
            if ret is not True:
                self.send(self.prefix+': run: Error closing SSH: ' + ret + '\n')
            self.ssh = None

        if runret is False:
            self.send(self.prefix + ': ending ThreadRemote (with error)\n')
        else:
            self.send(self.prefix + ': ending ThreadRemote\n')
        
        # for deleting from window
        wx.CallAfter(self.window.finished_thread, self)
        
    def run2(self):
        self.send(self.prefix + ': starting ThreadRemote\n')
        
        serverdirsep = '/' # directory separator of server
        
        # remote
        dirfiles = u'input'
        direxec = u'output'
        
        # ou crear dirtemp/
        #                 input/ out.dat.xml 0.mfm 1.unv ...
        #                 output/ solver's cwd: output files

        # create data file: menu.dat.xml...
        datafile = self.menus.get_datafile()
        datafilebase = os.path.basename(datafile)
        newdatafile = datafilebase + '.temp-remote.xml'
        #newdatafile = os.path.join(dirtemp,datafilebase) # antes
        
        extra = [ self.window.get_extra('..'+serverdirsep+dirfiles+serverdirsep) ]
        names = NameTransform.NameTransform('..'+serverdirsep+dirfiles+serverdirsep) # / porque é para o solver
        self.menus.save_data(newdatafile,extras=extra,transform=names) # transformextra=names
        
        #Modificacion: copia de ficheros desde la base de datos de materiales.
        if self.window.MaterialsDB_exists:
            matfile = config.FILE_MATERIALS_DAT
            matfilebase = os.path.basename(matfile)
            newmatfile = matfilebase + '.temp-remote.xml'
            self.materials.save_data(newmatfile, force=True ,transform=names)

        # #
        import SSHoper
        # #
        
        def remove():
            # ssh: remove remote directory
            self.send(self.prefix+': Removing temporary directory in server\n')
            ret = ssh.exec_command_out_read('rm -rf '+self.tempdir+'; echo -n $?')
            if ret[0] is not True:
                self.send(self.prefix+\
                    ': Error removing temporary directory in server: ' + ret[0] + '\n')
                return False
            if ret[1] != '0':
                self.send(self.prefix+\
                    ': Error removing temporary directory in server: exit code: ' + ret[1] + '\n')
                return False
            return True


        warning_list = []
        self.send(self.prefix+': Opening SSH connection\n')
        ssh = self.ssh = SSHoper.SSHoper(self)
        ssh.set_params(self.options.get('host'),self.options.get('user'), \
            self.options.get('passw'),self.options.get('keyfile'))
        ret = ssh.open(True, True, warning_list)
        if len(warning_list) > 0:
            string = '; '.join(warning_list)
            self.send(self.prefix+': Warning: ' + string + '\n')
        if ret is not True:
            self.send(self.prefix+': Error opening SSH: ' + ret + '\n')
            return False


        # ssh: create remote directory
        self.send(self.prefix+': Creating temporary directory in server\n')
        # . ou $HOME
        # self.tmpdir relativo
        ret = ssh.exec_command_out_read('mktemp -d -p . -t ' + self.appname + '.XXXXXXXXXX') # quitar u
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
        self.send(self.prefix+': Created temporary directory \''+self.tempdir+'\'\n')


        # ssh: create subdirectories
        self.send(self.prefix+': Creating subdirectories in server\n')
        ret = ssh.exec_command_out_read(
            'mkdir '+self.tempdir+serverdirsep+dirfiles+' && mkdir '+self.tempdir+serverdirsep+direxec+' && echo okok')
        if ret[0] is not True:
            self.send(self.prefix+\
                ': Error creating temporary subdirectories in server: ' + ret[0] + '\n')
            remove()
            return False
        if ret[1] != 'okok\n':
            self.send(self.prefix+\
                ': Error creating temporary subdirectories in server: mkdir failed\n')
            remove()
            return False

        # scp: copy files to remote directory
        self.send(self.prefix+': Copying files to remote directory\n')
        tocopy = []
        for origin, destiny in names.get_cache().items():
            src = origin
            dst = serverdirsep.join([self.tempdir,dirfiles,destiny[0]])
            tocopy.append((src, dst))
        # copying menu file
        tocopy.append( (newdatafile,
                serverdirsep.join([self.tempdir,dirfiles,datafilebase]))
                    )
        # copying materials file only if exists
        if self.window.MaterialsDB_exists:
            tocopy.append( (newmatfile,
                    serverdirsep.join([self.tempdir,dirfiles,config.FILE_MATERIALS_DAT]))
                     )
        
        for one in tocopy:
            self.send(self.prefix+': Copying \''+one[0]+'\' -> \''+one[1]+'\'\n')
            ret = ssh.file_put(one[0],one[1])
            
            if ret is not True:
                self.send(self.prefix+\
                    ': Error copying file \''+one[0]+'\' to \''+one[1]+'\': ' + ret + '\n')
                remove()
                return False

                
        # ssh: exec solver(s)
        for executable in self.options.get('executables'):
            command = executable.get('text')
            args = executable.get('attrib').get('args')
            if command is None or command == '':
                continue
            if args is None:
                args = ''
            else:
                args = ' ' + args


            datafilepath = serverdirsep.join(['..',dirfiles,datafilebase])
            execute = command + args + ' ' + datafilepath

            temp = ''

            string =  'export PATH=$HOME/.' + self.appname + '/solvers:$PATH &&'
            string += ' cd '+self.tempdir+serverdirsep+direxec+' &&'
            if self.options.get('queuing') is not None and len(self.options.get('queuing'))>0:
                string += ' ' + self.options.get('queuing')
                temp += ' ' + self.options.get('queuing')
            string += ' "' + execute + '"'
            temp += ' "' + execute + '"'
            # 'cd' non necesario porque cada comando é independente en paramiko
            
            self.send(self.prefix+': Executing solver: '+temp+'\n')

            ret = ssh.exec_command_ioe_call(string,
                None, # input
                self.send) # callback
            if ret[0] is not True:
                self.send(self.prefix+\
                    ': Error executing solver in server: ' + ret[0] + '\n')
                remove()
                return False


        # listing remote files
        filelist = []
        ret = ssh.file_list(serverdirsep.join([self.tempdir,direxec]))
        if not isinstance(ret,list):
            self.send(self.prefix+\
                ': Error listing remote files\n')
            remove()
            return False
        else:
            filelist = ret


        # scp: copy files to local directory
        self.send(self.prefix+': Copying files to local directory\n')
        tocopy = []
        for f in filelist:
            tocopy.append( (serverdirsep.join([self.tempdir,direxec,f]), f ) )
        for one in tocopy:
            self.send(self.prefix+': Copying \''+one[0]+'\' -> \''+one[1]+'\'\n')
            ret = ssh.file_get(one[0],one[1])

            if ret is not True:
                self.send(self.prefix+\
                    ': Error copying file \''+one[0]+'\' to \''+one[1]+'\': ' + ret + '\n')
                remove()
                return False


        # ssh: erase files
        return remove()

        # ollo: servidor con '/', local pode estar con '\'"
        # borrar dir se hai erro ?

        # ssh: create remote directory
        # scp: copy files to remote directory
        # ssh: exec solver
        # scp: obtain files
        # ssh: erase files

        return True

    def send(self, msg):
        wx.CallAfter(self.window.add_text, msg)
