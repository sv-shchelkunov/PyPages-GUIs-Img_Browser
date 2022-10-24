import lib.shch_img_browser_lib as Shch

from PIL import ImageTk as pil_image_tk
from PIL import Image as pil_image
import tkinter as tk
from tkinter import messagebox as tk_messagebox
from tkinter import filedialog as tk_filedialog

DEBUG_ENABLED = False

class ShchImgBrowser():
    __program_version__ = """
    Shch Image Browser version 0.0.1 (September, 07, 2021)
    """
    __application_help__ = """
    This app is to browse image files in a specified folder.
    To select the folder of choice, use |Folder| > |Select Folder| in the main menu.
    To select/unselect image files' extensions use |Extensions| > |Select Extensions|.
    The middle button under the shown image can be used to autoplay images.
    The sliding bar under it can be moved to adjust the frequency at which images are autoplayed.
    The two side buttons further under with the (-) and (+) symbols will change the image size.
    """
    __doc__ = __program_version__ + __application_help__
    #!
    def __init__(self, tk_window_main):
        self.CONFIG = Shch.ImgBrowserConfig()

        self.IMAGE_SCALES = (.1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .65, .7, .75) # predefined image scales (1 = full screen).
        # self.CONFIG.IMAGE_SCALE_INDEX is normalized in the function  fnc_showImage(...)
        self.IMAGE_FLIP_LEFT_RIGHT = 0
        self.IMAGE_FLIP_TOP_BOTTOM = 0
        self.IMAGE_ROTATIONS = (None, pil_image.ROTATE_90, pil_image.ROTATE_180, pil_image.ROTATE_270)
        self.IMAGE_ROTATION_INDEX = 0

        self.WIDGET_FONT_SIZES = (6, 8, 10, 12, 14, 16, 18, 22, 24, 28, 32, 36) # predefined scales for buttons, and labels
        # self.CONFIG.WIDGET_FONT_SIZE_INDEX is normalized in the function font (...)


        self.AUTOPLAY = 0 # if 0 - no autoplay; if 1 - autoplay (to be used by fnc_autoplay(...))
        self.AUTOPLAY_QUEUE = []
        self.AUTOPLAY_INTERVAL = 15 # in tics (one tic = 100 ms).

        self.tk_main = tk_window_main
        self.tk_main.protocol("WM_DELETE_WINDOW", self.fnc_paintStop)
        self.fnc_paintStart()
        # below we use fnc_paint(...) to obtain the list of image files in a given folder (see self.CONFIG.IMAGE_FOLDER above)
        self.fnc_paint()
        # end of __init__
    #!
    # shows little help about this application.
    # Args: none.
    # Returns: nothing.
    def fnc_help(self):
        tk_messagebox.showinfo('Help:', ShchImgBrowser.__application_help__)
        # end of function
    #!
    # shows the version number.
    # Args: none.
    # Returns: nothing.
    def fnc_about(self):
        tk_messagebox.showinfo('About this program:', ShchImgBrowser.__program_version__)
        # end of function
    #!
    # stops this program.It will show a prompt to confirm the user choice.
    # Args:
    #   kwargs : (typical kwargs)
    #       'save' : <any value>
    #           This is used to save settings (image folder and image files' extensions) before exit.
    # Returns: nothing.
    def fnc_exit(self, **kwargs):
        if tk_messagebox.askyesno("Are you sure?","Do you wish to stop?"):
            if 'save' in kwargs:
                self.CONFIG.fnc_save(folder=1, extensions=1, image_scale=1, widget_font_size=1)

            self.fnc_paintStop()
        # end of function

    #!
    # starts construction of the slide show main window.
    #   This method creates all menus.
    # Args: none.
    # Returns: nothing.
    def fnc_paintStart(self, **kwargs):
        if ('paint_again' in kwargs):
            if len(self.__m__) > 0:
                self.tk_menu_main.delete(0, len(self.__m__))
        else:
            self.tk_main.title('-- Shch Image Browser --')
            if Shch.fnc_IsExistingFile(self.CONFIG.ICO_PATH):
                self.tk_main.iconbitmap(self.CONFIG.ICO_PATH)
            # creating a menu to be able to navigate to a desired folder, or select desired files' extentions, etc
            self.tk_menu_main = tk.Menu(self.tk_main)
            self.tk_main.config(menu= self.tk_menu_main)
            # creating a dict to hold the references to the menu drop-downs
            self.__m__ = dict()
            # creating list to hold references to frames
            self.__f__ = dict() # it is used extensively in fnc_paint(...)
            self.IS_CLOSING = False

        self.__m__['tk_menu_folder'] = tk.Menu(self.tk_menu_main, font=('TkTextFont', self.font(cuarto=1)))
        self.tk_menu_main.add_cascade(label= 'Folder', menu= self.__m__['tk_menu_folder'])
        self.__m__['tk_menu_extensions'] = tk.Menu(self.tk_menu_main, font=('TkTextFont', self.font(cuarto=1)))
        self.tk_menu_main.add_cascade(label= 'Extensions', menu=  self.__m__['tk_menu_extensions'])
        self.__m__['tk_menu_image'] =  tk.Menu(self.tk_menu_main, font=('TkTextFont', self.font(cuarto=1)))
        self.tk_menu_main.add_cascade(label= 'Image', menu= self.__m__['tk_menu_image'])
        self.__m__['tk_menu_browser'] =  tk.Menu(self.tk_menu_main, font=('TkTextFont', self.font(cuarto=1)))
        self.tk_menu_main.add_cascade(label= 'Browse', menu= self.__m__['tk_menu_browser'])
        self.__m__['tk_menu_display'] =  tk.Menu(self.tk_menu_main, font=('TkTextFont', self.font(cuarto=1)))
        self.tk_menu_main.add_cascade(label= 'Display', menu= self.__m__['tk_menu_display'])
        self.__m__['tk_menu_misc'] = tk.Menu(self.tk_menu_main, font=('TkTextFont', self.font(cuarto=1)))
        self.tk_menu_main.add_cascade(label= 'Mics', menu= self.__m__['tk_menu_misc'])

        # creating menu commands
        # Folder commands
        self.__m__['tk_menu_folder'].add_command(label= 'Select Folder', command= self.fnc_selectImageFolder)
        self.__m__['tk_menu_folder'].add_command(label= '-?- Remember Folder', command= lambda: self.CONFIG.fnc_save(folder=1))

        # Extensions commands
        self.__m__['tk_menu_extensions'].add_command(label= 'Select Extensions', command= lambda: self.fnc_adjustExtensions(0))
        self.__m__['tk_menu_extensions'].add_command(label= 'Add Extension (+)', command= lambda: self.fnc_adjustExtensions(1))
        self.__m__['tk_menu_extensions'].add_command(label= 'Remove Extension (-)', command= lambda: self.fnc_adjustExtensions(-1))
        self.__m__['tk_menu_extensions'].add_command(label= '-?- Remember Extensions', command= lambda: self.CONFIG.fnc_save(extensions=1))

        # Image commands
        self.__m__['tk_menu_image'].add_command(label= '(+) Increase Size', command= lambda: self.fnc_scale(1))
        self.__m__['tk_menu_image'].add_command(label= '(-) Reduce Size', command= lambda: self.fnc_scale(-1))
        self.__m__['tk_menu_image'].add_command(label= '_o~ Rotate, CW', command= lambda: self.fnc_rotate(-1))
        self.__m__['tk_menu_image'].add_command(label= '~o_ Rotate, CCW', command= lambda: self.fnc_rotate(1))
        self.__m__['tk_menu_image'].add_command(label= '|| Flip, Left-Right', command= lambda: self.fnc_flip(1))
        self.__m__['tk_menu_image'].add_command(label= '= Flip, Top-Buttom', command= lambda: self.fnc_flip(-1))
        self.__m__['tk_menu_image'].add_command(label= '. Reset', command= self.fnc_reset)
        self.__m__['tk_menu_image'].add_command(label= '-?- Remember Image Scale', command= lambda: self.CONFIG.fnc_save(image_scale=1))

        # Browser commands
        self.__m__['tk_menu_browser'].add_command(label= 'Play / Pause', command= lambda: self.fnc_autoplay())
        self.__m__['tk_menu_browser'].add_command(label= '>> +10 Forward, Fast', command= lambda: self.fnc_next(10))
        self.__m__['tk_menu_browser'].add_command(label= '>> +25 Forward, Fast Super', command= lambda: self.fnc_next(25))
        self.__m__['tk_menu_browser'].add_command(label= '>>+100 Forward, Fast Ultra', command= lambda: self.fnc_next(100))
        self.__m__['tk_menu_browser'].add_command(label= '-10 << Backward, Fast', command= lambda: self.fnc_next(-10))
        self.__m__['tk_menu_browser'].add_command(label= '-25 << Backward, Fast Super', command= lambda: self.fnc_next(-25))
        self.__m__['tk_menu_browser'].add_command(label= '-100<< Backward, Fast Ultra', command= lambda: self.fnc_next(-100))

        # Display commands
        self.__m__['tk_menu_display'].add_command(label= '|+| Larger Buttons', command= lambda: self.fnc_regDisplay(1))
        self.__m__['tk_menu_display'].add_command(label= '|-| Smaller Buttons', command= lambda: self.fnc_regDisplay(-1))
        self.__m__['tk_menu_display'].add_command(label= '-?- Remember Button Scale', command= lambda: self.CONFIG.fnc_save(widget_font_size=1))

        # Miscellaneous commands
        self.__m__['tk_menu_misc'].add_command(label= 'Help', command= self.fnc_help)
        self.__m__['tk_menu_misc'].add_command(label= 'About', command= self.fnc_about)
        self.__m__['tk_menu_misc'].add_command(label= 'Exit', command= self.fnc_exit)
        self.__m__['tk_menu_misc'].add_command(label= 'Remember & Exit', command= lambda: self.fnc_exit(save=1))
        # end of function
    #!
    # completes constrution of the slide show main window.
    # Updates self.CURRENT_IMAGE_INDEX, self.IMAGE_FILES_LIST, paints the new image and (re)paints the buttons (again).
    #   This method display the zeroth image, and all functional buttons.
    # Args:
    #   kwargs : typical keyword arguments
    #       'autoplay_cancel' : <any value>
    #           If this is set, autoplay will be canceled.
    #       'image_keep' : <any value>
    #           This must be set before re-painting with the newly specified button/label sizes.
    # Returns: nothing.
    def fnc_paint(self, **kwargs):
        if self.IS_CLOSING:
            return

        if 'autoplay_cancel' in kwargs:
            self.fnc_autoplay(stop=1)

        if not ('image_keep' in kwargs):
            self.CURRENT_IMAGE_INDEX = 0
            self.IMAGE_FILES_LIST = Shch.fnc_GetImageFileList(self.CONFIG.IMAGE_FOLDER, self.CONFIG.IMAGE_FILE_EXTENSIONS)

        if len(self.__f__) > 0:
            [self.__f__[_key].destroy() for _key in self.__f__]

        if len(self.IMAGE_FILES_LIST) < 1:
            self.__f__['tk_frame_warning'] = tk.Frame(self.tk_main)
            self.__f__['tk_frame_warning'].pack(padx= 5, pady= 5)

            self.tk_label_w_no_images_warning = tk.Label(
                        self.__f__['tk_frame_warning'],
                        text = "Hi! There are no legit images in the selected folder.", font = ('Times', 14),
                        padx = 12, pady = 10,
                        relief = tk.SUNKEN, bd = 8
                        )
            self.tk_label_showing_how_to_choose_folder = tk.Label(
                        self.__f__['tk_frame_warning'],
                        text = "To choose another folder use |Folder| > |Select Folder|.", font = ('Times', 14),
                        padx = 2, pady = 10,
                        relief = tk.RAISED, bd = 8
                        )
            self.tk_label_w_extensions_warning = tk.Label(
                        self.__f__['tk_frame_warning'],
                        text = "Also, check your image files' extensions (i.e. image types).", font = ('Times', 13),
                        padx = 1, pady = 10,
                        relief = tk.SUNKEN, bd = 8
                        )
            self.tk_label_showing_how_to_choose_extensions = tk.Label(
                        self.__f__['tk_frame_warning'],
                        text = "To select extensions use |Extensions| > |Select Extensions|.", font = ('Times', 13),
                        padx = 6, pady = 10,
                        relief = tk.RAISED, bd = 8
                        )
            self.tk_label_w_no_images_warning.pack(ipadx= 12, ipady= 10)
            self.tk_label_showing_how_to_choose_folder.pack(ipadx= 6, ipady= 10)
            self.tk_label_w_extensions_warning.pack(ipadx= 12, ipady= 10)
            self.tk_label_showing_how_to_choose_extensions.pack(ipadx= 6, ipady= 10)

            return

        # frame to place the image in
        self.__f__['tk_frame_image'] = tk.Frame(self.tk_main)
        self.__f__['tk_frame_image'].pack(padx= 1, pady= 1)
        # frame for tk_button_back, tk_button_forward and tk_button_autoplay
        self.__f__['tk_frame_button'] = tk.Frame(self.tk_main)
        self.__f__['tk_frame_button'].pack(padx= 1, pady= 1)
        # frame for tk_delay_scale
        self.__f__['tk_frame_autoplay'] = tk.Frame(self.tk_main)
        self.__f__['tk_frame_autoplay'].pack(padx= 3, pady= 1)
        # frame for tk_scale_down, tk_scale_up and tk_exit_button
        self.__f__['tk_frame_scale'] = tk.Frame(self.tk_main)
        self.__f__['tk_frame_scale'].pack(padx= 5, pady= 5)

        # button to autoplay, or move one image at a time either forward or back
        self.tk_button_back_fast = tk.Button(
                    self.__f__['tk_frame_button'],
                    padx= 3, pady= 3,
                    text='-10<<', font = ('Arial', self.font(primero=1)), fg = 'black',
                    relief = tk.GROOVE, bd = 7,
                    command= lambda: self.fnc_next(-10),
                    )
        self.tk_button_back = tk.Button(
                    self.__f__['tk_frame_button'],
                    text='<<', font = ('Arial', self.font(primero=1)), fg = 'black',
                    relief = tk.GROOVE, bd = 10,
                    command= lambda: self.fnc_next(-1),
                    )
        self.tk_button_autoplay = tk.Button(
                    self.__f__['tk_frame_button'],
                    text='play', font =('Helvetica', self.font(primero=1)), fg = '#b35900',
                    relief = tk.GROOVE, bd = 10,
                    command= lambda: self.fnc_autoplay()
                    )
        self.tk_button_forward = tk.Button(
                    self.__f__['tk_frame_button'],
                    text='>>', font = ('Arial', self.font(primero=1)), fg = 'black',
                    relief = tk.GROOVE, bd = 10,
                    command= lambda: self.fnc_next(1),
                    )
        self.tk_button_forward_fast = tk.Button(
                    self.__f__['tk_frame_button'],
                    pady= 3,
                    text='>>+10', font = ('Arial', self.font(primero=1)), fg = 'black',
                    relief = tk.GROOVE, bd = 7,
                    command= lambda: self.fnc_next(10),
                    )
        self.tk_button_back_fast.grid(row= 1, column= 0,)
        self.tk_button_back.grid(row= 1, column= 1,)
        self.tk_button_autoplay.grid(row= 1, column= 2)
        self.tk_button_forward.grid(row= 1, column= 3,)
        self.tk_button_forward_fast.grid(row= 1, column= 4,)

        # scale to provide the delay value when autoplaying images. The dleay value is in tics.
        #   1 tic = 100 ms.
        self.tk_scale_delay = tk.Scale(
                    self.__f__['tk_frame_autoplay'],
                    from_= 1, to= 100,
                    orient='horizontal',
                    font= ('TkTextFont', self.font(tercero=1)),
                    )
        self.tk_scale_delay.grid(row= 0, column= 0, columnspan=3)
        self.tk_scale_delay.set(self.AUTOPLAY_INTERVAL)

        # buttons to scale images up or down. Also the exit button is grouped togtehr with those two.
        self.tk_button_scale_down = tk.Button(
                    self.__f__['tk_frame_scale'],
                    padx= 4,
                    text='(-)', font = ('Arial', self.font(tercero=1)), fg = 'green',
                    relief = tk.GROOVE, bd = 7,
                    command= lambda: self.fnc_scale(-1),
        )
        self.tk_button_exit = tk.Button(
                    self.__f__['tk_frame_scale'],
                    text='leave', font = ('Arial', self.font(cuarto=1)), fg = 'red',
                    relief = tk.RIDGE, bd = 7,
                    command= self.fnc_exit,
                    )
        self.tk_button_scale_up = tk.Button(
                    self.__f__['tk_frame_scale'],
                    text='(+)', font = ('Arial', self.font(tercero=1)), fg = 'green',
                    relief = tk.GROOVE, bd = 7,
                    command= lambda: self.fnc_scale(1),
        )
        self.tk_button_scale_down.grid(row= 0, column= 0)
        self.tk_button_exit.grid(row= 0, column= 1)
        self.tk_button_scale_up.grid(row= 0, column= 2)

        # loading and displaying the zeroth image.
        self.fnc_next(0)
        # end of function
    #!
    #
    def fnc_paintStop(self):
        self.IS_CLOSING = True
        self.tk_main.destroy()
        # end of function

    #!
    # shows the image with the specified name residing in self.CONFIG.IMAGE_FOLDER.
    # Args:
    #   image_file : str
    #       The name of an image file (for instance My 101thImage.jpg).
    # Returns: success_code : int
    #   This is 1 if success, and 0 otherwise
    def fnc_showImage(self, image_file):
        _img_path = Shch.fnc_GetImageFilePath(self.CONFIG.IMAGE_FOLDER, image_file)
        _img_name = image_file
        _img_okay = True
        try:
            _img = pil_image.open(_img_path)
        except:
            _img_okay = False

        if _img_okay:
            # Here we flip the image
            if not (self.IMAGE_FLIP_LEFT_RIGHT == 0):
                try:
                    _img = _img.transpose(pil_image.FLIP_LEFT_RIGHT)
                except:
                    pass
            if not (self.IMAGE_FLIP_TOP_BOTTOM == 0):
                try:
                    _img = _img.transpose(pil_image.FLIP_TOP_BOTTOM)
                except:
                    pass

            # Below the image is rotated (in 90 degree increments)
            if not (self.IMAGE_ROTATION_INDEX == 0):
                try:
                    _img = _img.transpose(self.IMAGE_ROTATIONS[self.IMAGE_ROTATION_INDEX])
                except:
                    pass

            _img_width, _img_height = _img.size
            _img_info = 'width: {}, height: {}'.format(_img_width, _img_height)

            _screen_width = self.tk_main.winfo_screenwidth()
            _screen_height = self.tk_main.winfo_screenheight()
            _width_ratio = float(_screen_width) /  float(_img_width)
            _height_ratio = float (_screen_height) / float(_img_height)

            # Here we are computing the desired image scale...
            if self.CONFIG.IMAGE_SCALE_INDEX < 0:
                self.CONFIG.IMAGE_SCALE_INDEX = 0
            if self.CONFIG.IMAGE_SCALE_INDEX > (len(self.IMAGE_SCALES) - 1):
                self.CONFIG.IMAGE_SCALE_INDEX = len(self.IMAGE_SCALES) - 1
            _img_scale = self.IMAGE_SCALES[self.CONFIG.IMAGE_SCALE_INDEX] * (_width_ratio if (_width_ratio < _height_ratio) else _height_ratio)
            _img_width = int(_img_scale * _img_width)
            _img_height = int(_img_scale * _img_height)
            # and loading and resizing the image
            try:
                self.img = pil_image_tk.PhotoImage(_img.resize((_img_width, _img_height), pil_image.ANTIALIAS))
            except:
                _img_okay = False

        try:
            self.tk_label_w_img.destroy()
            self.tk_label_w_img_info.destroy()
            self.tk_label_w_img_name.destroy()
        except:
            pass
        self.tk_label_w_img = tk.Label(
                    self.__f__['tk_frame_image'],
                    image = self.img,
                    ) if _img_okay else\
                    tk.Label(
                    self.__f__['tk_frame_image'],
                    text = "Bad Image", font = ('Arial', 16),
                    )
        self.tk_label_w_img_name = tk.Label(
                    self.__f__['tk_frame_image'],
                    text = _img_name, font = ('Times', self.font(segundo=1)),
                    anchor= 'w'
                    )
        self.tk_label_w_img_info = tk.Label(
                    self.__f__['tk_frame_image'],
                    text = _img_info if _img_okay else "Bad Image",
                    font = ('Times', self.font(segundo=1)),  fg = 'black' if _img_okay else 'red',
                    anchor= 'e'
                    )

        self.tk_label_w_img.grid(row= 0, column= 0, columnspan= 2, sticky="we")
        self.tk_label_w_img_name.grid(row= 1, column= 0, sticky='w')
        self.tk_label_w_img_info.grid(row= 1, column= 1, sticky='e')

        if _img_okay:
            return 1
        return 0
    #!
    # shows the next image (from self.IMAGE_FILES_LIST).
    #   This function is used as a callback by the back and forward buttons.
    # Args:
    # increment: int
    #   This is used to obtain the index of the next image. If the new index is less than zero, it will be equated to zero.
    #   If the new index is greater than the last index in the file_list, it will be equated to the last index.
    def fnc_next(self, increment):
        if len(self.IMAGE_FILES_LIST) < 1:
            return

        self.CURRENT_IMAGE_INDEX += increment
        _last_image_index = len(self.IMAGE_FILES_LIST) - 1

        if self.CURRENT_IMAGE_INDEX < 0:
            self.CURRENT_IMAGE_INDEX = 0
        if  self.CURRENT_IMAGE_INDEX > _last_image_index:
            self.CURRENT_IMAGE_INDEX = _last_image_index

        self.tk_button_back_fast['state'] =  'disabled' if (self.CURRENT_IMAGE_INDEX <= 0) else 'active'
        self.tk_button_back['state'] =  'disabled' if (self.CURRENT_IMAGE_INDEX <= 0) else 'active'
        self.tk_button_forward['state'] = 'disabled' if (self.CURRENT_IMAGE_INDEX >= _last_image_index) else 'active'
        self.tk_button_forward_fast['state'] = 'disabled' if (self.CURRENT_IMAGE_INDEX >= _last_image_index) else 'active'

        _success_code = self.fnc_showImage(self.IMAGE_FILES_LIST[self.CURRENT_IMAGE_INDEX])
        # end of function
    #!
    # play images in self.IMAGE_FILES_LIST
    #   This function is a callback for tk_button_autoplay (or Play/Pause command in the menu).
    # Args:
    #   kwargs:
    #       'stop' : <any value>
    #           The variable is used to stop autoplaying. If it presents, it takes precidence over 'loop'.
    #       'loop': <any value>
    #           The variable is used to distiguish between the callback calls placed by the autoplay_button, or by the
    #           after(...) method from within fnc_autoplay(...) itself. Do not use this keyword variable when placing
    #           calls from under e.g. tk_button_autoplay. Use loop= <any value>, when placing callback calls from under
    #           fnc_autoplay(...).
    #   Returns: nothing.
    def fnc_autoplay(self, **kwargs):
        if len(self.IMAGE_FILES_LIST) < 1:
            return

        _stop_in_kwargs = 'stop' in kwargs

        if ('loop' in kwargs) and (not _stop_in_kwargs):
            if self.CURRENT_IMAGE_INDEX >= len(self.IMAGE_FILES_LIST) - 1:
                self.CURRENT_IMAGE_INDEX = -1
            self.fnc_next(1)

            _interval = 100 * self.tk_scale_delay.get()
            self.AUTOPLAY_QUEUE = [self.tk_main.after(_interval, lambda: self.fnc_autoplay(loop=1))]
            return

        [self.tk_main.after_cancel(_each) for _each in self.AUTOPLAY_QUEUE]
        self.AUTOPLAY_QUEUE = []

        if _stop_in_kwargs:
            self.AUTOPLAY = 0
            self.tk_button_autoplay['text'] = 'play'
            return

        self.AUTOPLAY += 1
        if self.AUTOPLAY > 1:
            self.AUTOPLAY = 0

        if self.AUTOPLAY == 0:
            self.tk_button_autoplay['text'] = 'play'
            return

        _interval = 100 * self.tk_scale_delay.get()
        self.AUTOPLAY_QUEUE = [self.tk_main.after(_interval, lambda: self.fnc_autoplay(loop=1))]
        self.tk_button_autoplay['text'] = 'pause'
        # end of function

    #!
    # changes the image scale relative to the screen.
    #   This function is a callback used by tk_button_scale_up and tk_button_scale_down (and their conterparts in the menu).
    # Args:
    #   scale_index_increment : int
          # This is used to increment self.CONFIG.IMAGE_SCALE_INDEX, which is used by fnc_showImage(...) to puul out
    #       the desired scale from self.IMAGE_SCALES
    # Returns: nothing.
    def fnc_scale(self, scale_index_increment):
        if len(self.IMAGE_FILES_LIST) < 1:
            return

        self.CONFIG.IMAGE_SCALE_INDEX += scale_index_increment
        # self.CONFIG.IMAGE_SCALE_INDEX is normalized in the function  fnc_showImage(...)

        self.fnc_next(0)
        # end of function
    #!
    # flips the image horizontally.
    #   This function is a callback used by the flip commands in the menu.
    # Args:
    #   how : int
    #       If how == 1, the image is flipped left-right (horizontally).
    #       If  how = -1, the image is flipped top-buttom (vertically).
    # Returns: nothing.
    def fnc_flip(self, how):
        if len(self.IMAGE_FILES_LIST) < 1:
            return

        if how == 1:
            self.IMAGE_FLIP_LEFT_RIGHT += 1
            if self.IMAGE_FLIP_LEFT_RIGHT > 1:
                self.IMAGE_FLIP_LEFT_RIGHT = 0
        if how == -1:
            self.IMAGE_FLIP_TOP_BOTTOM += 1
            if self.IMAGE_FLIP_TOP_BOTTOM > 1:
                self.IMAGE_FLIP_TOP_BOTTOM = 0

        if (how == 1) or (how == -1):
            self.fnc_next(0)
        # end of function
    #!
    # rotates the image (in 90 degree increments).
    #   This function is a callback used by the rotate commands in the menu.
    # Args:
    #   how : int
    #       If how == 1, the image rotated CCW. If how = -1, the image is rotated CW.
    # Returns: nothing.
    def fnc_rotate(self, how):
        if len(self.IMAGE_FILES_LIST) < 1:
            return

        if (how == 1) or (how == -1):
            self.IMAGE_ROTATION_INDEX += how

            if self.IMAGE_ROTATION_INDEX < 0:
                self.IMAGE_ROTATION_INDEX += 4
            if self.IMAGE_ROTATION_INDEX > 3:
                self.IMAGE_ROTATION_INDEX = 0

            self.fnc_next(0)
        # end of function
    #!
    # resets the image by removing all rotations, flips, and reverting to the maximum scale.
    #   This function is a callback used by Reset command in the menu.
    # Args: none.
    # Returns: nothing.
    def fnc_reset(self):
        if len(self.IMAGE_FILES_LIST) < 1:
            return

        # self.CONFIG.IMAGE_SCALE_INDEX = len(self.IMAGE_SCALES) - 1
        self.IMAGE_FLIP_LEFT_RIGHT = 0
        self.IMAGE_FLIP_TOP_BOTTOM = 0
        self.IMAGE_ROTATION_INDEX = 0

        self.fnc_next(0)
        # end of function

    #!
    # changes button sizes on the display.
    # Args:
    #   index_increment : int
    #       The amount by which to increment or decrement the (current) size index.
    #       If the new index is < 0, it is set to 0. If the new index is larger than the last
    #       index of self.WIDGET_FONT_SIZES, it is set to the last index of self.WIDGET_FONT_SIZES
    # Returns: nothing.
    def fnc_regDisplay(self, index_increment, **kwargs):
        self.CONFIG.WIDGET_FONT_SIZE_INDEX += index_increment
        # self.CONFIG.WIDGET_FONT_SIZE_INDEX is normalized in the function font(...)

        _was_autoplaying = (self.AUTOPLAY == 1)
        _autoplaying_interval = self.tk_scale_delay.get()

        self.fnc_paintStart(paint_again=1)
        self.fnc_paint(autoplay_cancel=1, image_keep=1)
        self.tk_scale_delay.set(_autoplaying_interval)

        if _was_autoplaying:
            self.fnc_autoplay()
        # end of function
    #!
    # returns the font size
    # Args:
    #   kwargs: typical keyword arguments.
    #       'primero' : <any value
    #           Sets the returned value to self.WIDGET_FONT_SIZES[self.WIDGET_FONT_SIZE_INDEX]
    #       'segundo': <any value>
    #           Sets the returned value to 12/14 of 'primero'
    #       'tercero': <any value>
    #           Sets the returned value to 11/14 of 'primero'
    #       'cuarto': <any value>
    #           Sets the returned value to 10/14 of 'primero'
    #       'quinto': <any value>
    #           Sets the returned value to 9/14 of 'primero'
    #       'sexto': <any value>
    #           Sets the returned value to 8/14 of 'primero'
    # Returns: font_size : int
    #   If no kwargs are given it will default to 'primero'.
    def font(self, **kwargs):
        if self.CONFIG.WIDGET_FONT_SIZE_INDEX < 0:
            self.CONFIG.WIDGET_FONT_SIZE_INDEX = 0
        if self.CONFIG.WIDGET_FONT_SIZE_INDEX > len(self.WIDGET_FONT_SIZES) - 1:
            self.CONFIG.WIDGET_FONT_SIZE_INDEX = len(self.WIDGET_FONT_SIZES) - 1

        if 'primero' in kwargs:
            return self.WIDGET_FONT_SIZES[self.CONFIG.WIDGET_FONT_SIZE_INDEX]

        _coeff = 1.0

        if 'segundo' in kwargs:
            _coeff = 12/14.
        if 'tercero' in kwargs:
            _coeff = 11/14.
        if 'cuarto' in kwargs:
            _coeff = 10/14.
        if 'quinto' in kwargs:
            _coeff = 9/14.
        if 'sexto' in kwargs:
            _coeff = 8/14.

        return int(_coeff* self.WIDGET_FONT_SIZES[self.CONFIG.WIDGET_FONT_SIZE_INDEX])
    #!
    # selects the folder with images.
    # Args: no arguments.
    # Returns:
    def fnc_selectImageFolder(self):
        _img_folder = tk_filedialog.askdirectory()
        if (len(_img_folder) > 0) and (not (_img_folder == self.CONFIG.IMAGE_FOLDER)):
            self.CONFIG.IMAGE_FOLDER = _img_folder
            self.fnc_paint(autoplay_cancel=1)
        # end of function
    #!
    # callback for |Extensions| > |Select Extensions|,
    # callback for |Extensions| > |(+) Add Extension|,
    # callback for |Extensions| > |(-) Remove Extension|
    def fnc_adjustExtensions(self, action):
        if action == 1:
            _extAdj = Shch.ExtsIns(self.tk_main, self.CONFIG.fnc_insertExtension, ico_path=self.CONFIG.ICO_PATH)
        elif action == -1:
            _extAdj = Shch.ExtsRem(self.tk_main, self.CONFIG.fnc_removeExtension, ico_path=self.CONFIG.ICO_PATH)
        elif action == 0:
            _extAdj = Shch.ExtsAdj(\
                        self.tk_main, self.CONFIG.fnc_selectExtensions,\
                        exts_list = self.CONFIG.IMAGE_FILE_EXTENSIONS, ico_path=self.CONFIG.ICO_PATH)
        else:
            return

        _extAdj.top.focus_set()
        _extAdj.top.grab_set()
        if DEBUG_ENABLED:
            print('...before _extAdj.top.wait_window()')
        _extAdj.top.wait_window()
        if DEBUG_ENABLED:
            print('...after _extAdj.top.wait_window()')
        if not _extAdj.IS_CANCELED:
            self.fnc_paint(autoplay_cancel=1)
        # end of function
    # end of class

if __name__ == "__main__":
    tk_window_main = tk.Tk()
    # centering the window...
    screen_width = tk_window_main.winfo_screenwidth()
    screen_height = tk_window_main.winfo_screenheight()
    tk_window_main.geometry('{}x{}+{}+{}'.format(screen_width, screen_height, 0, 0))

    slide_show = ShchImgBrowser(tk_window_main)
    tk_window_main.mainloop()

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
