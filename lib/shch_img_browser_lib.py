import os
from shutil import copyfile
import getpass
import json
import tkinter as tk

DEBUG_ENABLED = False
#!
# returns the path to an image file.
#   Note that this method is simply a wrapper for os.path.join(...).
# Args:
#   image_folder: str
#       A legit folder name.
#   image_file : str
#       A legit file name.
# Returns: image_path : str
#       This is the path to the specified file, image_file, in the folder, image_folder.
def fnc_GetImageFilePath(image_folder, image_file):
    return os.path.join(image_folder, image_file)
    # end of function
#!
# this is a wrapper for os.path.isfile(...)
# Args:
#   file_path : str
#       The file path to check if that file exists.
# Returns: result : bool
#   The return value is that of os.path.isfile(file_path)
def fnc_IsExistingFile(file_path):
    return os.path.isfile(file_path)
#!
# checks if a given file (image_file) has one of the extentions as in the list, extensions.
# Args:
#   image_file : str
#       A legit file name.
#   extensions : dict
#       The format of extensions is (example): {'png': (1, 0), 'jpg': (1, 0), 'jpeg': (1, 0), }
#       Each extension name must be without preciding ".". In other word, .png should be supplied as 'png' not
#       as '.png'. The key, which is a tuple/list, has its members be set either to 0 or 1.
#       The 1st entry indicates if the extension (file type) is selected (to be used in the slideshow).
#       For that it must be == 1.
#       The 2nd entry indicates if the extension is treates as case sensitive (1), or not (0).
# Returns: result : bool
#   The return value is False if the file (image_file) has its extension that is not in extensions.
#   If there, the result = True.
def fnc_HasLegitExtension(image_file, extensions):
    if not type(image_file) == type(''):
        return False
    if (not isinstance(extensions, dict)) or len(extensions) < 1:
        return False

    _ext = os.path.splitext(image_file)[1][1:]
    _ext_lower = _ext.lower()

    for _each_ext, _label in extensions.items():
        if isinstance(_label, (list, tuple)) and (len(_label) == 2):
            _selected, _cs = _label
            if _selected == 1:
                if (_cs == 0) and (_each_ext.lower() == _ext_lower):
                    return True
                if (_cs == 1) and (_each_ext == _ext):
                    return True

    return False
    # end of function
#!
# gets the list of image files in a given folder (image_folder). Only names of the files will be returned whose
#   extentions are listed in the list/tuple (legit_extensions).
# Args:
#   image_folder : str
#       This must be a legit folder name.
#   legit_extensions : dict
#       The format of legit_extensions is (example): {'png': (1, 0), 'jpg': (1, 0), 'jpeg': (1, 0), }
#       Each extension name must be without preciding ".". In other word, .png should be supplied as 'png' not
#       as '.png'. The key, which is a tuple/list, has its members be set either to 0 or 1.
#       The 1st entry indicates if the extension (file type) is selected (to be used in the slideshow).
#       For that it must be == 1.
#       The 2nd entry indicates if the extension is treates as case sensitive (1), or not (0).
# Returns: list
#   Each member is a string which is a file name (without any folder name(s)).
#   If no files were found, the list is empty.
def fnc_GetImageFileList(image_folder, legit_extensions):
    try:
        return [_f for _f in os.listdir(image_folder) if\
            os.path.isfile(os.path.join(image_folder, _f)) and\
            fnc_HasLegitExtension(_f, legit_extensions)]
    except:
        return []
    # end of function

class ImgBrowserConfig():
    __doc__ ="""
    loads the config info, if it is available in the folder named shch_img_browser_cfg,
        in the file named 'current user name'.cfg. Otherwise it loads the default settings.
    Args: none.
    Returns: instance of this class.
    """
    #!
    def __init__(self):
        global DEBUG_ENABLED

        self.HOME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.CONFIG_FOLDER = 'shch_img_browser_cfg'
        self.CURRENT_USER = getpass.getuser()
        _config_folder_path = os.path.join(self.HOME_DIR, self.CONFIG_FOLDER)
        _config_file_path = os.path.join(_config_folder_path, '{}.cfg'.format(self.CURRENT_USER))
        if DEBUG_ENABLED:
            print(_config_file_path)

        self.CONFIG_KEYS = {'ICO_FOLDER' : 'str', 'ICO_FILE' : 'str',\
                            'IMAGE_FOLDER' : 'str', 'IMAGE_FILE_EXTENSIONS' : 'dict',\
                            'IMAGE_SCALE_INDEX' : 'int', 'WIDGET_FONT_SIZE_INDEX' : 'int'}
        _useDefaults = True
        # try to load from the config file. If not available, use the default settings
        try:
            with open(_config_file_path, 'r') as _config_file:
                _config = json.load(_config_file)
                self.__c__ = {_key : _config[_key] for _key in self.CONFIG_KEYS if\
                        self.fnc_checkType(self.CONFIG_KEYS[_key], _config[_key])}
                if DEBUG_ENABLED:
                    print(self.__c__)

                if len(self.__c__) == len(self.CONFIG_KEYS):
                    _useDefaults = False
        except:
            if DEBUG_ENABLED:
                print('no config is loaded')

        if _useDefaults:
            self.__c__ = dict()
            self.__c__['ICO_FOLDER'] = self.CONFIG_FOLDER
            self.__c__['ICO_FILE'] = 'shch_071821_121644.ico'

            self.__c__['IMAGE_FILE_EXTENSIONS'] =\
                    {'png': (1, 0), 'jpg': (1, 0), 'jpeg': (1, 0), 'tiff': (1, 0), 'tif': (1, 0),\
                     'gif': (1, 0), 'bmp': (1, 0), 'raw': (1, 0), 'eps': (1, 0),\
                    }
            # changed 25-11-2021 (25th-November-2021, Thanksgiving Day)
            self.__c__['IMAGE_FOLDER'] =\
                    ImgBrowserStartDir(self.__c__['IMAGE_FILE_EXTENSIONS'], self.HOME_DIR).fnc_getStartDir()
            #
            self.__c__['IMAGE_SCALE_INDEX'] = 10
            self.__c__['WIDGET_FONT_SIZE_INDEX'] = 4

        self.ICO_PATH =  fnc_GetImageFilePath(\
            self.HOME_DIR, fnc_GetImageFilePath(\
            self.__c__['ICO_FOLDER'], self.__c__['ICO_FILE']))
        self.IMAGE_FOLDER = self.__c__['IMAGE_FOLDER']
        self.IMAGE_FILE_EXTENSIONS =  {_ext: _label for _ext, _label in self.__c__['IMAGE_FILE_EXTENSIONS'].items()}
        self.IMAGE_SCALE_INDEX = self.__c__['IMAGE_SCALE_INDEX']
        self.WIDGET_FONT_SIZE_INDEX = self.__c__['WIDGET_FONT_SIZE_INDEX']
        # end of __init__

    #!
    # checks varaible type
    # Args:
    #   type_of_var: str
    #       Describes the type. It can be be presently str, int and dict.
    # Returns: success_code : bool
    #   This is True is the check has passed. False otherwise.
    def fnc_checkType(self, type_of_var, var_to_check):
        if type_of_var == 'str':
            return type('') == type(var_to_check)

        if type_of_var == 'int':
            return type(0) == type(var_to_check)

        if type_of_var == 'dict':
            return isinstance(var_to_check, dict)

        return False

    #!
    # saves the existing configuration in the file named 'current user name'.cfg, which is located in
    #   the folder named shch_img_browser_cfg.
    # Args:
    #   kwargs: (typical kwargs)
    #       'folder' : <any value>
    #           If this is in kwargs, the folder name will be saved (but extensions will not be changed).
    #       'extensions' : <any value>
    #           If this is in kwargs, all selected extensions will be saved (but not the image folder name).
    #           Note: have 'folder' and 'extensions' together in kwargs to save both the new image folder
    #           name and new legit files' extensions.
    #       'image_scale' : <any value>
    #           If this is in kwargs, the current image scale will be saved.
    # Returns: nothing.
    def fnc_save(self, **kwargs):
        _config_folder_path = os.path.join(self.HOME_DIR, self.CONFIG_FOLDER)
        if not os.path.isdir(_config_folder_path):
            try:
                os.mkdir(_config_folder_path)
            except:
                return

        _config_file_path = os.path.join(_config_folder_path, '{}.cfg'.format(self.CURRENT_USER))

        try:
            with open(_config_file_path, 'w') as _config_file:

                if 'folder' in kwargs:
                    self.__c__['IMAGE_FOLDER'] = self.IMAGE_FOLDER
                    if DEBUG_ENABLED:
                        print(self.__c__['IMAGE_FOLDER'])
                if 'extensions' in kwargs:
                    self.__c__['IMAGE_FILE_EXTENSIONS'] = self.IMAGE_FILE_EXTENSIONS
                    if DEBUG_ENABLED:
                        print(self.__c__['IMAGE_FILE_EXTENSIONS'])
                if 'image_scale' in kwargs:
                    self.__c__['IMAGE_SCALE_INDEX'] = self.IMAGE_SCALE_INDEX
                    if DEBUG_ENABLED:
                        print(self.__c__['IMAGE_SCALE_INDEX'])
                if 'widget_font_size' in kwargs:
                    self.__c__['WIDGET_FONT_SIZE_INDEX'] = self.WIDGET_FONT_SIZE_INDEX
                    if DEBUG_ENABLED:
                        print(self.__c__['WIDGET_FONT_SIZE_INDEX'])

                _config_to_save = json.dumps(self.__c__)
                _config_file.write(_config_to_save)

        except:
            if DEBUG_ENABLED:
                print('no config is saved')

    #!
    # removes the given item from self.IMAGE_FILE_EXTENSIONS
    # Args:
    #   extension_to_del : str
    #       This is the extension to delete from self.IMAGE_FILE_EXTENSIONS
    #   kwargs: usual keyword arguments
    #       'all' : <any value>
    #           Set this to any value to activate the removal of all matches (case insensitive) in the item list.
    # Returns: nothing
    def fnc_removeExtension(self, extension_to_del, **kwargs):
        if len(self.IMAGE_FILE_EXTENSIONS) < 1:
            return

        if not (type(extension_to_del) == type('')):
            return

        if 'all' in kwargs:
            _extension_to_del_lower = extension_to_del.lower()
            _img_file_extensons = {_ext: _label  for _ext, _label in\
                self.IMAGE_FILE_EXTENSIONS.items() if not\
                _ext.lower() == _extension_to_del_lower}
            self.IMAGE_FILE_EXTENSIONS = _img_file_extensons
        else:
            if extension_to_del in self.IMAGE_FILE_EXTENSIONS:
                self.IMAGE_FILE_EXTENSIONS.pop(extension_to_del)
        # end of function
    #!
    # inserts the given extension into self.IMAGE_FILE_EXTENSIONS
    # Args:
    #   extension_to_ins : str
    #       This is the extension to insert to self.IMAGE_FILE_EXTENSIONS
    #   args: typical args
    #       args[0] : int
    #           If args[0] is integer, the newly inserted extension label will be set to args[0], provided
    #           that it is -1, 0, or 1. Otherwise the label defaults to 1.
    # Returns: nothing.
    def fnc_insertExtension(self, extension_to_ins, *args):
        if not (type(extension_to_ins) == type('')):
            return

        _cs = 0
        if (len(args) > 0) and (type(args[0]) == type(0)):
            _cs = args[0]
            if _cs > 1:
                _cs = 1
            if _cs < 0:
                _cs = 0

        try:
            self.IMAGE_FILE_EXTENSIONS[extension_to_ins] = (1, _cs)
        except:
            pass
        # end of function
    #!
    #
    # Args:
    #   selected_exts : dict
    #       This must be a dictionary with the keys = extensions, and the values = 1, 0, -1
    # Returns: nothing.
    def fnc_selectExtensions(self, selected_exts):
        if len(self.IMAGE_FILE_EXTENSIONS) < 1:
            return
        for _ext in self.IMAGE_FILE_EXTENSIONS:
            self.IMAGE_FILE_EXTENSIONS[_ext] = (0, self.IMAGE_FILE_EXTENSIONS[_ext][1])

        if len(selected_exts) < 1:
            return

        for _ext in selected_exts:
            if _ext in self.IMAGE_FILE_EXTENSIONS:
                self.IMAGE_FILE_EXTENSIONS[_ext] = (1, self.IMAGE_FILE_EXTENSIONS[_ext][1])
        # end of function
    # end of class ImgBrowserConfig

class ExtsAdj():
    #!
    def __init__(self, root, callback=None, exts_list={}, **kwargs):
        self.callback = callback
        self.IS_CANCELED = True

        self.top = tk.Toplevel(root)
        if ('ico_path' in kwargs) and fnc_IsExistingFile(kwargs['ico_path']):
            self.top.iconbitmap(kwargs['ico_path'])

        self.list = tk.Listbox(self.top, selectmode='multiple', font= (14))
        for _ext, _label in exts_list.items():
            self.list.insert('end', _ext)

            if isinstance(_label, (list, tuple)) and (len(_label) == 2) :
                _selected, _cs = _label

                if _selected == 1:
                    self.list.selection_set(self.list.size() - 1)
                # if case sensitive,, change background
                if _cs == 1:
                    self.list.itemconfig('end', bg= '#EEE8AA')

        self.list.pack(expand= 'yes', fill= 'both', padx= 10, pady= 3)

        self.frame_for_buttons = tk.Frame(self.top)
        self.frame_for_buttons.pack()
        self.button_okay = tk.Button(
            self.frame_for_buttons,
            text= "Okay", font=(14), fg= 'black',
            relief = tk.GROOVE, bd = 4,
            command=  self.fnc_okay,
        )
        self.button_cancel = tk.Button(
            self.frame_for_buttons,
            text= "Cancel", font=(14), fg= 'red',
            relief = tk.GROOVE, bd = 4,
            command= self.top.destroy,
        )
        self.button_okay.grid(row= 0, column= 0)
        self.button_cancel.grid(row= 0, column= 1)

        self.button_select_all = tk.Button(
            self.top,
            text= 'Select All', font= (14), fg= 'green',
            relief = tk.RIDGE, bd = 4,
            command= self.fnc_select_all,
        )
        self.button_unselect_all = tk.Button(
            self.top,
            text= 'Unselect All', font= (14), fg= 'green',
            relief = tk.RIDGE, bd = 4,
            command= self.fnc_unselect_all,
        )
        self.button_select_all.pack()
        self.button_unselect_all.pack()
        # end of __init__

    #!
    # okays the selections, sets self.items_selected to a list with members that are the items selected by a user.
    #   Also  returns a reference to self.items_selected.
    #   Note that invoking this function destroys the Popup.
    # Args: none.
    # Return: selected_items : list
    #   In this list, each member is an item selected ny a user.
    def fnc_okay(self):
        _selected_indices = self.list.curselection()
        _selected_exts = [self.list.get(_each) for _each in _selected_indices]

        self.top.destroy()

        if not (self.callback is None):
            try:
                self.callback(_selected_exts)
                self.IS_CANCELED = False
            except:
                pass
        # end of function

    #!
    # selects all items which are in the list box
    # Args: none.
    # Return:
    def fnc_select_all(self):
        _last_index = self.list.size() - 1
        self.list.selection_set(first= 0, last= _last_index)
        # end of function
    #!
    # unselects everything
    # Args: none.
    # Return:
    def fnc_unselect_all(self):
        _last_index = self.list.size() - 1
        self.list.selection_clear(first= 0, last= _last_index)
        # end of function
    # end of class ExtsAdj

class ExtsRem():
    #!
    def __init__(self, root, callback=None, **kwargs):
        self.callback = callback
        self.IS_CANCELED = True

        self.top = tk.Toplevel(root)
        if ('ico_path' in kwargs) and fnc_IsExistingFile(kwargs['ico_path']):
            self.top.iconbitmap(kwargs['ico_path'])

        self.label_w_info = tk.Label(
            self.top,
            text= "Enter extension", font= (14), fg= 'black',
        )
        self.entry_for_ext = tk.Entry(
        self.top,
        font= (14),
        )
        self.button_remove = tk.Button(
            self.top,
            text= "[-] Remove", font=(14), fg= 'black',
            relief = tk.GROOVE, bd = 4,
            command=  self.fnc_remove,
        )
        self.button_removeAll = tk.Button(
            self.top,
            text= "[=] Remove All", font=(14), fg= 'red',
            relief = tk.GROOVE, bd = 4,
            command= lambda: self.fnc_remove(all=1),
        )
        self.button_cancel = tk.Button(
            self.top,
            text= 'Cancel', font= (14), fg= 'green',
            relief = tk.RIDGE, bd = 4,
            command= self.top.destroy,
        )

        self.label_w_info.grid(row= 0, column= 0, padx= 5, pady= (2, 5), )
        self.entry_for_ext.grid(row= 1, column= 0, padx= 7, pady= (5, 5), )
        self.button_remove.grid(row= 2, column= 0, padx= 5, pady= (4, 4), )
        self.button_removeAll.grid(row= 3, column= 0, padx= 5, pady= (4, 4), )
        self.button_cancel.grid(row= 4, column= 0, padx= 5, pady= (4, 10), )
        # end of __init__

    #!
    # removes an extension from the list
    # Args:
    #   kwargs: usual keyword arguments
    #       'all' : <any value>
    #           Set this to any value to activate the removal of all matches (case insensitive) in the item list.
    # Returns: nothing
    def fnc_remove(self, **kwargs):
        _item = self.entry_for_ext.get()
        if DEBUG_ENABLED:
            print('...before self.top.destroy()')
        self.top.destroy()
        if DEBUG_ENABLED:
            print('...after self.top.destroy()')

        if not (self.callback is None):
            try:
                if DEBUG_ENABLED:
                    print('...before self.callback(_item, **kwargs)')
                self.callback(_item, **kwargs)
                if DEBUG_ENABLED:
                    print('...after self.callback(_item, **kwargs)')
                self.IS_CANCELED = False
                if DEBUG_ENABLED:
                    print('...after self.IS_CANCELED = False')
            except:
                pass
        # end of function
    # end of class ExtsRem

class ExtsIns():
    #!
    def __init__(self, root, callback=None, **kwargs):
        self.callback = callback
        self.IS_CANCELED = True

        self.top = tk.Toplevel(root)
        if ('ico_path' in kwargs) and fnc_IsExistingFile(kwargs['ico_path']):
            self.top.iconbitmap(kwargs['ico_path'])

        self.label_w_info = tk.Label(
            self.top,
            text= "Enter extension", font= (14), fg= 'black',
        )
        self.entry_for_ext = tk.Entry(
        self.top,
        font= (14),
        )
        self.button_insert_cis = tk.Button(
            self.top,
            text= "[o] Insert (case insensitive)", font=(14), fg= 'black',
            relief = tk.GROOVE, bd = 4,
            command=  self.fnc_insert,
        )
        self.button_insert_cs = tk.Button(
            self.top,
            text= "[::] Insert (case sensitive)", font=(14), fg= 'red',
            relief = tk.GROOVE, bd = 4,
            command= lambda: self.fnc_insert(1),
        )
        self.button_cancel = tk.Button(
            self.top,
            text= 'Cancel', font= (14), fg= 'green',
            relief = tk.RIDGE, bd = 4,
            command= self.top.destroy,
        )

        self.label_w_info.grid(row= 0, column= 0, padx= 5, pady= (2, 5), )
        self.entry_for_ext.grid(row= 1, column= 0, padx= 7, pady= (5, 5), )
        self.button_insert_cis.grid(row= 2, column= 0, padx= 5, pady= (4, 4), )
        self.button_insert_cs.grid(row= 3, column= 0, padx= 5, pady= (4, 4), )
        self.button_cancel.grid(row= 4, column= 0, padx= 5, pady= (4, 10), )
        # end of __init__

    #!
    # inserts an extension into the list
    # Args:
    #   args: typical args
    #       args[0] : int
    #           If args[0] is integer, the newly inserted extension label will be set to args[0], provided
    #           that it is -1, 0, or 1. Otherwise the label defaults to 1.
    # Returns: nothing
    def fnc_insert(self, *args):
        _item = self.entry_for_ext.get()
        self.top.destroy()

        if not (self.callback is None):
            try:
                self.callback(_item, *args)
                self.IS_CANCELED = False
            except:
                pass
        # end of function
    # end of class ExtsIns

class ImgBrowserStartDir():
    __doc__ = """
    finds the local user folder (C:/Users/<User Name>/, or /home/<user name>/) and then finds if in that folder
        a subfolder named Pictures/Saved Pictures/, exists and has images.
        If the folder exists and has images it will be a default starting folder when the program is run for the first time.
        If folder does not exists, the next folder to be checked is Pictures/; if present and has images it will be set as
        a default folder for when the program is run for the first time.
        If those conditions are not met, Pictures/Saved Pictures/ will be created in the local user folder,
        and a few images will be transfered there from a repo that is supplied with the dist for this program.
    Args: legit_extensions :  dict
        The format of legit_extensions is (example): {'png': (1, 0), 'jpg': (1, 0), 'jpeg': (1, 0), 'tiff': (1, 0), }
        Each extension name must be without preciding ".". In other word, .png should be supplied as 'png' not
        as '.png'. The key, which is a tuple/list, has its members be set either to 0 or 1.
        The 1st entry indicates if the extension (file type) is selected (to be used in the slideshow).
        For that it must be == 1.
        The 2nd entry indicates if the extension is treates as case sensitive (1), or not (0).
    Returns: instance of this class.
    """
    #!
    def __init__(self, legit_extensions, home_dir):
        self.IMG_HOME_DIR = None
        _img_folder_code = -1
        try:
            _img_folder = os.path.join(os.path.expanduser('~'), 'Pictures', 'Saved Pictures')
        except:
            return
        # return # uncomment to see how self.IMG_HOME_DIR = None works

        if os.path.isdir(_img_folder):
            _img_files = fnc_GetImageFileList(_img_folder, legit_extensions)
            if len(_img_files) > 0:
                self.IMG_HOME_DIR = _img_folder
                if DEBUG_ENABLED:
                    print('startup image folder: ', self.IMG_HOME_DIR)
                return
        else:
            _img_folder_code = 0
            if DEBUG_ENABLED:
                print('folder: {}'.format(_img_folder), ' is not found')

        _img_folder = os.path.dirname(_img_folder) # go level up to ~/Pictures/
        if os.path.isdir(_img_folder):
            _img_files = fnc_GetImageFileList(_img_folder, legit_extensions)
            if len(_img_files) > 0:
                self.IMG_HOME_DIR = _img_folder
                if DEBUG_ENABLED:
                    print('startup image folder: ', self.IMG_HOME_DIR)
                return
        else:
            try:
                os.mkdir(_img_folder)
                if DEBUG_ENABLED:
                    print('folder: {}'.format(_img_folder), ' has been created')
            except:
                return

        _img_folder = os.path.join(_img_folder, 'Saved Pictures') # go level down to ~/Pictures/Saved Pictures/
        if _img_folder_code == 0:
            try:
                os.mkdir(_img_folder)
                if DEBUG_ENABLED:
                    print('folder: {}'.format(_img_folder), ' has been created')
            except:
                return

        _local_img_folder = os.path.join(home_dir, 'shch_img_browser_imgs')
        _img_files = fnc_GetImageFileList(_local_img_folder, legit_extensions)
        for _img_file in _img_files:
            try:
                _source = fnc_GetImageFilePath(_local_img_folder, _img_file)
                _destination = fnc_GetImageFilePath(_img_folder, _img_file)
                copyfile(_source, _destination)
                if DEBUG_ENABLED:
                    print('file: {}'.format(_img_file), ' has been transfered')
            except:
                if DEBUG_ENABLED:
                    print('file: {}'.format(_img_file), ' cannot be transfered')

        self.IMG_HOME_DIR = _img_folder
        if DEBUG_ENABLED:
            print('startup image folder: ', self.IMG_HOME_DIR)
        # end of function

    #!
    # returns the path for the image folder to be used when this program is run for the first time.
    # Args: none.
    # Returns : path_to_img_folder : str
    def fnc_getStartDir(self):
        return self.IMG_HOME_DIR
        # end of function
    # end of class (ImgBrowserStartDir)

# screen centering
#:-)
#:-)
#:-)
#:-)
#:-)
#:-)
#:-)
#:-)
#:-]
#:-]
#:-]
#:-]
#:-]
#:-]
#:-]
#:-]
# end of screen centering
