#!/usr/bin/env python

import cairo
import gi
gi.require_version('Gtk' , '3.0')

from gettext import gettext as _

import os
import sys

from TurtleArt.tablock import Media
from TurtleArt.taconstants import CONSTANTS
from TurtleArt.tatype import *
from TurtleArt.tawindow import TurtleArtWindow

from gi.repository import Gtk
from gi.repository import Gdk

# search sys.path for a dir containing TurtleArt/tawindow.py
# path to the toplevel directory of the TA installation
_TA_INSTALLATION_PATH = None
for path in sys.path:
    try:
        entries = os.listdir(path)
    except OSError:
        continue
    if "TurtleArt" in entries:
        new_path = os.path.join(path, "TurtleArt")
        try:
            new_entries = os.listdir(new_path)
        except OSError:
            continue
        if "tawindow.py" in new_entries:
            _TA_INSTALLATION_PATH = path
            break
# if the TA installation path was not found, notify the user and refuse to run
if _TA_INSTALLATION_PATH is None:
    print _("The path to the TurtleArt installation must be listed in the "
            "environment variable PYTHONPATH.")
    exit(1)

_PLUGIN_SUBPATH = 'plugins'
_MACROS_SUBPATH = 'macros'


class DummyTurtleMain(object):

    """Keep the main objects for running a dummy TA window in one place.
    (Try not to have to inherit from turtleblocks.TurtleMain.)
    """

    def __init__(self, win, name="exported project"):
        """Create a scrolled window to contain the turtle canvas.
        win -- a GTK toplevel window
        """
        self.win = win
        self.set_title = self.win.set_title

        # setup a scrolled container for the canvas
        self.vbox = Gtk.VBox(False, 0)
        self.vbox.show()
        self.sw = Gtk.ScrolledWindow()
        self.sw.set_policy(Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
        self.sw.show()
        self.canvas = Gtk.DrawingArea()
        width = Gdk.screen_width() * 2
        height = Gdk.screen_height() * 2
        self.canvas.set_size_request(width, height)
        self.sw.add_with_viewport(self.canvas)
        self.canvas.show()
        self.vbox.pack_end(self.sw, True, True, 0)
        self.win.add(self.vbox)
        self.win.show_all()

        # exported code is always in interactive mode
        interactive = True

        # copied from turtleblocks.TurtleMain._build_window()
        if interactive:
            gdk_win = self.canvas.get_window()
            cr = gdk_win.cairo_create()
            surface = cr.get_target()
        else:
            img_surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
                                             1024, 768)
            cr = cairo.Context(img_surface)
            surface = cr.get_target()
        self.turtle_canvas = surface.create_similar(
            cairo.CONTENT_COLOR, max(1024, Gdk.screen_width() * 2),
            max(768, Gdk.screen_height() * 2))

        # instantiate an instance of a dummy sub-class that supports only
        # the stuff TurtleGraphics needs
        # TODO don't hardcode running_sugar
        share_path = _TA_INSTALLATION_PATH
        self.tw = TurtleArtWindow(self.canvas, _TA_INSTALLATION_PATH,
                                  share_path,
                                  turtle_canvas=self.turtle_canvas,
                                  parent=self, running_sugar=False,
                                  running_turtleart=False)

        self.name = name

    def _quit_ta(self, widget=None, e=None):
        """Quit all plugins and the main window. No need to prompt the user
        to save their work, since they cannot change anything.
        """
        for plugin in self.tw.turtleart_plugins:
            if hasattr(plugin, 'quit'):
                plugin.quit()
        Gtk.main_quit()
        exit()


def get_tw():
    """ Create a GTK window and instantiate a DummyTurtleMain instance. Return
    the TurtleArtWindow object that holds the turtles and the canvas.
    """
    # copied from turtleblocks.TurtleMain._setup_gtk()

    win = Gtk.Window()
    gui = DummyTurtleMain(win=win, name=sys.argv[0])
    # TODO re-enable this code (after giving gui the right attributes)
    # win.set_default_size(gui.width, gui.height)
    # win.move(gui.x, gui.y)
    win.maximize()
    win.set_title(str(gui.name))
    # if os.path.exists(os.path.join(gui._execdirname, gui._ICON_SUBPATH)):
    #     win.set_icon_from_file(os.path.join(gui._execdirname,
    #                                         gui._ICON_SUBPATH))
    win.show()
    win.connect('delete_event', gui._quit_ta)

    return gui.tw
