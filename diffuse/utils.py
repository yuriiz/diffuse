import gettext
import gi
import locale
import os
import sys

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# convenience class for displaying a message dialogue
class MessageDialog(Gtk.MessageDialog):
    def __init__(self, parent, type, s):
        if type == Gtk.MessageType.ERROR:
            buttons = Gtk.ButtonsType.OK
        else:
            buttons = Gtk.ButtonsType.OK_CANCEL
        Gtk.MessageDialog.__init__(self, parent = parent, destroy_with_parent = True, message_type = type, buttons = buttons, text = s)
        self.set_title(APP_NAME)

# platform test
def isWindows():
    return os.name == 'nt'

# convenience function to display debug messages
def logDebug(s):
    pass #sys.stderr.write('%s: %s\n', (APP_NAME, s))

# report error messages
def logError(s):
    m = MessageDialog(None, Gtk.MessageType.ERROR, s)
    m.run()
    m.destroy()

# create nested subdirectories and return the complete path
def make_subdirs(p, ss):
    for s in ss:
        p = os.path.join(p, s)
        if not os.path.exists(p):
            try:
                os.mkdir(p)
            except IOError:
                pass
    return p

# use the program's location as a starting place to search for supporting files
# such as icon and help documentation
if hasattr(sys, 'frozen'):
    app_path = sys.executable
else:
    app_path = os.path.realpath(sys.argv[0])
bin_dir = os.path.dirname(app_path)

# translation location: '../share/locale/<LANG>/LC_MESSAGES/diffuse.mo'
# where '<LANG>' is the language key
lang = locale.getdefaultlocale()[0]
if isWindows():
    # gettext looks for the language using environment variables which
    # are normally not set on Windows so we try setting it for them
    for v in 'LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG':
        if v in os.environ:
            lang = os.environ[v]
            # remove any additional languages, encodings, or modifications
            for v in ':.@':
                lang = lang.split(v)[0]
            break
    else:
        if lang is not None:
            os.environ['LANG'] = lang
    del v
    locale_dir = 'locale'
else:
    locale_dir = '../share/locale'
locale_dir = os.path.join(bin_dir, locale_dir)
gettext.bindtextdomain('diffuse', locale_dir)

gettext.textdomain('diffuse')
_ = gettext.gettext

APP_NAME = 'Diffuse'
VERSION = '0.5.0'
COPYRIGHT = _('''Copyright © 2006-2019 Derrick Moser
Copyright © 2015-2020 Romain Failliot''')
WEBSITE = 'https://github.com/MightyCreak/diffuse'
