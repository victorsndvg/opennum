#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import os
import os.path
import errno
import sys
import Window



def create_dir(dirname):
    try:
        os.makedirs(dirname) # devolve excepción se xa existía o directorio
    except OSError, e:
        if e.errno != errno.EEXIST:
            print e
    return os.path.isdir(dirname)



def run():

    print 'MF pid', os.getpid()
    
    exe_path = sys.argv[0]
    exe_path_real = os.path.realpath(exe_path)
    exe_path_dir = os.path.dirname(exe_path_real)
    exe_path_name = os.path.basename(exe_path_real)
    exe_path_abs = os.path.abspath(exe_path_dir) # absolute path of executable dir

    point = exe_path_name.find('.')
    if point > 0:
        appname = exe_path_name[:point]
    else:
        appname = exe_path_name

    print "pathexe", exe_path
    print "pathreal", exe_path_real
    print "pathname", exe_path_name
    print "pathdir", exe_path_dir
    print "pathabs", exe_path_abs
    print 'appname', appname


    app = wx.App(0)
    app.SetAppName(appname)

#    print wx.GetApp().GetAppName()

    # determina e crea o directorio de configuración
    configdir = wx.StandardPaths.Get().GetUserDataDir() # retorna en utf8 ?
    result = create_dir(configdir)
    if not result:
        configdir = None
    print 'configdir', configdir
    
    frame = Window.Window(appname, exe_path_abs, configdir)
    frame.Center()
    frame.Show()
#    frame2 = Window.Window(appname, exe_path_abs, configdir)
#    frame2.Show()
    app.MainLoop()



# comentado para que no se pueda arrancar la aplicación ejecutando este fichero

#if __name__ == '__main__':
#    run()



# para arrancar desde otro, poner en el otro:

# import launcher
# if __name__ == '__main__':
#   launcher.run()
