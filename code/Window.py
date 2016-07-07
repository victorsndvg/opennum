#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import config
import dialogs
import PanelWidgets
import PanelVisual
import PanelExec
import Menus
import Menu # para nome de materialsDB
import SubMenu # para nome de materialsDB
import Leaf # para nome de materialsDB
import Applications2
import Log
import Process
import FileManager2
import Parametrize
import WindowTabular
import ThreadRemote
import WindowRemote
import WindowCustom
import WindowHtml

import os
import sys
import shutil
import subprocess
import codecs # para file.read utf-8
import logging


class Window(wx.Frame):

    # number of id linear spaces

    ID_OPEN = 3*config.ID_SPACES+config.SPACE_MENU
    ID_EXIT = 4*config.ID_SPACES+config.SPACE_MENU
    ID_HELP = 5*config.ID_SPACES+config.SPACE_MENU
    ID_DUMP = 6*config.ID_SPACES+config.SPACE_MENU
    ID_SAVE = 7*config.ID_SPACES+config.SPACE_MENU
    ID_ABOUT = 8*config.ID_SPACES+config.SPACE_MENU
    ID_HELP1 = 9*config.ID_SPACES+config.SPACE_MENU
    ID_HELP2 = 10*config.ID_SPACES+config.SPACE_MENU
    ID_HELP3 = 11*config.ID_SPACES+config.SPACE_MENU
    ID_HELP4 = 12*config.ID_SPACES+config.SPACE_MENU
    ID_HELP5 = 13*config.ID_SPACES+config.SPACE_MENU
    ID_NULL = 14*config.ID_SPACES+config.SPACE_MENU
    ID_VADD = 21*config.ID_SPACES+config.SPACE_MENU
    ID_MADD = 22*config.ID_SPACES+config.SPACE_MENU
    ID_TDEL = 23*config.ID_SPACES+config.SPACE_MENU
    ID_MESHES = 24*config.ID_SPACES+config.SPACE_MENU
    ID_MACTION = 25*config.ID_SPACES+config.SPACE_MENU
    MIN_PROTECTED_ID = 26



    def __init__(self, appname, path, configdir):
        #self.title = wx.GetApp().GetAppName()
        self.title = appname
        wx.Frame.__init__(self,None,wx.ID_ANY,self.title) # era 1, é -1

#Variable usada para indexar los nuevos menus Application/Sample data
#Se utiliza como valor de partida para indexar el resto de menus
	self.apps_index = 0							#añadido
	self.menuapp = None							#añadido
	self.menusampledata = None						#añadido
	self.application = None							#añadido
	self.sample_data = None							#añadido
	self.has_folder = False							#añadido
	self.has_app = False							#añadido
	self.only_one_app = False						#añadido
	self.only_one_example = False						#añadido

        self.path_local = None
        self.path_exe = unicode(path,sys.getfilesystemencoding())
        self.configdir = configdir # parece que xa está en unicode
	# flag para la comprobacion de existencia de materialsdb
	self.MaterialsDB_exists = False					#añadido
	# flag para la comprobacion de existencia de config
	self.ConfigFile_exists = False					#añadido
	# flag para la aplicacion de cambios de configuracion. Solo dentro del menu de configuracion.
	self.apply_config_flag = True					#añadido
	# flag para recargar el menu al acabar la ejecucion de un solver
	self.reload_menu = False						#añadido

        if self.configdir is None:
            self.errormsg(u'Error: Could not create config dir. Some funcionality may be affected')

        # se existe o directorio apps no directorio home, utilizao, se non, utiliza o suministrado no paquete
        self.appsdir = self.calculate_appsdir()

        self.menus = Menus.Menus(self)
        self.apps2 = None
        self.materials = None
        self.config = None

        # para a venta de datos tabulares
        self.tabular = None
        
        self.threads = []
        
#        below
#        self.menu_postload()
        self.process = Process.Process(self)
        self.timer = None
        self.menulast = [] # special menus [Materials Database]

        self.path_local_save_filename = None
        self.path_local_dir_materials = None
        self.path_local_materials = None
        self.path_local_remotedata = None
	self.init_config() #load initial configuration
        if self.configdir is not None:
            self.path_local_save_filename = os.path.join(self.configdir, config.FILE_LASTFOLDER)
            self.path_local_materials_dir = os.path.join(self.configdir, config.DIR_MATERIALS)
            self.path_local_materials = os.path.join(self.configdir, config.DIR_MATERIALS, config.FILE_MATERIALS)
            self.path_local_config_dir = os.path.join(self.configdir, config.DIR_CONFIG)
            self.path_local_config = os.path.join(self.configdir, config.DIR_CONFIG, config.FILE_CONFIG)
            self.path_local_remotedata = os.path.join(self.configdir, config.FILE_REMOTEDATA)
            self.copy_materials() # copy if materials do not exist. with force=True always
            self.load_materials() # to self.materials
            self.copy_config() # copy if config do not exist. with force=True always
            self.load_config() # to self.config
	    self.apply_config() #apply the configuration from file
	    if self.maximize_window:
		self.Maximize()
            
        self.remotedata = {}
        self.load_remotedata()

        self.path_local_saved = self.path_local_read()

        #self.clear_choices()

        self.taskssave = []
        self.taskscurrent = -1 # -1 ready to run # -2 disabled # 0 running first task ...
        if os.path.isfile(os.path.join(self.path_exe,os.pardir,config.DIR_IMAGES,u'icon.'+self.title+'.xpm')):
            ico = wx.Icon(os.path.join(self.path_exe,os.pardir,config.DIR_IMAGES,u'icon.'+self.title+'.xpm'), wx.BITMAP_TYPE_XPM)
	else:
            ico = wx.Icon(os.path.join(self.path_exe,os.pardir,config.DIR_IMAGES,u'icon.opennum.xpm'), wx.BITMAP_TYPE_XPM)
        self.SetIcon(ico)

        self.splitterB = wx.SplitterWindow(self, -1)
        self.splitterA = wx.SplitterWindow(self.splitterB, -1)
        self.panelA = PanelWidgets.PanelWidgets(self.splitterA, self)
        self.panelB = PanelVisual.PanelVisual(self.splitterA, self, self.path_exe)
        self.panelC = PanelExec.PanelExec(self.splitterB)
        self.splitterB.SetMinimumPaneSize(80)
        self.splitterB.SetSashGravity(1.0)
        #self.splitterB.SetSashPosition(400)
        self.splitterB.SplitHorizontally(self.splitterA, self.panelC, self.window_height)
        self.splitterA.SetMinimumPaneSize(100)
        self.splitterA.SplitVertically(self.panelA, self.panelB, self.splitterA_size)
# ...
        self.splitterA.Layout()
        self.splitterB.Layout()
        self.Layout()

        self.CreateStatusBar()

        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        self.menu_postload()

        self.logger = Log.Log()
        self.logger.add_logger(self.panelC)

        self.filemanager = FileManager2.FileManager2()
        self.filemanager.set_callback(self.logger.add_text)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.splitterB, 1, wx.EXPAND)
        self.SetSizer(box)
        #self.SetSizerAndFit(box)
        #self.SetMinSize(box.GetMinSize())
        self.SetMinSize((400,300))
        self.SetSize((self.window_width,self.window_height))
	

        self.timer = wx.Timer(self)

        self.Bind(wx.EVT_MENU, self.event_menu)
#        self.Bind(wx.EVT_MENU_OPEN, self.test)
        self.Bind(wx.EVT_CLOSE, self.event_close)
        self.Bind(wx.EVT_END_PROCESS, self.event_end_process)
        self.Bind(wx.EVT_TIMER, self.event_timer)

#carga automatica del ultimo directorio de trabajo
	self.load_lastfolder()							#añadido


    def get_appname(self):
        return self.title



    def errormsg(self, txt):
        #print 'errormsg:', txt #code prior version 0.0.1
        logging.error(txt)
        dialogs.show_error(self, txt)



    def askmsg(self, txt, mode):
        #print 'askmsg:', txt, ':', #code prior version 0.0.1
        if mode == 'yesno':
            res = dialogs.ask_yes_no(self, txt)
        elif mode == 'okcancel':
            res = dialogs.ask_ok_cancel(self, txt)
        else:
            res = False
        #print res #code prior version 0.0.1
        logging.warning('askmsg:'+txt+': '+res)
        return res



    # se existe o directorio apps no directorio home, utilizao, se non, utiliza o suministrado no paquete.
    # agora permite a busqueda noutros directorios. Ex: help
    def calculate_appsdir(self,apps_dir=None):				#modificado
	if apps_dir is None:						#añadido
	    apps_dir = config.DIR_APPS					#añadido
        dirappshome = os.path.join(self.configdir, apps_dir)		#modificado
        if os.path.isdir(dirappshome):					#modificado
            appsdir = dirappshome					#añadido
        else:
            appsdir = os.path.join(self.path_exe, os.pardir, apps_dir) #modificado
        return appsdir



    def interface_separa(self):
        # pseudo separador. provisional
        pos = self.menubar.GetMenuCount()
        menu_sep = wx.Menu()
        self.menubar.Append(menu_sep, u' | ')
        self.menubar.EnableTop(pos, False)



    def interface_all(self):

        self.interface_clear()
        self.interface_pre1()
        self.interface_pre2()
        self.interface_in()
        self.interface_post1()


    def interface_clear(self):
        while self.menubar.GetMenuCount()>0:
            self.menubar.Remove(0)



    def interface_pre1(self):

        self.menu_folder = wx.Menu()

        #item_o = wx.MenuItem(menu_folder, self.ID_OPEN, u'&Open...\tCtrl+F', u'Select a working folder')
	self.item_o = wx.MenuItem(self.menu_folder, self.ID_OPEN, self.folder_name+'\tCtrl+F', u'Select a working folder')#añadido
        self.menu_folder.AppendItem(self.item_o)

	self.menuapp = wx.MenuItem(self.menu_folder, self.ID_NULL, self.applications_name)
        self.menu_folder.AppendItem(self.menuapp)
	self.menuapp.Enable(False)

	self.menusampledata = wx.MenuItem(self.menu_folder, self.ID_NULL, self.sample_data_name)
	self.menu_folder.AppendItem(self.menusampledata)
	self.menusampledata.Enable(False)

        #self.menu_folder.AppendSeparator()

        self.item_q = wx.MenuItem(self.menu_folder, self.ID_EXIT, self.quit_name+u'\tCtrl+Q', u'Exit program')
        self.menu_folder.AppendItem(self.item_q)

        #self.menubar.Append(menu_folder, u'&Folder')
	self.menubar.Append(self.menu_folder, self.project_name)								#añadido



##################################################
#Nuevo menu Application y Sample data
    def load_menuapp(self):

	if self.menuapp is not None and not (self.only_one_app and self.only_one_example):	

	    self.menu_folder.DeleteItem(self.menusampledata)
	    self.menu_folder.DeleteItem(self.item_q)
	    if isinstance(self.menuapp, wx.MenuItem):
		self.menu_folder.DeleteItem(self.menuapp)
		appsdir = self.calculate_appsdir()
		apps = Applications2.Applications2()
		ok = apps.read(appsdir)

		if not ok:
		    self.errormsg(u'Error reading application list')

            	if len(apps.get()) == 1: # one application => load it (1st sample data)		    
		    self.menuapp = wx.MenuItem(self.menu_folder, self.ID_NULL, self.applications_name)
        	    self.menu_folder.AppendItem(self.menuapp)
		    self.menuapp.Enable(False)
		else:
		    self.apps_index = 0

		    self.application = apps.build_application()
		    self.apps_index = self.application.reindex(self.apps_index)
		    self.menuapp = self.build_menu(self.application)
	    	    self.menu_folder.AppendSubMenu(self.menuapp, self.applications_name)

            self.menusampledata = wx.MenuItem(self.menu_folder, self.ID_NULL, self.sample_data_name)
            self.menu_folder.AppendItem(self.menusampledata)
	    self.menusampledata.Enable(False)
	    if not (self.has_app or os.path.exists(config.FILE_MENULOCAL)):
		self.menu_folder.AppendSeparator()
            self.item_q = wx.MenuItem(self.menu_folder, self.ID_EXIT, self.quit_name+u'\tCtrl+Q', u'Exit program')
            self.menu_folder.AppendItem(self.item_q)

# Necesario para que reindexe materials database cuando no existe lastfolder o directorio nuevo
#	    self.menus.reindex(self.apps_index)

##################################################


    def load_menusampledata(self):

	self.menu_folder.DeleteItem(self.menusampledata)
	self.menu_folder.DeleteItem(self.item_q)
	appsdir = self.calculate_appsdir()
	apps = Applications2.Applications2()
	ok = apps.read(appsdir)
	if not ok:
	    self.errormsg(u'Error reading application list')

	self.sample_data = apps.build_sampledata(self.menus.get_name())
	if len(self.sample_data.get_children()) == 1:
	    self.menusampledata = wx.MenuItem(self.menu_folder, self.ID_NULL, self.sample_data_name)
            self.menu_folder.AppendItem(self.menusampledata)
	    self.menusampledata.Enable(False)
	else:
	    self.apps_index = self.sample_data.reindex(self.apps_index)
	    self.menusampledata = self.build_menu(self.sample_data)

	    if apps.has_app(self.menus.get_name()):
	    	self.menu_folder.AppendSubMenu(self.menusampledata, self.sample_data_name + u' ('+self.menus.get_name()+')')
	    else:
	    	self.menu_folder.AppendSubMenu(self.menusampledata, self.sample_data_name)
	self.menu_folder.AppendSeparator()
        self.item_q = wx.MenuItem(self.menu_folder, self.ID_EXIT, self.quit_name+u'\tCtrl+Q', u'Exit program')
        self.menu_folder.AppendItem(self.item_q)

# Necesario para que reindexe materials database cuando no existe lastfolder o directorio nuevo
#	self.menus.reindex(self.apps_index)

##################################################


    def load_menuconfig(self):

	self.menu_folder.DeleteItem(self.item_q)
	self.apps_index = self.config.reindex(self.apps_index)
	if self.config is not None:
	    if len(self.config.get_children()) > 0:
		configmenus = self.config.get_children()
		for ch in configmenus:
		    if ch.get_name() == config.CONFIG_MENU_NAME:
			menuconfig = self.build_menu(ch)
			self.menu_folder.AppendSubMenu(menuconfig, ch.get_name())
			self.item_q = wx.MenuItem(self.menu_folder, self.ID_EXIT, self.quit_name+u'\tCtrl+Q', u'Exit program')
			self.menu_folder.AppendItem(self.item_q)

# Necesario para que reindexe materials database cuando no existe lastfolder o directorio nuevo
#	self.menus.reindex(self.apps_index)

##################################################

    def interface_pre2(self):
	if self.has_folder:
	    self.load_menuapp()
	    if self.has_app or os.path.exists(config.FILE_MENULOCAL):
	    	self.load_menusampledata()
	    if self.config is not None:
		self.load_menuconfig()
	self.menus.reindex(self.apps_index)

###################################################
# Nuevos menus Application, Sample data y Help
# Se añade el flag help para la creacion del menu help

    def build_menu(self,submenus,help=False):					#modificado
        menus = submenus.get_children()
	if True:
            menu_temp = wx.Menu()
            for submenu in submenus.get_children():
                if submenu.is_hidden():
                    continue
                (selected,kind) = False,wx.ITEM_NORMAL
                attribs = submenu.get_attribs()
                if (attribs.get(u'selected') == u'true'):
                    (selected,kind) = True,wx.ITEM_CHECK
#                    (selected,kind) = False,wx.ITEM_RADIO
		    #permite añadir separadores entre subsubmenus
            	if (attribs.get(u'separator') == u'true'):	#añadido
        	    menu_temp.AppendSeparator()			#añadido
		    continue					#añadido
#--------------------------------------------------------------------------------------------------------------------------------------------------------
		#Permite a los submenus mostrar como text el tag title
                if (attribs.get(u'title') == None):                         #añadido
                	item_name = attribs.get(u'name')                    #añadido
                else:                                                       #añadido
                	item_name = attribs.get(u'title')                   #añadido
#--------------------------------------------------------------------------------------------------------------------------------------------------------
                item_sample_temp = wx.Menu()
		# Si es menu help trabajamos con otras ids
		if help:							#añadido
		    submenuid = config.SPACE_MENU				#añadido
		else:								#añadido
		    submenuid = config.SPACE_MENU_DYN				#añadido
		
                item_temp = wx.MenuItem(menu_temp, submenu.get_index() * config.ID_SPACES \
                        + submenuid , item_name, u'select ' + submenu.get_name(), kind)                 #--------------------------------------------------------------------------------------------------------------------------------------------------------
                #Permite visualizar subsubmenus.
                #subitem_temp = wx.Menu()                                #añadido
		subsubmenuAdded = False
                for subsubmenu in submenu.get_children():               #añadido
                    if subsubmenu.is_hidden():                          #añadido
                        continue                                        #añadido
                    if not (isinstance(subsubmenu, SubMenu.SubMenu)):   #añadido
                        continue                                        #añadido
                    (selected,kind) = False,wx.ITEM_NORMAL              #añadido
                    subattribs = subsubmenu.get_attribs()               #añadido
                    if (subattribs.get(u'selected') == u'true'):        #añadido
                        (selected,kind) = True,wx.ITEM_CHECK            #añadido
		    if (subattribs.get(u'separator') == u'true'):	#añadido
			item_sample_temp.AppendSeparator()		#añadido
			continue					#añadido
		#Permite a los submenus mostrar como text el tag title
                    if (subattribs.get(u'title') == None):             	#añadido
                    	subitem_name = subattribs.get(u'name')          #añadido
                    else:                                               #añadido
                    	subitem_name = subattribs.get(u'title')         #añadido
		    # Si es menu help trabajamos con otras ids
		    if help:							#añadido
			subsubmenuid = config.SPACE_MENU			#añadido
		    else:							#añadido
			subsubmenuid = config.SPACE_MENU_DYN			#añadido
                    #subitem_temp.Append(subsubmenu.get_index()*config.ID_SPACES + config.SPACE_MENU_DYN, subitem_name)    # añadido
                    subitem_temp = wx.MenuItem(item_sample_temp, subsubmenu.get_index() * config.ID_SPACES \
                        + subsubmenuid, subitem_name, u'select ' + subsubmenu.get_name(), kind)
                    item_sample_temp.AppendItem(subitem_temp)                  #añadido
		    subsubmenuAdded = True

                #---------------------------------------------------------------------------------------------------------------------------------------------------------
                if subsubmenuAdded:
                    menu_temp.AppendSubMenu(item_sample_temp, item_name)
		else:
		    menu_temp.AppendItem(item_temp)

	return menu_temp



    def interface_in(self):
        self.menulast = [] # for materials database
        menus = self.menus.get_children()
        for menu in menus:
            if menu.is_hidden():
                continue
	    menuattribs = menu.get_attribs()
	    # permite añadir separadores entre menus			
	    if (menuattribs.get(u'separator') == u'true'):		#añadido
#		pos = self.menubar.GetMenuCount()			#añadido
#        	menu_sep = wx.Menu()					#añadido
#        	self.menubar.Append(menu_sep, u'|')			#añadido
#		self.menubar.EnableTop(pos, False)			#añadido
		self.interface_separa()
		continue						#añadido
            menu_temp = wx.Menu()

            for submenu in menu.get_children():
                if submenu.is_hidden():
                    continue
                (selected,kind) = False,wx.ITEM_NORMAL
                attribs = submenu.get_attribs()
		#permite añadir separadores entre submenus
            	if (attribs.get(u'separator') == u'true'):		#añadido
        	    menu_temp.AppendSeparator()				#añadido
		    continue						#añadido
                if (attribs.get(u'selected') == u'true'):
                    (selected,kind) = True,wx.ITEM_CHECK
#                    (selected,kind) = False,wx.ITEM_RADIO
#-------------------------------------------------------------------------------------
		#Permite a los submenus mostrar como text el tag title
                if (attribs.get(u'title') is None):                         #añadido
                	item_name = attribs.get(u'name')                    #añadido
                else:                                                       #añadido
                	item_name = attribs.get(u'title')                   #añadido
#-------------------------------------------------------------------------------------
                item_temp = wx.MenuItem(menu_temp, submenu.get_index() * config.ID_SPACES + \
                        config.SPACE_MENU_DYN, item_name, u'select ' + submenu.get_name(), kind)

                 #--------------------------------------------------------------------
                #Permite visualizar subsubmenus.
                subitem_temp = wx.Menu()                                #añadido
                subitemAdded = False                                    #añadido
                for subsubmenu in submenu.get_children():               #añadido
                    if subsubmenu.is_hidden():                          #añadido
                        continue                                        #añadido
                    if not (isinstance(subsubmenu, SubMenu.SubMenu)):   #añadido
                        continue                                        #añadido
                    (selected,kind) = False,wx.ITEM_NORMAL              #añadido
                    subattribs = subsubmenu.get_attribs()               #añadido
		    #permite añadir separadores entre subsubmenus
            	    if (subattribs.get(u'separator') == u'true'):	#añadido
        	    	subitem_temp.AppendSeparator()			#añadido
		    	continue					#añadido
                    if (subattribs.get(u'selected') == u'true'):        #añadido
                        (selected,kind) = True,wx.ITEM_CHECK            #añadido
		#Permite a los submenus mostrar como text el tag title
                    if (subattribs.get(u'title') == None):             	#añadido
                    	subitem_name = subattribs.get(u'name')          #añadido
                    else:                                               #añadido
                    	subitem_name = subattribs.get(u'title')         #añadido
                    subitem_temp.Append(subsubmenu.get_index()*config.ID_SPACES + config.SPACE_MENU_DYN, subitem_name)    # añadido
                    subitemAdded = True                                 #añadido
                if subitemAdded:                                        #añadido
                    item_temp.SetSubMenu(subitem_temp)                  #añadido
                #---------------------------------------------------------------------
                
                menu_temp.AppendItem(item_temp)
                if (selected): # this must go after preceding line
                    item_temp.Check()
            if ((menu.get_name() == self.materialsdb_name) or (menu.get_name() == self.materialsdb_name[1:])): # ou outra comprobación
                self.menulast.append( (menu_temp, u'&'+menu.get_name()) )
		self.MaterialsDB_exists = True				#añadido
	    elif menu.get_name() == config.NAME_CONFIG_FILE:
                self.menulast.append( (menu_temp, u'&'+menu.get_name()) )
		self.Configfile_exists = True				#añadido
            else:
                self.menubar.Append(menu_temp, u'&'+menu.get_name())

# Construccion del menu Help al estilo Apps y Sample data
    def load_menuhelp(self):					#añadido
	helpdir = self.calculate_appsdir(config.DIR_DOCS)	#añadido
	apps = Applications2.Applications2()			#añadido	
	ok = apps.read(helpdir)					#añadido
	if not ok:						#añadido
	    self.errormsg(u'Error reading application list')	#añadido
	
	self.menu_help = apps.build_help()			#añadido'
	if len(self.menu_help.get_children()) == 0:		#añadido
	    menuhelpwx = None					#añadido
	else:							#añadido
	    if self.apps_index < self.MIN_PROTECTED_ID:
		index = self.MIN_PROTECTED_ID
	    else:
		index = self.apps_index
	    self.menu_help.reindex(index)			#añadido
	    menuhelpwx = self.build_menu(self.menu_help,help=True)#añadido
	return menuhelpwx					#añadido


    def interface_post1(self):
# Construccion del menu Help al estilo Apps y Sample data
	menuhelpwx = self.load_menuhelp()			#añadido
	if menuhelpwx is not None:				#añadido
            self.menubar.Append(menuhelpwx, self.help_name)		#añadido

        # pseudo separador. provisional
        if len(self.menulast) > 0:
            self.interface_separa()
    
        # provisional
        for menu in self.menulast:
            self.menubar.Append(menu[0], menu[1]) # 0 menu 1 name

        self.menulast = []

#        menu_help = wx.Menu()
#        item_h5 = wx.MenuItem(menu_help, self.ID_HELP5, u'&Getting Started', u'HTML documentation about getting started with the application')
#        menu_help.AppendItem(item_h5)
#        item_h4 = wx.MenuItem(menu_help, self.ID_HELP4, u'Graphical &Interface', u'HTML documentation about MaxFEM GUI')
#        menu_help.AppendItem(item_h4)
#        item_h3 = wx.MenuItem(menu_help, self.ID_HELP3, u'&User guide', u'HTML user guide')
#        menu_help.AppendItem(item_h3)
#        item_h2 = wx.MenuItem(menu_help, self.ID_HELP2, u'&Applications', u'HTML documentation of applications')
#        menu_help.AppendItem(item_h2)
#        item_h1 = wx.MenuItem(menu_help, self.ID_HELP1, u'&Math models', u'HTML documentation about math models')
#        menu_help.AppendItem(item_h1)
#        item_h3 = wx.MenuItem(menu_help, self.ID_HELP3, u'&Test PDF', u'PDF documentation test')
#        menu_help.AppendItem(item_h3)
#        menu_help.AppendSeparator()
#        item_h = wx.MenuItem(menu_help, self.ID_ABOUT, u'Abou&t', u'HTML authoring and basic information about MaxFEM')
#        menu_help.AppendItem(item_h)
#        item_h = wx.MenuItem(menu_help, self.ID_ABOUT, u'&About', u'About this program')
#        menu_help.AppendItem(item_h)

        # pseudo separador. provisional
        #if len(self.menulast) > 0:
        #    self.interface_separa()


    def process_pending(self):
        #wx.App.SafeYield()
        wx.SafeYield()



    def retitle(self):
        txt = self.title
        if self.menus.is_loaded():
            txt += u' - ' + self.menus.get_name()
        if isinstance(self.path_local, basestring):
            txt += u' - ' + self.path_local
        self.SetTitle(txt)



    def path_local_set(self, newpath):
        # o solo si no falla ?
#        clears buffers. here and in menu_load
        self.filemanager.clear()
        # forgets plot association
        self.panelB.forget()
        
        try:
            if newpath is None:
                os.chdir(self.path_exe)
            else:
                os.chdir(newpath)
        except OSError:
            self.errormsg(u'Error changing current working directory')
            return False
        self.path_local = newpath
        #print u'path_local', self.path_local #code prior version 0.0.1
        logging.debug(u'path_local'+self.path_local)
        self.retitle()

        # para almacenalo para a proxima execución
        self.path_local_write(self.path_local)

        return True



    def path_local_get(self):
        if (isinstance(self.path_local,basestring)):
            return self.path_local
        else:
            return u""


            
    def path_local_read(self):
        path = None
        if self.path_local_save_filename is not None:
            try:
                #file1 = open(self.path_local_save_filename, "r") # lia mal
                file1 = codecs.open(self.path_local_save_filename, encoding='utf-8')
                path = file1.read()
                file1.close()
            except IOError:
                print 'PATH_READ_FAILED'
                pass
            #print 'PATH_READ', path #code prior version 0.0.1
            logging.debug('PATH_READ'+path)
        return path




    def path_local_write(self, path):
        if self.path_local_save_filename is not None:
            #print 'PATH_WRITE', path #code prior version 0.0.1
            logging.debug('PATH_WRITE'+path)
            try:
                file1 = open(self.path_local_save_filename,"w")
                file1.write(path.encode('utf-8'))
                file1.close()
            except IOError:
                print 'PATH_WRITE_FAILED'
                pass

    def reset_config(self):
        if dialogs.ask_ok_cancel(self, 'If you continue, your configuration file copy will be reset, all changes you made to it will be lost.'):
            self.copy_config(True)
            self.load_config()
            self.menu_postload(False) # false => does not test mesh existence


    def copy_config(self, force=False):
        try:
            if self.path_local_config is not None:
                if force or not os.path.exists(self.path_local_config):
                    #print u'Copying configuration file to:', self.path_local_config, '...' #code prior version 0.0.1
                    logging.debug(u'Copying configuration file to:'+self.path_local_config+'...')
                    if not os.path.exists(self.path_local_config_dir):
                        try:
                            os.mkdir(self.path_local_config_dir)
                        except OSError, e:
                            print 'Error creating materials directory:', e

                    from_file1 = os.path.join(self.path_exe, os.pardir, config.DIR_CONFIG, config.FILE_CONFIG)
                    from_file2 = os.path.join(self.path_exe, os.pardir, config.DIR_CONFIG, config.FILE_CONFIG_PREFIX + self.title + config.FILE_CONFIG_SUFFIX)
                    
                    if os.path.exists(from_file1):
                        from_file = from_file1
                    else:
                        if os.path.exists(from_file2):
                            from_file = from_file2
                        else:
                            #self.errormsg(u'Error copying materials database to local folder. '+\
                #'File not found. Some funcionality may be affected.')
			    #print u'Error copying configuration file to local folder. '+\
                #'File not found. Some funcionality may be affected.' #code prior version 0.0.1
                            logging.warning(u'Error copying configuration file to local folder. File not found. Some funcionality may be affected.')
                            return

                    shutil.copy2( from_file, self.path_local_config )
        except (IOError, shutil.Error, OSError), err:
            print repr(err)
            self.errormsg(u'Error copying materials database to local folder. '+\
                'Some funcionality may be affected');


    def load_config(self):
        ok = True
	    #print self.path_local_config #code prior version 0.0.1
        logging.debug(self.path_local_config)
        if self.path_local_config is not None:
            menuconfig = Menus.Menus(self)
            ok &= menuconfig.load_file(self.path_local_config)
            if ok:
                self.config = menuconfig
        else:
            ok &= False
        return ok








    def save_config(self):
        if self.config is not None and self.path_local_config is not None:
            # True: force: para que o garde ainda que un atributo indique o contrario
            self.config.save_menu(self.path_local_config, True)
	    self.apply_config()
            # BUG: working dir not set. consider other conditions
#            if self.path_local is not None:
#                self.config.save_data(config.FILE_CONFIG_DAT, force=True)


    def init_config(self):
	self.languaje = u'English'
	self.project_name = u'&Project'
	self.folder_name = u'Select folder'
	self.applications_name = u'Applications'
	self.sample_data_name = u'Sample data'
	self.quit_name = u'&Quit'
	self.help_name = u'&Help'
	self.materialsdb_name = u'&Help'
	self.maximize_window = False
	self.warning_on_load = True
	self.splitterA_size = 240
	self.window_width = 900
	self.window_height = 600









    def apply_config(self):
	if self.config is None 	or not self.apply_config_flag:
	    return

	for menuch in self.config.get_children():
# Config file interface options
	    if menuch.get_name() == config.CONFIG_MENU_NAME:
		for submenuch in menuch.get_children():
		    if submenuch.get_name() == config.CONFIG_SUBMENU_NAME:
			for structch in submenuch.get_children():
			    if structch.get_name() == config.CONFIG_STRUCT_NAME:
				for ch in structch.get_children():
				    try:
					#Maximized at start: yes/no
					if ch.get_name() == config.CONFIG_MAXIMIZE_OPTION:
					    prop = ch.get_elements_selected()[0]
					    self.maximize_window = (prop.lower() == config.VALUE_YES)
					#Enabled warning dialog when load app or example: yes/no
					elif ch.get_name() == config.CONFIG_WARNONLOAD_OPTION:
					    prop = ch.get_elements_selected()[0]
					    self.warning_on_load = (prop.lower() == config.VALUE_NO)
					#Run GUI in verbose mode: yes/no
					elif ch.get_name() == config.CONFIG_VERBOSE_OPTION:
					    prop = ch.get_elements_selected()[0]
					    if prop.lower() == config.VALUE_YES:
					        #Both logging.info and logging.debug will be printed
					        logging.getLogger().setLevel(logging.DEBUG)
					    else:
					        #Only logging.info will be printed
					        logging.getLogger().setLevel(logging.INFO)
					    #sh = logging.StreamHandler()
					    #sh.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
					    #logging.getLogger().addHandler(sh)
					#Set PanelWidgets size
					elif ch.get_name() == config.CONFIG_WIDGETS_PANEL_SIZE:
					    self.splitterA_size = int(ch.get_elements()[0])
					    #cambia en el aire.
					    self.splitterA.SetSashPosition(self.splitterA_size, redraw=True)
					#Set Window size
					elif ch.get_name() == config.CONFIG_WINDOW_SIZE:
					    for wsch in ch.get_children():
						if wsch.get_name() == config.CONFIG_WINDOW_WIDTH:
						    self.window_width = int(wsch.get_elements()[0])
						if wsch.get_name() == config.CONFIG_WINDOW_HEIGHT:
						    self.window_height = int(wsch.get_elements()[0])
					    #cambia en el aire
					    self.SetSize((self.window_width,self.window_height))
				    except:
					pass
# Config file internationalization options
	    elif menuch.get_name() == config.CONFIG_INTERNACIONALIZATION:	
		for submenuch in menuch.get_children():
		    if submenuch.get_name() == self.languaje:
			for structch in submenuch.get_children():
			    if structch.get_name() == u'Project':
				for ch in structch.get_children():
				    elementlist = ch.get_elements()
				    if ch.get_name() == u'Project':
					if len(elementlist) > 0:
					    self.project_name = ch.get_elements()[0]
				    elif ch.get_name() == u'Folder':
					if len(elementlist) > 0:
					    self.folder_name = ch.get_elements()[0]
				    elif ch.get_name() == u'Applications':
					if len(elementlist) > 0:
					    self.applications_name = ch.get_elements()[0]
				    elif ch.get_name() == u'Sample data':
					if len(elementlist) > 0:
					    self.sample_data_name = ch.get_elements()[0]
				    elif ch.get_name() == u'Quit':
					if len(elementlist) > 0:
					    self.quit_name = ch.get_elements()[0]
			    if structch.get_name() == u'Help':
				for ch in structch.get_children():
				    if ch.get_name() == u'Help':
					self.help_name = ch.get_elements()[0]
			    if structch.get_name() == u'Materials':
				for ch in structch.get_children():
				    if ch.get_name() == u'Database':
					self.materialsdb_name = ch.get_elements()[0]



    def reset_materials(self):
        if dialogs.ask_ok_cancel(self, 'If you continue, your materials database copy will be reset, all changes you made to it will be lost.'):
            self.copy_materials(True)
            self.load_materials()
            self.menu_postload(False) # false => does not test mesh existence


    def copy_materials(self, force=False):
        try:
            if self.path_local_materials is not None:
                if force or not os.path.exists(self.path_local_materials):
                    #print u'Copying materials to:', self.path_local_materials, '...' #code prior version 0.0.1
                    logging.debug(u'Copying materials to:'+self.path_local_materials+'...')
                    if not os.path.exists(self.path_local_materials_dir):
                        try:
                            os.mkdir(self.path_local_materials_dir)
                        except OSError, e:
                            print 'Error creating materials directory:', e

                    from_file1 = os.path.join(self.path_exe, os.pardir, config.DIR_MATERIALS, config.FILE_MATERIALS)
                    from_file2 = os.path.join(self.path_exe, os.pardir, config.DIR_MATERIALS, config.FILE_MATERIALS_PREFIX + self.title + config.FILE_MATERIALS_SUFFIX)
                    
                    if os.path.exists(from_file1):
                        from_file = from_file1
                    else:
                        if os.path.exists(from_file2):
                            from_file = from_file2
                        else:
                            #self.errormsg(u'Error copying materials database to local folder. '+\
                            #'File not found. Some funcionality may be affected.')
                            #print u'Error copying materials database to local folder. '+\
                            #'File not found. Some funcionality may be affected.' #code prior version 0.0.1
                            logging.warning(u'Error copying materials database to local folder. File not found. Some funcionality may be affected.')
                            return

                    shutil.copy2( from_file, self.path_local_materials )
        except (IOError, shutil.Error, OSError), err:
            print repr(err)
            self.errormsg(u'Error copying materials database to local folder. '+\
                'Some funcionality may be affected');



    def load_materials(self):
        ok = True
        if self.path_local_materials is not None:
            menumaterials = Menus.Menus(self)
            ok &= menumaterials.load_file(self.path_local_materials)
            if ok:
                self.materials = menumaterials
        else:
            ok &= False
        return ok



    def save_materials(self):
        if self.materials is not None and self.path_local_materials is not None:
            # True: force: para que o garde ainda que un atributo indique o contrario
            self.materials.save_menu(self.path_local_materials, True)

            # BUG: working dir not set. consider other conditions
            if self.path_local is not None:
                self.materials.save_data(config.FILE_MATERIALS_DAT, force=True)


                
    def reset_materials(self):
        if dialogs.ask_ok_cancel(self, 'If you continue, your materials database copy will be reset, all changes you made to it will be lost.'):
            self.copy_materials(True)
            self.load_materials()
            self.menu_postload(False) # false => does not test mesh existence



    def get_extra(self, prefix=''):
        # leaf for solver to know where materials are
        l = Leaf.Leaf()
        l.set_name(u'materialsDB')
        l.tag = u'leaf'
        l.get_attribs()[u'type'] = u'file'
        #l.set_elements_nosel([self.path_local_materials])
        l.set_elements_nosel([prefix+config.FILE_MATERIALS_DAT])

        s = SubMenu.SubMenu()
        s.tag = u'submenu'
        s.set_name(u'Open')
        s.add_child(l)

        m = Menu.Menu()
        m.tag = u'menu'
        m.set_name(config.NAME_MATERIALS_FILE)
        m.add_child(s)

        return m



    def save_all(self):
        extra = [self.get_extra()]

        self.menus.save_menu()
        self.menus.save_data(extras=extra)
        self.save_materials()
	self.save_config()



    # load the current working dir
    def menu_load(self, changed):
#        clears buffers. here and in path_local_set
        self.filemanager.clear()
        # forgets plot association
        self.panelB.forget()
        
        file_to = config.FILE_MENULOCAL
        #print 'load', file_to #code prior version 0.0.1
        logging.debug('load'+file_to)
        ok = True
        newmenu = Menus.Menus(self)
        result = newmenu.load_file(file_to)
        if not result:
            #emitted in menus.load_file
            #self.errormsg(u'Error loading menu file')
            ok = False
        else:
            if changed is True:
		self.logger.end()
                self.logger.change()
                name = newmenu.get_name()
		self.logger.start(name)
            else:
                self.logger.add_text(u'Menu updated!' + u'\n')
                name = None
            self.menus = newmenu
            self.menu_postload()
        return ok



    def menu_postload(self, hard=False):

            # adds apps tree
#Eliminado: antiguo menu Application
#            if self.apps2 is not None: # poñer aqui todo !!!
#                tree = self.apps2.build_menu()
#                self.menus.del_childs_by_name(tree.get_name()) # whithout this, Materials Database Reset increments the number of menu items
#                self.menus.add_child_start(tree)
#                self.menus.reindex()
                #self.menus.set_children_parents() # test. non solucionou o crash

            # add materials tree
            if self.materials is not None:
                for ch in self.materials.get_children(): # normalmente só hai un
                    # para que non o garde co menu
                    # pero asi non o garda o materials tampouco! [ agora si: force=True en Menus.save_menu ]
                    ch.get_attribs()[config.AT_SAVETHIS] = config.VALUE_FALSE # pasar a get_data() ?
                    # para leaf folder file que garde rutas absolutas
                    ch.get_data()[config.IS_MATERIALS] = True
                    self.menus.del_childs_by_name(ch.get_name()) # whithout this, Materials Database Reset increments the number of menu items
                    self.menus.add_child(ch) # resets parent of ch
		#self.menus.reindex(self.apps_index)
# Config menu en la barra de menús
#            if self.config is not None:
#                for ch in self.config.get_children(): # normalmente só hai un
#                    # para que non o garde co menu
#                    # pero asi non o garda o materials tampouco! [ agora si: force=True en Menus.save_menu ]
#                    ch.get_attribs()[config.AT_SAVETHIS] = config.VALUE_FALSE # pasar a get_data() ?
#                    # para leaf folder file que garde rutas absolutas
#                    ch.get_data()[config.IS_CONFIG] = True
#                    self.menus.del_childs_by_name(ch.get_name()) # whithout this, Materials Database Reset increments the number of menu items
#                    self.menus.add_child(ch) # resets parent of ch
		#self.menus.reindex(self.apps_index)
	    self.menus.reindex(self.apps_index)

            self.interface_all()
            self.retitle()

            #print "datafile", self.menus.get_datafile() #code prior version 0.0.1
            logging.debug("datafile"+self.menus.get_datafile())
            #print "to_save", self.menus.to_save() #code prior version 0.0.1
            logging.debug("to_save"+str(self.menus.to_save()))

            if hard:
                # test existence of files and folders
                errors = self.menus.pretest()
                if len(errors)>0:
                    self.errormsg('\n'.join(errors))

            # preload mesh files
            # desactualizado en Leaf.py
            #errors = self.menus.preload()
            #if len(errors)>0:
            #    self.errormsg('\n'.join(errors)+'\n\n*Not changing files*')


            

    # chamado desde panelWidgets.add_widget en caso de copymenu
    # return value: True: copyed ; False: not copyed ; None: error
    def menu_copy_load(self, dirs):
        #print 'menu_copy_load', dirs #code prior version 0.0.1
        logging.debug('menu_copy_load'+dirs)
        ret = None
        if self.warning_on_load or dialogs.ask_ok_cancel(self, 'If you continue, some files in the current working folder may be overwritten'):
            # cerra log
            # para que non falle ao intentar borrar un arquivo aberto
            self.logger.end()

            # limpa widgets
            # CRASH
            # self.panelA.display_set(None) # limpa widget que hai
            if self.menu_copy2(dirs):
                if self.menu_load(True):
                    ret = True
        else:
            ret = False
        # CRASH
        # self.panelA.display_set(None)
        return ret



    def remove_file_folder(self, name):
        ok = True

        try:
            if os.path.exists(name):
                if os.path.isdir(name):
                    shutil.rmtree(name)
                else:
                    os.unlink(name)
        except (IOError, shutil.Error, OSError), err:
            ok = False
            print repr(err)
            self.errormsg(u'Error erasing data (' + name + ') from working folder')
            
        return ok
    
        

#    def menu_erase2(self): # DANGER!!!
#        # should remove all files and directories in current directory
#        ok = True
#
#        try:
#            files = os.listdir(u'.')
#            print 'borrando', files
#            for file in files:
#                if os.path.isdir(file):
#                    shutil.rmtree(file)
#                else:
#                    os.unlink(file)
#        except (IOError, shutil.Error, OSError), err:
#            ok = False
#            print repr(err)
#            self.errormsg(u'Error erasing data from working folder')
#
#        return ok


    def menu_copy2(self, dirs):
        ok = True
    
#    #    # ok = self.menu_erase2() # DANGER!!!
        
        if ok is False:
            return ok

        dir_from = os.path.join(self.appsdir, dirs)
        dir_to = u'.'

        #print 'copy', dir_from, "->", dir_to #code prior version 0.0.1
        logging.debug('copy'+dir_from+"->"+dir_to)

        try:

            files1 = os.listdir(dir_from)
            
            # avoid .hidden files
            files2 = []
            dirs2 = []

            for file in files1:
                if len(file) > 0 and file[0]!=u'.':
                    if os.path.isdir(os.path.join(dir_from, file)):
                        dirs2.append(file)
                    else:
                        files2.append(file)

            #print 'copiando files', files2 #code prior version 0.0.1
            logging.debug('copiando files'+''.join(files2))
            #print 'copiando dirs', dirs2 #code prior version 0.0.1
            logging.debug('copiando dirs'+''.join(dirs2))
        
            for file in files2:
                file_from = os.path.join(dir_from, file)

                affected = os.path.join(dir_to, file)
                if not self.remove_file_folder(affected):
                    ok = False
                    return ok

                shutil.copy2( file_from , dir_to )
            for dir in dirs2:
                subdir_from = os.path.join(dir_from, dir)
                subdir_to = os.path.join(dir_to, dir)
		if os.path.isdir(subdir_to):
		    shutil.rmtree(subdir_to)
                affected = os.path.join(dir_to, dir)
                if not self.remove_file_folder(affected):
                    ok = False
                    return ok
                shutil.copytree( subdir_from , subdir_to )
        except (IOError, shutil.Error, OSError), err:
            ok = False
            #print repr(err)
	    self.errormsg(u'Error copying '+subdir_to+' to working folder.\n'+repr(err)+u': ')

        return ok



    def event_folder(self):
        # se nesta execución non seleccionou un folder, aparece seleccionado o último da anterior execución
	self.has_app = False					#añadido
        if self.path_local is None:
            temp = self.path_local_saved
            if temp is None:
                temp = u''
        else:
            temp = self.path_local_get()

        path_new = dialogs.get_folder(self,temp)
        if path_new is not None:
            if self.path_local_set(path_new):
		self.has_folder = True   			#añadido
                self.logger.end()				#añadido
                self.menus = Menus.Menus(self)			#añadido

                if os.path.exists(config.FILE_MENULOCAL):	#añadido
		    if not self.menu_load(True):		#añadido
			self.menu_postload()			#añadido
		    return True					#añadido
                # in case of failure				#añadido
		else:
	    	    appsdir = self.calculate_appsdir()
	    	    apps = Applications2.Applications2()
	    	    ok = apps.read(appsdir)
	    	    if not ok:
			self.errormsg(u'Error reading application list')
            	    if len(apps.get()) == 1: # one application => load it
			self.only_one_app = True
		    	#if len(apps.get()[0][3]) == 1: # one example => load it
			if True: # one application => load 1st example
			    self.only_one_example = True
                    	    if self.menu_copy2(apps.get()[0][2]+u'/'+apps.get()[0][3][0][2]):
                            	if self.menu_load(True):
                                    return True
                self.menu_postload()				#añadido
        return False
       
#test
# comentado para que cargue cada vez
#                if self.apps2 is None:
# Comentado: antiguo menu Application
#                self.appsdir = self.calculate_appsdir()
#                self.apps2 = Applications2.Applications2()
#                ok = self.apps2.read(self.appsdir)
#                if not ok:
#                    self.errormsg(u'Error reading application list')
#test
#                if os.path.exists(config.FILE_MENULOCAL):
#                self.logger.end()
#                self.menus = Menus.Menus(self)
#                if os.path.exists(config.FILE_MENULOCAL):
#                    if self.menu_load(False):
#                        return True
# Comentado: antiguo menu Application
#                else:
		#Si existe solo una aplicacion
#                    if len(self.apps2.get()) == 1: # one application => load it				#añadido
#			print self.apps2.get()[0][3]							#añadido
#			if len(self.apps2.get()[0][3]) == 1:						#añadido
#                            if self.menu_copy2(self.apps2.get()[0][2]+u'/'+self.apps2.get()[0][3][0][2]):#añadido
#                            	if self.menu_load(True):						#añadido
#                                	return True							#añadido
#                    else:										#añadido
#                        self.menu_postload()
#                        return True



#Carga automatica del ultimo directorio de trabajo
    def load_lastfolder(self):							#añadido
	path_new = None								#añadido
	path_file_lf = os.path.join(self.configdir, config.FILE_LASTFOLDER)	#añadido
	if os.path.exists(path_file_lf) and self.configdir is not None:		#añadido
	    self.path_local_save_filename = path_file_lf			#añadido
	    file1 = codecs.open(self.path_local_save_filename, encoding='utf-8')#añadido
            path_new = file1.read()						#añadido
            file1.close()							#añadido
            #print path_new							#añadido #code prior version 0.0.1
            logging.debug(path_new)
            if path_new is not None and os.path.exists(path_new):		#añadido
        	if self.path_local_set(path_new):  				#añadido
		    self.has_folder = True					#añadido
# carga del menu applications        
# comentado para que cargue cada vez		
#                if self.apps2 is None:						#añadido
# Comentado: antiguo menu Application
#        	    self.appsdir = self.calculate_appsdir()			#añadido
#		    self.apps2 = Applications2.Applications2()			#añadido
#		    ok = self.apps2.read(self.appsdir)				#añadido
#		    if not ok:							#añadido
#			self.errormsg(u'Error reading application list')	#añadido
		    self.logger.end()						#añadido
		    self.menus = Menus.Menus(self)				#añadido
		    if os.path.exists(config.FILE_MENULOCAL):			#añadido
			if self.menu_load(True):				#añadido
			    self.has_app = True
			    return True						#añadido
# en caso de error
		    self.menu_postload()					#añadido
        return False



    def event_close(self, event):
        #print u"closing [x]" #code prior version 0.0.1
        logging.debug(u"closing [x]")
        self.panelA.display_set(None) # save mem
        self.logger.end()
        self.save_all() # menu data materials

        #        self.menu_choice()

        self.panelB.rem() # non funciona (ocupado?)

        event.Skip()



    def event_menu(self, event):
        id = event.GetId()

        if (id % config.ID_SPACES == config.SPACE_MENU):
            if (id==self.ID_EXIT):
                self.Close()
                return # this way does not save 2 times on menu exit

        self.panelA.display_set(None) # save mem
        self.save_all() # menu data materials
#        self.menu_choice()
	self.apply_config_flag = False

        if (id % config.ID_SPACES == config.SPACE_MENU):
            index = id // config.ID_SPACES

            if (id==self.ID_EXIT):
                self.Close()
            elif (id==self.ID_OPEN):
                result = self.event_folder()
            elif (id==self.ID_TDEL):
                self.panelB.rem()
            elif (id==self.ID_DUMP):
                self.menus.dump()
            elif (id==self.ID_SAVE):
                # protexer de salvar sen directorio de traballo
                self.menus.save_data()
	    else:
		try:
		    submenu = self.menu_help.get_index( index )
		except:
		    submenu = None
		# Control de eventos del menu Help al estilo Apps y Sample data
		if submenu is not None:							#añadido
		    if submenu.get_attribs()[config.AT_HELP] == config.VALUE_TRUE:	#añadido
			try:								#añadido
			    dirname = submenu.get_attribs()[config.AT_SOURCE]		#añadido
			except:								#añadido
			    dirname = submenu.get_attribs()[u'name']			#añadido
			if not self.launch_auto(os.path.join(dirname, u'index.xhtml')):	#añadido
			    if not self.launch_auto(os.path.join(dirname, u'index.html')):#añadido
				if not self.launch_auto(os.path.join(dirname, u'index.htm')):#añadido
				    self.errormsg(u'File '+dirname+u'/'+u'index.[xhtml | html | htm] not exists.')#añadido
##############################################################33
# Deprecated actions
#            elif (id==self.ID_VADD):
#                self.panelB.add_p()
#            elif (id==self.ID_MADD):
#                self.panelB.add_m()
#            elif (id==self.ID_MESHES):
#                self.aux_meshes()
#            elif (id==self.ID_MACTION):
#                self.panelB.maction()
#            elif (id==self.ID_ABOUT):
#                dialogs.about(self.title, self.path_exe)
#                self.launch_auto(os.path.join(u'About',u'index.html'), False)
#        item_h3 = wx.MenuItem(menu_help, self.ID_HELP3, u'&Test PDF', u'PDF documentation test')
#        menu_help.AppendItem(item_h3)
#            elif (id==self.ID_HELP1):
#                self.launch_auto(os.path.join(u'Math_models',u'index.html'), False)
#            elif (id==self.ID_HELP2):
#                self.launch_auto(os.path.join(u'apps',u'index.html'))
#            elif (id==self.ID_HELP3):
#		self.launch_auto(os.path.join(u'User_guide',u'index.html'))
#            elif (id==self.ID_HELP4):
#		self.launch_auto(os.path.join(u'interface',u'index.html'))
#            elif (id==self.ID_HELP5):
#		self.launch_auto(os.path.join(u'Getting_Started',u'index.html'))
#                #self.launch_auto(u'sample.pdf')
#        elif (id % config.ID_SPACES == config.SPACE_MENU_APP):
#
#            index = id // config.ID_SPACES
#            result = self.copy_mnu(self.apps.get_filename(index))

        elif (id % config.ID_SPACES == config.SPACE_MENU_DYN):

            index = id // config.ID_SPACES
            submenu = self.menus.get_index( index )
	    if submenu is None:
		if self.application is not None:
		    submenu = self.application.get_index( index )
		if submenu is None:
		    if self.sample_data is not None:
		        submenu = self.sample_data.get_index( index )
		if submenu is None:
		    if self.config is not None:
			submenu = self.config.get_index( index )
			self.apply_config_flag = True
            if (submenu is None):
                #print index, id #code prior version 0.0.1
                logging.debug(index+str(id))
            else:
                #print index, id, submenu.get_name() #code prior version 0.0.1
                logging.debug(str(index)+str(id)+submenu.get_name())
		#Carga de las aplicaciones
		copyvalue = submenu.get_attribs().get(config.AT_COPY)		#añadido
            	if copyvalue is not None:					#añadido
                    if self.menu_copy_load(copyvalue):				#añadido
			if not self.has_app:
		            self.has_app = True					#añadido
			    self.interface_all()				#añadido

                actions = submenu.get_actions()
                for action in actions:
                    name = action.get(u'name')
                    self.reload_menu = action.get(u'reload') == config.VALUE_TRUE
                    #params = action.get('params')
#                    if action[0] == u'copymnu' and len(action)>=2:
#                        result = self.copy_mnu(action[1])
                    if name == u'exec':
                        self.menu_exec2(action)
                    elif name == u'exec_custom':
                        self.menu_exec_custom(action)
                    elif name == u'exec_ssh':
                        self.menu_exec_ssh(action)
                    elif name == u'kill_exec':
                        self.menu_kill()
                    elif name == u'close_plots':
                        self.panelB.rem()
                    elif name == u'reset_materials':
                        self.reset_materials()
                    elif name == u'reset_config':
                        self.reset_config()
                    else:
                        self.errormsg(u'Unknown action: ' + name)
                children1 = submenu.get_children()
                children2 = [] # not hidden children
                for c in children1:
                    if not c.is_hidden():
                        children2.append(c)
                num = len(children2)
                display = None
                if num == 1:
                    display = children2[0]
                    self.panelA.display_set(display)


#Se añade control de lanzamiento
    def launch_auto(self, path, allow_home=True):
        path1 = os.path.abspath(os.path.join(self.configdir,config.DIR_DOCS,path))
        path2 = os.path.abspath(os.path.join(self.path_exe,os.pardir,config.DIR_DOCS,path))
        if allow_home and os.path.exists(path1):
#            if os.name == 'nt':
#                self.launch(path1)
#            else:
#                self.launch('file://'+path1)
            self.launch('file:///'+path1)
	    return True					#añadido
        elif os.path.exists(path2):
#            if os.name == 'nt':
#                self.launch(path2)
#            else:
#                self.launch('file://'+path2)
            self.launch('file:///'+path2)
	    return True					#añadido
	return False					#añadido



    def launch(self, url, opt=None):
        #print 'launching', url #code prior version 0.0.1
        logging.debug('launching'+url)
        wx.LaunchDefaultBrowser(url.replace(' ', '%20')) # wx.BROWSER_NEW_WINDOW) # falla esta constante



    def add_text(self, txt):
        #if txt[0]=='Y':
        #    raise NameError('Yes')
        #else:
        self.logger.add_text('ww'+txt)



    # closes tabular data window
    def tabular_onclose(self):
        #print 'tabular_onclose' url #code prior version 0.0.1
        logging.debug('tabular_onclose'+url)
        self.tabular = None



    # closes tabular data window
    def tabular_close(self):
        #print 'tabular_close' url #code prior version 0.0.1
        logging.debug('tabular_close'+url)
        # así ?
        if self.tabular is not None:
            self.tabular.Close()
            self.tabular.Destroy() # así ?
            self.tabular = None



    # shows a window with tabular data of the children of struct
    def tabular_show(self, struct, fromfile=False):
        #print 'tabular_show', struct url #code prior version 0.0.1
        logging.debug('tabular_show'+struct+url)
        if self.tabular is None:
            self.tabular = WindowTabular.WindowTabular(self, self.tabular_onclose)
        self.tabular.display(struct, fromfile)
	#self.write_gr2_from_struct(struct)


    #Crea una estructua de datos a partir de un struct para luego escribir un fichero .gr2
    def gr2_data_from_struct(self,struct):						#añadido
	child = struct.get_children()							#añadido
	name = struct.get_name()							#añadido
	struct.get_attribs()[u'data'] = 'file:' + os.path.join(self.configdir,'2d_graph.gr2')	
	fn = struct.get_attribs().get(u'data')						#añadido
	if fn is not None:								#añadido
	    i = fn.find(u':')								#añadido
	    filename = fn[i+1:]								#añadido
	else:										#añadido
	    struct.get_attribs()[u'data'] = os.path.join(self.configdir,u'2d_graph.gr2')
            #print len(child)								#añadido #code prior version 0.0.1
            logging.debug(len(child))
	if len(child) >= 2:								#añadido
	    sigs = []									#añadido
	    xlegend = child[0].get_name()						#añadido
	    xvalues = child[0].get_elements()						#añadido
	    xaxis = {u'legend':xlegend,u'values':xvalues}				#añadido
	    for i in range(1,len(child)):						#añadido
		ylegend = child[i].get_name()						#añadido
		yvalues = child[i].get_elements()					#añadido
		yaxis = {u'legend':ylegend,u'values':yvalues}				#añadido
		sigs.append({u'xaxis':xaxis,u'yaxis':yaxis})				#añadido
	    signals = {u'filename':filename,u'title':name,u'xlabel':xlegend,u'ylabel':ylegend,u'signals':sigs} #Temporal
	    return signals								#añadido
	else:										#añadido
	    self.errormsg(u'Two or more data arrays needed')
	    return None									#añadido

    #escribe un fichero .gr2 con el formato de entrada de 2d_graph
    #deberia estar esto localizado en window.py?? ??????
    #temporal: escribe el fichero en ../code. q variable contiene el directorio temporal .MaxFEM. cambiar
    #q variable contiene el directorio de trabajo?? ---> path_local_get() ???. cambiar
    #las listas se escriben con el formato [ , , , ]. Corregir.
    def write_gr2_from_struct(self,struct):						#añadido
	signals = self.gr2_data_from_struct(struct)					#añadido


	if signals is not None:								#añadido
	    sigs = signals.get(u'signals')						#añadido
            try:
		filegr2 = open(signals.get(u'filename'),'w')				#añadido
		filegr2.write(str(len(sigs))+'\n')					#añadido
		for sig in sigs:							#añadido
		    xvalues = sig.get(u'xaxis').get(u'values')				#añadido
		    yvalues = sig.get(u'yaxis').get(u'values')				#añadido
		    if len(xvalues)<= 0 or len(yvalues) <=0:				#añadido
			self.errormsg(u'Error showing plot: No scalar data to plot.')	#añadido
			return None							#añadido
		    filegr2.write(str(len(xvalues)) + u'\n')				#añadido
		    for v in xvalues:							#añadido
			filegr2.write(str(v) + u' ')					#añadido
		    filegr2.write(u'\n')						#añadido
		    for v in yvalues:							#añadido
			filegr2.write(str(v) + u' ')					#añadido
		    filegr2.write(u'\n')						#añadido
		filegr2.write(signals.get(u'title') + u'\n')				#añadido
		filegr2.write(u'X (' +signals.get(u'xlabel') + u')' + u'\n')		#añadido
		filegr2.write(u'Y' + u'\n')						#añadido
		for sig in sigs:							#añadido
		    filegr2.write(sig.get(u'yaxis').get(u'legend') + u'\n')		#añadido
		filegr2.close()								#añadido
            except IOError:								#añadido
		#print u'Error writing data to temporary file: ' + filegr2		#añadido #code prior version 0.0.1
                logging.warning(u'Problem writing data to temporary file: '+filegr2)
		return None								#añadido
	return signals.get(u'filename')							#añadido

    def graph2d_from_struct(self,struct):						#añadido
	filename = self.write_gr2_from_struct(struct)					#añadido
	if filename is not None:							#añadido
	    self.panelB.add_update(struct)						#añadido
	    try:									#añadido
		os.remove(filename)							#añadido
	    except IOError:								#añadido
		print u'Error deleting temporary file: ' + filename			#añadido




    # updates a window with tabular data of the children of struct.
    # if the window has children of other struct, does nothing.
    def tabular_update(self, struct):
        #print 'tabular_update', struct #code prior version 0.0.1
        logging.debug('tabular_update'+struct)
        if self.tabular is not None:
            self.tabular.update(struct) # does nothing if it is displaying other struct



    def htmlhelp_show(self, struct):

        data = struct.get_attribs().get(config.AT_HELPWINDOWDATA)
        configuration = struct.get_attribs().get(config.AT_HELPWINDOWCONFIG)

        if data is None:
            self.errormsg('Error creating help window: No data to show')
            return

        # path da instalacion, para rutas relativas a el
        instpath = os.path.join(self.path_exe, os.pardir)

        ret = WindowHtml.add_pre(self, data, configuration, instpath)

        if ret is not None:
            self.errormsg('Error creating help window: ' + ret)
            return



    def load_remotedata(self):
        if self.path_local_remotedata is None:
            return

        try:
            file = open(self.path_local_remotedata,'rb')
        except Exception, why:
            # default value
            if not 'queuing' in self.remotedata:
                self.remotedata['queuing'] = 'qrsh -q general -j y -V -cwd'
            # Not really an error, occours always the first time is executed
            logging.debug('Problem loading remotedata.txt: ' + repr(why))
            return

        for line in file:
            if line[-1] == '\n':
                line = line[:-1]
            parts = line.split(None,1)
            if len(parts) < 2:
                continue
            if parts[0] == 'user':
                self.remotedata['user'] = parts[1]
            elif parts[0] == 'host':
                self.remotedata['host'] = parts[1]
            elif parts[0] == 'key':
                self.remotedata['key'] = parts[1]
            elif parts[0] == 'queuing':
                self.remotedata['queuing'] = parts[1]

        file.close()



    def save_remotedata(self):
        if self.path_local_remotedata is None:
            return

        try:
            file = open(self.path_local_remotedata,'wb')
        except Exception, why:
            self.errormsg('Error saving remote data: ' + repr(why))
            return
        user = self.remotedata.get('user')
        if user is None:
            user = ''
        host = self.remotedata.get('host')
        if host is None:
            host = ''
        key = self.remotedata.get('key')
        if key is None:
            key = ''
        queuing = self.remotedata.get('queuing')
        if queuing is None:
            queuing = ''
        file.write('user ' + user + '\n')
        file.write('host ' + host + '\n')
        file.write('key ' + key + '\n')
        file.write('queuing ' + queuing + '\n')
        file.close()
        

        
    def menu_exec_ssh(self, action):

        if self.taskscurrent>=0 and self.taskscurrent<len(self.taskssave):
            self.errormsg('There are pending processes to run. Will not start a thread')
            return

        #if len(self.choices) > 0: # ???
        #    self.errormsg('There are pending parametrised processes to run. Will not start a thread')
        #    return

        # aviso hai outro thread. continuar si/non
        nt = self.num_threads()
        if nt != 0:
            self.errormsg(u'There are already '+unicode(nt)+u' threads running. Will not create another thread')
            return

#            res = self.askmsg(u'There are already '+unicode(nt)+u' threads running. Create another thread?','yesno')
#            if res is False:
#                return


        params = action.get('params')
        if params is None or len(params)<1:
            self.errormsg(u'Error in menu: missing executable name')
            return
        
        # <dialog>
        dialog = WindowRemote.WindowRemote(self, self.remotedata)
        r = dialog.ShowModal()
        if r == wx.ID_OK:
            datanew = dialog.get_data()
            for d,v in datanew.items():
                self.remotedata[d] = v
            self.save_remotedata()
        dialog.Destroy()
        dialog = None
        if r != wx.ID_OK:
            return
        # </dialog>

        options = {}
        options['host'] = self.remotedata.get('host')
        options['user'] = self.remotedata.get('user')
        options['passw'] = self.remotedata.get('pass')
        options['keyfile'] = self.remotedata.get('key')
        options['queuing'] = self.remotedata.get('queuing')
        options['executables'] = params

        thread = ThreadRemote.ThreadRemote(self, options)
        self.add_thread(thread)
        thread.start()



    def event_end_process(self, event):
        self.end_process(event.m_exitcode,custom_command=True)



    def end_process(self, exitcode, stopped=False, custom_command=False):
        #print u'end', exitcode, stopped #code prior version 0.0.1
        logging.debug(u'end'+str(exitcode)+str(stopped))
        if not stopped:
            self.timer.Stop()
            self.event_timer2()

        txt = self.panelC.stop_code(exitcode) # si no se ejecuta siempre, dio: Elapsed time = 23:59:57.250

        if not stopped:
            self.process.ended()

        self.logger.add_text(u'SOLVER ' + unicode(self.taskscurrent) + ' STOP: ' + txt + u'\n')
        
# if we are executing parametrized, exec next combination
        #more = self.next_choice()
        #if more is not True and more!=0:
        #    self.logger.add_text(unicode(more) + u' SOLVERS STOP: ' + txt + u'\n') # non sempre
        
        error = exitcode != 0

        # si hay error cancela la secuencia de ejecucion
        name = None
        if error:
            res = None
            if self.taskscurrent >= 0 and self.taskscurrent < len(self.taskssave):
                name = self.taskssave[self.taskscurrent].get('path')
                if name is None:
                    name = self.taskssave[self.taskscurrent].get('text')
        else:
            res = self.next_task2(custom_command)

        # True -> started another one
        if res is None: # finished series
            txt = self.panelC.time()
            elapsed = self.panelC.endall()
            if len(elapsed) > 0:
                elapsed = ' elapsed: ' + elapsed
            self.logger.add_text(u'SOLVERS STOP: ' + txt + elapsed + u'\n')
            self.taskscurrent = -2
	    if self.reload_menu:				#reload menu at solvers stop
		self.menu_load(False)				#reload menu at solvers stop
        if res is False: # error in last command
            txt = self.panelC.time()
            elapsed = self.panelC.endall()
            if len(elapsed) > 0:
                elapsed = ' elapsed: ' + elapsed
            self.logger.add_text(u'SOLVERS STOP ERROR: ' + txt + elapsed + u'\n')
            self.taskscurrent = -2

        if error:
            if exitcode is None:
                if name is None:
                    self.errormsg('A solver failed to start. Cancelling execution. See execution window')
                else:
                    self.errormsg('Solver \''+name+'\' failed to start. Cancelling execution. See execution window')
            else:
                if name is None:
                    self.errormsg('A solver returned exit code '+unicode(exitcode)+'. Cancelling execution. See execution window')
                else:
                    self.errormsg('Solver \''+name+'\' returned exit code '+unicode(exitcode)+'. Cancelling execution. See execution window')



    def event_timer(self, event):
        self.event_timer2()


    
    def event_timer2(self):
        self.logger.add_text('aa'+self.process.read())

    def menu_exec_custom(self, action):

        params = action.get('params')

        if params is None or len(params)<1:
            self.errormsg(u'Error in menu: missing executable name')
            return        

        # <dialog>
        dialog = WindowCustom.WindowCustom(self,action)
        r = dialog.ShowModal()
        if r == wx.ID_OK:
	    salida = dialog.get_custom_command()
	    if salida is not None and isinstance(salida,basestring):
		action['data'] = salida
	    elif salida is not None:
		action[u'params'] = salida
	    #Recoger los datos
        dialog.Destroy()
        dialog = None
        if r != wx.ID_OK:
            return
        # </dialog>
	self.menu_exec2(action, True)


    def menu_exec2(self, action, custom_command=False):
        if self.process.is_running():
            self.errormsg('There is a process running. Will not start another one')
            return

        if self.taskscurrent>=0 and self.taskscurrent<len(self.taskssave):
            self.errormsg('There are pending processes to run. Will not start another one')
            return

        #if len(self.choices) > 0: # ???
        #    self.errormsg('There are pending parametrised processes to run. Will not start another one')
        #    return

        nt = self.num_threads()
        if nt != 0:
            self.errormsg(u'There are already '+unicode(nt)+u' threads running. Will not create another thread')
            return
#            res = self.askmsg(u'There are already '+unicode(nt)+u' threads running. Continue?','yesno')
#            if res is False:
#                return

        params = action.get('params')

        for param in params:
            if True: # era type=solver
                executable = None
                executable1 = os.path.join(self.configdir,config.DIR_SOLVERS,param.get('text'))
                executable2 = os.path.join(self.path_exe,os.pardir,config.DIR_SOLVERS,param.get('text'))

                # repensar: action[1] pode ser 'executable', para o cal valeria 'executable.exe' en windows, pero non en posix/mac/...: os.name
                exesallowed = os.name != 'posix'
                if os.path.isfile(executable1) or ( exesallowed and os.path.isfile(executable1+'.exe') ):
                    executable = executable1
                elif os.path.isfile(executable2) or ( exesallowed and os.path.isfile(executable2+'.exe') ):
                    executable = executable2

                if executable is None:
                    #self.errormsg(u'Error: solver executable \''+param.get('text')+ u'\' not found')
                    #return False
                    pass
                else:
		    param['path'] = executable # anhade elementos en estructura usada fuera ?

		if custom_command and action.get('data') is not None:
		    param.get('attrib')['data'] = action.get('data')
	#Permite el comando del sistema [+ ejecutable (opcional)]

        self.taskssave = params
        self.taskscurrent = -1

        txt = self.panelC.start()
        self.logger.add_text(u'SOLVERS START: ' + txt + u'\n')
        
        self.next_task2(custom_command)



    def next_task2(self,custom_command=False):
        if self.taskscurrent < -1:
            return None

        self.taskscurrent += 1

        ret = self.exec2(custom_command)
        
        # novo codigo: irregular ? non respeta fluxo ?
        if ret is False: # error iniciando ejecucion
            self.end_process(None, True, custom_command) # continua con otros. Ya finalizado

        # distinto caso: non executado por erro de non executado por fin
        return ret



    def exec2(self,custom_command=False):
        if self.taskscurrent < 0 or self.taskscurrent >= len(self.taskssave):
            return None

        param = self.taskssave[self.taskscurrent]

        if 'path' in param:
            command = u'"'+param.get('path')+u'"'
        else:
            command = param.get('text')
        
        args = param.get('attrib').get('args')
        if args is not None and args != u'':
            command += u' ' + args

	if custom_command and param.get('attrib').get('data') is not None:
	    command = param.get('attrib').get('data') + u' ' + command

#        if param.get('attrib').get('type') == 'solver':
#            result = self.process.start(command, self.menus.get_datafile()+u'\n')
#        else:
#            result = self.process.start(command, None)

        result = self.process.start(command, None)

        txt = self.panelC.time()
        if result is True:
            self.logger.add_text(u'SOLVER '+ unicode(self.taskscurrent) +' START: '+txt+': '+command+'\n')
            self.timer.Start(200)
        else:
            self.logger.add_text(u'SOLVER '+ unicode(self.taskscurrent) +' failed to start: '+txt+': '+command+'\n')

        return result is True



    def menu_kill(self):
        #del self.choices[self.choiceindex:]
        self.process.kill()



    # threads #



    def num_threads(self):
        return len(self.threads)



    def stop_threads(self):
        while self.threads:
            thread = self.threads[0]
            thread.stop() # no hace nada
            self.threads.remove(thread)
 
 
 
    def add_thread(self, thread):
        #print 'window: thread added:', thread #code prior version 0.0.1
        logging.debug('window: thread added:'+str(thread))
        self.threads.append(thread)



    def finished_thread(self, thread):
        #print 'window: thread ended:', thread #code prior version 0.0.1
        logging.debug('window: thread ended:'+str(thread))
        self.threads.remove(thread)



# ---- old ---- ---- ---- ---- old ---- ---- ---- ---- old ---- ---- ---- ---- old ---- ---- ----



    # deprecated. vaise borrar substituido por exec2
    def exec1(self, action, vector=None):
    
        if action[0] == u'exesolver':
            executable = None
            executable1 = os.path.join(self.configdir,config.DIR_SOLVERS,action[1])
            executable2 = os.path.join(self.path_exe,os.pardir,config.DIR_SOLVERS,action[1])

            # repensar: action[1] pode ser 'executable', para o cal valeria 'executable.exe' en windows, pero non en posix/mac/...: os.name
            exesallowed = True
            if os.path.isfile(executable1) or ( exesallowed and os.path.isfile(executable1+'.exe') ):
                executable = executable1
            elif os.path.isfile(executable2) or ( exesallowed and os.path.isfile(executable2+'.exe') ):
                executable = executable2

            if executable is None:
                self.errormsg(u'Error: solver executable \''+action[1]+ u'\' not found')
                return False
        else:
            executable = action[1]

        args = u' '.join(action[2:])
        command = executable
        if args != u'':
            command += u' ' + args

        if action[0] == u'exesolver':
            result = self.process.start(command, self.menus.get_datafile()+u'\n')
        else:
            result = self.process.start(command, None)
        if result is True:
            #self.panelC.clear_st()
            if vector is None or self.choiceindex == 0:
                txt = self.panelC.start()
            else:
                txt = self.panelC.time()
            txtv = u''
            if vector is not None:
                txtv = u' [' + vector + u']'
            if vector is not None and self.choiceindex == 0:
                self.logger.add_text(unicode(len(self.choices)) + u' SOLVERS START: ' + txt + u'\n')

            if vector is None:
                self.logger.add_text(u'SOLVER START: ' + txt + txtv + u'\n')
            else:
                self.logger.add_text(u'SOLVER ' + unicode(self.choiceindex) + u' START: ' + txt + txtv + u'\n')

            self.timer.Start(200)



    # deprecated: substituir por menu_exec2
    def menu_exec(self, action):
         # protexer de salvar sen directorio de traballo
#        self.menus.save_data()
#        self.menu_choice()

        if self.process.is_running():
            self.logger.add_text("Process not started: BUSY [menu_exec:process]")
            return

        # PORQUE ESTO AQUI ?!!?
        self.clear_choices()
        self.action = action

        if len(self.choices) > 0: # ???
            print u'BUSY'
            return

        params = self.menus.get_parameters()
        p = Parametrize.Parametrize()
        p.setp(params)
        numchoices = p.get_num_choices()
        print u'choices: ', numchoices

        p.save_xml(u'parameters.xml')

        if numchoices <= 0:
            self.errormsg(u'Cancelling parametrized execution with 0 combinations')
            return
        if numchoices == 1:
            self.exec1(action)
            return
        if numchoices >= 2:
            self.choices = p.get_choices()
            self.choiceindex = 0
            for choice in self.choices:
                print choice
                namedir = Parametrize.Parametrize.dirname(choice)
                try:
                    os.mkdir(namedir)
                except OSError, e:
                    print repr(e)
                self.menus.save_data(os.path.join(namedir,self.menus.get_datafile()), p.index_convert(choice))
            self.next_choice()
            return



# True: can be other iterations [or no]
# number: there are no [more] iterations
    def next_choice(self):
        if self.choiceindex < len(self.choices):
            name = Parametrize.Parametrize.name(self.choices[self.choiceindex])
            namedir = Parametrize.Parametrize.dirname(self.choices[self.choiceindex])
            try:
                os.chdir(namedir)
            except OSError, e:
                print repr(e)
                self.errormsg(u'Cancelling parametrized execution ' +
                    u'because of error changing working directory: ' + e)
            else:
                self.exec1(self.action, name)
                self.choiceindex += 1
                try:
                    os.chdir(self.path_local_get())
                except OSError, e:
                    print repr(e)
                    self.errormsg(u'Cancelling parametrized execution ' +
                        u'because of error changing working directory: ' + e)
                else:
                    return True
        was = len(self.choices)
        self.clear_choices()
        return was



#    def aux_meshes(self):
#    #    leaf-file-field    # tamén ?
#        leafs = self.menus.get_nodes(u'leaf-file-mesh')
#        for l in leafs:
#            l.read_source(True, True)


    def clear_choices(self):
        self.choices = []
        self.choiceindex = 0


    def menu_choice(self):
        params = self.menus.get_parameters()
        p = Parametrize.Parametrize()
        p.setp(params)
        print u'choices: ', p.get_num_choices()

