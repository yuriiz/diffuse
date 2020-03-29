#!/usr/bin/env python3

import encodings
import os
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from diffuse import diffuse
from diffuse.utils import isWindows, logError, make_subdirs, _
from diffuse.utils import APP_NAME, VERSION, COPYRIGHT, bin_dir

if __name__ == '__main__':
    args = sys.argv
    argc = len(args)

    if argc == 2 and args[1] in [ '-v', '--version' ]:
        print('%s %s\n%s' % (APP_NAME, VERSION, COPYRIGHT))
        sys.exit(0)
    if argc == 2 and args[1] in [ '-h', '-?', '--help' ]:
        print(_('''Usage:
    diffuse [ [OPTION...] [FILE...] ]...
    diffuse ( -h | -? | --help | -v | --version )

Diffuse is a graphical tool for merging and comparing text files.  Diffuse is
able to compare an arbitrary number of files side-by-side and gives users the
ability to manually adjust line matching and directly edit files.  Diffuse can
also retrieve revisions of files from Bazaar, CVS, Darcs, Git, Mercurial,
Monotone, RCS, Subversion, and SVK repositories for comparison and merging.

Help Options:
  ( -h | -? | --help )             Display this usage information
  ( -v | --version )               Display version and copyright information

Configuration Options:
  --no-rcfile                      Do not read any resource files
  --rcfile <file>                  Specify explicit resource file

General Options:
  ( -c | --commit ) <rev>          File revisions <rev-1> and <rev>
  ( -D | --close-if-same )         Close all tabs with no differences
  ( -e | --encoding ) <codec>      Use <codec> to read and write files
  ( -L | --label ) <label>         Display <label> instead of the file name
  ( -m | --modified )              Create a new tab for each modified file
  ( -r | --revision ) <rev>        File revision <rev>
  ( -s | --separate )              Create a new tab for each file
  ( -t | --tab )                   Start a new tab
  ( -V | --vcs ) <vcs-list>        Version control system search order
  --line <line>                    Start with line <line> selected
  --null-file                      Create a blank file comparison pane

Display Options:
  ( -b | --ignore-space-change )   Ignore changes to white space
  ( -B | --ignore-blank-lines )    Ignore changes in blank lines
  ( -E | --ignore-end-of-line )    Ignore end of line differences
  ( -i | --ignore-case )           Ignore case differences
  ( -w | --ignore-all-space )      Ignore white space differences'''))
        sys.exit(0)

    # this is not automatically set on some older version of PyGTK
    Gtk.Window.set_default_icon_name('diffuse')

    # find the config directory and create it if it didn't exist
    rc_dir, subdirs = os.environ.get('XDG_CONFIG_HOME', None), [u'diffuse']
    if rc_dir is None:
        rc_dir = os.path.expanduser(u'~')
        subdirs.insert(0, u'.config')
    rc_dir = make_subdirs(rc_dir, subdirs)
    # find the local data directory and create it if it didn't exist
    data_dir, subdirs = os.environ.get('XDG_DATA_HOME', None), [u'diffuse']
    if data_dir is None:
        data_dir = os.path.expanduser(u'~')
        subdirs[:0] = [ u'.local', u'share' ]
    data_dir = make_subdirs(data_dir, subdirs)
    # load resource files
    i, rc_files = 1, []
    if i < argc  and args[i] == '--no-rcfile':
        i += 1
    elif i + 1 < argc and args[i] == '--rcfile':
        i += 1
        rc_files.append(args[i])
        i += 1
    else:
        # parse system wide then personal initialisation files
        if isWindows():
            rc_file = os.path.join(bin_dir, u'diffuserc')
        else:
            rc_file = os.path.join(bin_dir, u'../../etc/diffuserc')
        for rc_file in rc_file, os.path.join(rc_dir, u'diffuserc'):
            if os.path.isfile(rc_file):
                rc_files.append(rc_file)
    for rc_file in rc_files:
        # convert to absolute path so the location of any processing errors are
        # reported with normalised file names
        rc_file = os.path.abspath(rc_file)
        try:
            diffuse.theResources.parse(rc_file)
        except IOError:
            logError(_('Error reading %s.') % (rc_file, ))

    diff = diffuse.Diffuse(rc_dir)

    # load state
    statepath = os.path.join(data_dir, 'state')
    diff.loadState(statepath)

    # process remaining command line arguments
    encoding, revs, close_on_same = None, [], False
    specs, had_specs, labels = [], False, []
    funcs = { 'modified': diff.createModifiedFileTabs,
              'commit': diff.createCommitFileTabs,
              'separate': diff.createSeparateTabs,
              'single': diff.createSingleTab }
    mode, options = 'single', {}
    while i < argc:
        arg = args[i]
        if len(arg) > 0 and arg[0] == '-':
            if i + 1 < argc and arg in [ '-c', '--commit' ]:
                # specified revision
                funcs[mode](specs, labels, options)
                i += 1
                rev = args[i]
                specs, labels, options = [], [], { 'commit': args[i] }
                mode = 'commit'
            elif arg in [ '-D', '--close-if-same' ]:
                close_on_same = True
            elif i + 1 < argc and arg in [ '-e', '--encoding' ]:
                i += 1
                encoding = args[i]
                encoding = encodings.aliases.aliases.get(encoding, encoding)
            elif arg in [ '-m', '--modified' ]:
                funcs[mode](specs, labels, options)
                specs, labels, options = [], [], {}
                mode = 'modified'
            elif i + 1 < argc and arg in [ '-r', '--revision' ]:
                # specified revision
                i += 1
                revs.append((args[i], encoding))
            elif arg in [ '-s', '--separate' ]:
                funcs[mode](specs, labels, options)
                specs, labels, options = [], [], {}
                # open items in separate tabs
                mode = 'separate'
            elif arg in [ '-t', '--tab' ]:
                funcs[mode](specs, labels, options)
                specs, labels, options = [], [], {}
                # start a new tab
                mode = 'single'
            elif i + 1 < argc and arg in [ '-V', '--vcs' ]:
                i += 1
                diff.prefs.setString('vcs_search_order', args[i])
                diff.preferences_updated()
            elif arg in [ '-b', '--ignore-space-change' ]:
                diff.prefs.setBool('display_ignore_whitespace_changes', True)
                diff.prefs.setBool('align_ignore_whitespace_changes', True)
                diff.preferences_updated()
            elif arg in [ '-B', '--ignore-blank-lines' ]:
                diff.prefs.setBool('display_ignore_blanklines', True)
                diff.prefs.setBool('align_ignore_blanklines', True)
                diff.preferences_updated()
            elif arg in [ '-E', '--ignore-end-of-line' ]:
                diff.prefs.setBool('display_ignore_endofline', True)
                diff.prefs.setBool('align_ignore_endofline', True)
                diff.preferences_updated()
            elif arg in [ '-i', '--ignore-case' ]:
                diff.prefs.setBool('display_ignore_case', True)
                diff.prefs.setBool('align_ignore_case', True)
                diff.preferences_updated()
            elif arg in [ '-w', '--ignore-all-space' ]:
                diff.prefs.setBool('display_ignore_whitespace', True)
                diff.prefs.setBool('align_ignore_whitespace', True)
                diff.preferences_updated()
            elif i + 1 < argc and arg == '-L':
                i += 1
                labels.append(args[i])
            elif i + 1 < argc and arg == '--line':
                i += 1
                try:
                    options['line'] = int(args[i])
                except ValueError:
                    logError(_('Error parsing line number.'))
            elif arg == '--null-file':
                # add a blank file pane
                if mode == 'single' or mode == 'separate':
                    if len(revs) == 0:
                        revs.append((None, encoding))
                    specs.append((None, revs))
                    revs = []
                had_specs = True
            else:
                logError(_('Skipping unknown argument "%s".') % (args[i], ))
        else:
            filename = diff.prefs.convertToNativePath(args[i])
            if (mode == 'single' or mode == 'separate') and os.path.isdir(filename):
                if len(specs) > 0:
                    filename = os.path.join(filename, os.path.basename(specs[-1][0]))
                else:
                    logError(_('Error processing argument "%s".  Directory not expected.') % (args[i], ))
                    filename = None
            if filename is not None:
                if len(revs) == 0:
                    revs.append((None, encoding))
                specs.append((filename, revs))
                revs = []
            had_specs = True
        i += 1
    if mode in [ 'modified', 'commit' ] and len(specs) == 0:
        specs.append((os.curdir, [ (None, encoding) ]))
        had_specs = True
    funcs[mode](specs, labels, options)

    # create a file diff viewer if the command line arguments haven't
    # implicitly created any
    if not had_specs:
        diff.newLoadedFileDiffViewer([])
    elif close_on_same:
        diff.closeOnSame()
    nb = diff.notebook
    n = nb.get_n_pages()
    if n > 0:
        nb.set_show_tabs(diff.prefs.getBool('tabs_always_show') or n > 1)
        nb.get_nth_page(0).grab_focus()
        diff.show()
        Gtk.main()
        # save state
        diff.saveState(statepath)
