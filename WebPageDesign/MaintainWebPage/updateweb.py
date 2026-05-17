#!/usr/bin/env python3
# ============================================================================
#
# NAME
#
#     updateweb.py
#
# DESCRIPTION
#
#     Python script which updates my web sites.
#
#     It does miscellaneous cleanup on my local copy of the web site on disk,
#     including updating copyright information, then synchronizes the local
#     copy to my remote server web sites using FTP.
#
# USAGE
#
#     It's best to use the associated makefile.
#     But you can call this Python utility from the command line,
#
#     $ python updateweb.py          Clean up my local copy, then use it
#                                    to update my remote web server site.
#                                    Log warnings and errors.
#     $ python updateweb.py -v       Same, but log debug messages also.
#     $ python updateweb.py -c       Clean up my local copy only.
#     $ python updateweb.py -t       Run unit tests only.
#     $ python updateweb.py -m       Upload MathJax files (only need to do this once).
#
#     We get username and password information from the file PARAMETERS_FILE.
#
#     Logs are written to the files,
#
#         logLocal.txt       Local web site cleanup log.
#         logRemote.txt      Remote web server update log.
#
# AUTHOR
#
#     Sean E. O'Connor        23 Aug 2007  Version 1.0 released.
#
# LEGAL
#
#     updateweb.py Version 7.4 - A Python utility program which maintains my web site.
#     Copyright (C) 2007-2026 by Sean Erik O'Connor.  All Rights Reserved.
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#     The author's address is seanerikoconnor!AT!gmail!DOT!com
#     with !DOT! replaced by . and the !AT! replaced by @
#
# NOTES
#
#    DOCUMENTATION
#
#    Python interpreter:               https://www.python.org/
#    Python tutorial and reference:    https://docs.python.org/lib/lib.html
#    Python debugger:                  https://docs.python.org/3/library/pdb.html
#    Python regular expression howto:  https://docs.python.org/3.7/howto/regex.html
#
# ============================================================================

# ----------------------------------------------------------------------------
#  Load Python Packages
# ----------------------------------------------------------------------------

# OS stuff
import sys
import os
import argparse
import subprocess
import shutil
from pathlib import Path

# Regular expressions
import re

# FTP stuff
import ftplib

# Date and time
import time
import stat
import datetime

# Logging
import logging

# Unit testing
import unittest

# Enumerated types (v3.4)
from enum import Enum
from typing import List, Any

# YAML configuration files (a superset of JSON!)
import yaml 
# Recommended by https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

# Python syntax highlighter.  See https://pygments.org
from pygments import highlight
from pygments.lexers import HtmlLexer, CssLexer, JavascriptLexer, YamlLexer, MakefileLexer, BashLexer, VimLexer, TexLexer
from pygments.lexers import PythonLexer, CppLexer, CLexer, CommonLispLexer, FortranFixedLexer, MatlabLexer, OutputLexer
from pygments.formatters import HtmlFormatter


# ----------------------------------------------------------------------------
#  Custom Top Level Exceptions.
# ----------------------------------------------------------------------------

class UpdateWebException(Exception):
    """Something went wrong at a deep level when searching local files, searching remote files, or trying to sync local and remote, and we could not recover.
       Derive from Exception as recommended by Python manual"""
    pass

# ----------------------------------------------------------------------------
#  User settings.
# ----------------------------------------------------------------------------

class TreeWalkSettings(Enum):
    """Enum types for how to walk the directory tree."""
    BREADTH_FIRST_SEARCH = 1
    DEPTH_FIRST_SEARCH = 2

class FileType(Enum):
    """'Enum' types for properties of directories and files."""
    DIRECTORY = 0
    FILE = 1
    ON_LOCAL_ONLY = 2
    ON_REMOTE_ONLY = 3
    ON_BOTH_LOCAL_AND_REMOTE = 4

class UserSettings:
    """Megatons of user selectable settings."""
    # Logging control.
    LOGFILENAME = ""
    VERBOSE = False  # Verbose mode.  Prints out everything.
    CLEAN = False  # Clean the local website only.
    UNITTEST = False  # Run a unit test of a function.
    MATHJAX = False  # Process and upload MathJax files to server.

    # When diving into the MathJax directory, web walking the deep directories
    # may exceed Python's default recursion limit of 1000.
    RECURSION_DEPTH = 5000
    sys.setrecursionlimit(RECURSION_DEPTH)

    # Fields in the file information (file_info) structure.
    # For example, file_info = 
    #   [ '/WebDesign/EquationImages/equation001.png',  -- The file name.
    #      1,                                           -- Enum type: Is it a file? dir? on local? on remote? on both?
    #      datetime.datetime(2010, 2, 3, 17, 15),       -- UTC encoded in a datetime class.
    #      4675]                                        -- File size in bytes.
    FILE_NAME = 0
    FILE_TYPE = 1
    FILE_DATE_TIME = 2
    FILE_SIZE = 3

    # Server settings.
    SERVER_SETTINGS_FILE_NAME = "/private/updateweb.yaml"
    SERVER_NAME = None
    USER_NAME = None
    PASSWORD_NAME = None
    FTP_ROOT_NAME = None
    FILE_SIZE_LIMIT_NAME = None

    # Map month names onto numbers.
    monthToNumber = {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12}

    # List of directories to skip over when processing or uploading the web page.
    # Some are private but most are dir of temporary files.
    # They will be listed as WARNING in the log.
    # Examples:
    #     My private admin settings directory.
    #     Git or SVN local admin directories.
    #     Compile build directories fromXCode.
    #     PyCharm build directories.
    #     Python cache directories.
    #     Jupyter checkpoint directories.
    #     XCode temporary file crap.
    DIR_TO_SKIP = "private|.git|.github|.svn|build|XCodeOutput|Debug|Release|PyCharm|.idea|__pycache__|.ipynb_checkpoints|ModuleCache.noindex|SymbolCache.noindex|Primpoly-[a-z]"

    # List of files to skip when processing or uploading to the web page.
    # They will be listed as WARNING in the log.
    # Examples:
    #     MathJax yml file.
    #     .htaccess (because it doesn't show up on the output of ftp LIST, so we must upload manually)
    FILE_TO_SKIP = ".travis.yml|.svnignore|.htaccess"

    # Suffixes for temporary files which will be deleted during the cleanup
    # phase.
    TEMP_FILE_SUFFIXES = r"""        # Use Python raw strings.
        \.                           # Match the dot in the file name.
                                     # Now begin matching the file name suffix.
                                     # (?: non-capturing match for the regex inside the parentheses,
                                     #   i.e. matching string cannot be retrieved later.
                                     # Now match any of the following file extensions:
        (?: o   | obj | lib |        #     Object files generated by C, C++, etc compilers
                              pyc |  #     Object file generated by the Python compiler
                  ilk | pdb | sup |  #     Temp files from VC++ compiler
            idb | ncb | opt | plg |  #     Temp files from VC++ compiler
            sbr | bsc | map | bce |  #     Temp files from VC++ compiler
            res | aps | dep | db  |  #     Temp files from VC++ compiler
                              jbf |  #     Paintshop Pro
                      class | jar |  #     Java compiler
                              fas |  #     CLISP compiler
                        swp | swo |  #     Vim editor
                        toc | aux |  #     TeX auxilliary files (not .synctex.gz or .log)
          DS_Store  | _\.DS_Store |  #     macOS finder folder settings.
                       _\.Trashes |  #     macOS recycle bin
        gdb_history)                 #     GDB history
        $                            #     Now we should see only the end of line.
        """

    # Special case:  Vim temporary files contain a twiddle anywhere in the
    # name.
    VIM_TEMP_FILE_EXT = "~"

    # Suffixes for temporary directories which should be deleted during the
    # cleanup phase.
    TEMP_DIR_SUFFIX = r"""           # Use Python raw strings.
        (?: Debug | Release |        # C++ compiler
           ipch   | \.vs    |        # Temp directories from VC++ compiler
        \.Trashes | \.Trash)         # macOS recycle bin
        $
        """

    # File extension for an internally created temporary file.
    TEMP_FILE_EXT = ".new"

    # Identify source file types.
    HYPERTEXT_FILE_PATTERN = r"""  # Use Python raw strings.
        (\.                        # Match the filename suffix after the .
            (?: html | htm |       # HTML hypertext
                css)               # CSS style sheet
        $)                         # End of line.
    """

    SOURCE_FILE_PATTERN = r"""      # Use Python raw strings.
        (?: makefile$ |             # Any file called makefile is a source file.
                                    # Note the $ at the end so we don't reprocess .gitconfig.html -> .gitconfig.html.html
          .vimrc$ |                 # Vim script
          (.bashrc$ |               # Bash configuration files.
           .bash_profile$ |
           .bash_logout$) 
          |
          (.gitignore$ |             # Git configuration files.
           .gitignore_global$ | 
           .gitconfig$)
          |
          (\.                       # Match the filename suffix after the .
                                    # Now match any of these suffixes:
             (?: 
                  c | cpp | h | hpp |   #     C++ and C
                  js |                  #     JavaScript
                  py |                  #     Python
                  lsp |                 #     LISP
                  ipynb |               #     Jupyter notebook
                  m  |                  #     MATLAB
                  FOR | for | f |       #     FORTRAN
                  yaml |                #     YAML = JSON superset
                  tex |                 #     LaTeX
                  txt | dat |           #     Data files
                  sh)                   #     Bash
             $)                         # End of line.
         )
         """

    # Special case of certain HTML and CSS files for which we want to generate a syntax highlighted source code listing.
    SPECIAL_FILE_TO_HIGHLIGHT_PATTERN = r"""
        (?: ^life\.html$          | # We want a listing of this particular HTML file.
            ^index\.html$         | # I want to list my top level HTML file.  (There is only one file with this name at the top level web directory.)
            ^webPageDesign\.html$ | # and also this HTML example file, but no others.
            ^StyleSheet\.css$ )     # I want to list my style sheet.
        """

    # Files for which we want to generate a syntax highlighted source code listing.
    # Uses an f-string combined with a raw-string.
    FILE_TO_HIGHLIGHT_PATTERN = fr"""
        (?: {SPECIAL_FILE_TO_HIGHLIGHT_PATTERN} | 
            {SOURCE_FILE_PATTERN} )
        """

    # Update my email address.
    # This is tricky:  Prevent matching and updating the name within in this
    # Python source file by using the character class brackets.
    OLD_EMAIL_ADDRESS = r"""
        artificer\!AT\!sean[e]rikoconnor\!DOT\!freeservers\!DOT\!com
        """
    NEW_EMAIL_ADDRESS = "seanerikoconnor!AT!gmail!DOT!com"

    # List of patterns to match, match groups to pull out of the old string, new strings to generate from these two items.  
    # Read patterns and strings from the updateweb.yaml file.
    STRING_REPLACEMENT_LIST = []
    # Pairs of test strings and their correct match/replacements.
    STRING_REPLACEMENT_TEST_VERIFY_STRING_LIST = []

    # Match a copyright line like this:
    #     Copyright (C) 1999-2026 by Sean Erik O&#39;Connor.  All Rights Reserved.
    # Extract the copyright symbol which can be ascii (C) or HTML &copy; and extract the old year.
    TWO_DIGIT_YEAR_FORMAT = "%02d"
    COPYRIGHT_LINE = r"""
        Copyright                       # Copyright.
        \s+                             # One or more spaces.
        (?P<symbol> \(C\) | &copy;)     # Match and extract the copyright symbol.
        \D+                             # Any non-digits.
        (?P<old_year>[0-9]+)            # Match and extract the old copyright year, place it into variable 'old_year'
        -                               # hyphen
        ([0-9]+)                        # New copyright year.
        \s+                             # One or more spaces.
        by\s+Sean\sErik                 # Start of my name.  This way we don't rewrite somebody else's copyright notice.
        """

    # Match a line containing the words,
    #    last updated YY
    # and extract the two digit year YY.
    LAST_UPDATED_LINE = r"""
        last\s+         # Match the words "last updated"
        updated\s+
        \d+             # Day number
        \s+             # One or more blanks or tab(
        [A-Za-z]+       # Month
        \s+             # One or more blanks or tabs
        (?P<year>\d+)   # Two digit year.  Place it into the variable 'year'
        """

    # Web server root directory.
    DEFAULT_ROOT_DIR = "/"

    # The ftp listing occasionally shows a date newer than the actual date. 
    # On my server, it could be 6 months newer when we are near New Year's Day.  Typically the server file time is only a 1 or 2 minutes newer.
    # But if the remote file time is much newer, it might be an old file with a bad date/time.  
    # Upload the file to be safe.
    # How to see the time differences from the log if they are large:
    #     egrep -o "Remote file.*is MUCH newer.*days" logRemote.txt
    #     Remote file Finance/MortgageLoanDerivation.tex.html is MUCH newer[8.0 minutes] by 885753.0 seconds = 14762.5 minutes = 246.0 hours = 10.3 days
    # How to see the time differences from the log if they are small and we wait and NOT upload:
    #    egrep -o "Remote file.*is newer.*days" logRemote.txt
    #    Remote file error404.html is newer by    102.0 seconds =      1.7 minutes =      0.0 hours =      0.0 days
    #    Remote file index.html is newer by    113.0 seconds =      1.9 minutes =      0.0 hours =      0.0 days
    MINUTES_NEWER_FOR_REMOTE_BEFORE_UPLOAD = 8.0

    # Upload only if we are newer by more than a few minutes.  Allows for a little slop in time stamps on server or host.
    MINUTES_NEWER_FOR_LOCAL_BEFORE_UPLOAD = 3.0

    # An ftp list command line should be at least this many chars, or we'll
    # suspect and error.
    MIN_FTP_LINE_LENGTH = 7

    # Parse an ftp listing, extracting <bytes> <mon> <day> <hour> <min> <year> <filename>
    # ftp listings are generally similar to UNIX ls -l listings.
    #
    # Some examples:
    #
    # (1) Freeservers ftp listing,
    #
    #          0        1   2                3           4    5   6   7      8
    #     drwxr-xr-x    3 1000             1000         4096 Nov 18  2006 Electronics
    #     -rw-r--r--    1 1000             1000        21984 Jun  4 03:46 StyleSheet.css
    #     -rw-r--r--    1 1000             1000         2901 Sep 26 17:12 allclasses-frame.html
    #
    # (2) atspace ftp listing,
    #
    #     drwxr-xr-x    3  seanerikoconnor vusers         49 Apr  7  2006 Electronics
    #     -rw-r--r--    1  seanerikoconnor vusers      21984 Jun  4 04:03 StyleSheet.css
    #
    FTP_LISTING = r"""
        [drwx-]+            # Unix type file mode.
        \s+                 # One or more blanks or tabs.
        \d+                 # Number of links.
        \s+
        \w+                 # Owner.
        \s+
        \w+                 # Group.
        \s+
        (?P<bytes> \d+)     # File size in bytes, placed into the variable 'bytes'.
        \s+
        (?P<mon> \w+)       # Month modified, placed into the variable 'mon'.
        \s+
        (?P<day> \d+)       # Day modified, placed into the variable 'day'.
        \s+
        (
            (?P<hour> \d+)  # Hour modified, placed into the variable 'hour'.
            :
            (?P<min> \d+)   # Minute modified, placed into the variable 'min'.
            |
            (?P<year> \d+)  # If hours and minutes are absent (happens when year is not the current year),
                            # extract the year instead.
        )
        \s+
        (?P<filename> [A-Za-z0-9"'.\-_,~()=+#]+)    # Path and file name containing letters, numbers,
                                                    # and funny characters.  We must escape some of
                                                    # these characters with a backslash, \.
        """

    # HTML header up to the style sheet.
    BASIC_HTML_BEGIN = \
        """
        <!DOCTYPE html>
        <html lang="en-US">  <!-- Set language of this page to USA English. -->
        
        <head>
            <!-- This page uses Unicode characters. -->
            <meta charset="utf-8">
        
            <!-- Set viewport to actual device width.  Any other settings makes the web page initially appear zoomed-in on mobile devices. -->
            <meta name="viewport" content="width=device-width, initial-scale=1">
        
            <!-- Title appears in the web browser tab for this page.  The browser also uses it to bookmark this page. -->
            <title>Sean Erik O'Connor - Home Page and Free Mathematical Software.</title>
        
            <!-- Search engines will search using words in this description.  They will also display title in their search results. -->
            <meta name="description" content="Syntax Colored Source Code Listing">
        
            <!-- Some content management software uses the author's name. -->
            <meta name="author" content="Sean Erik O'Connor">
        
            <meta name="copyright" content="Copyright (C) 1986-2026 by Sean Erik O'Connor.  All Rights Reserved.">   
        
            <!-- Begin style sheet insertion -->
            <style>
                /* Default settings for all my main web pages. */
                body
                {
                    /* A wide sans-serif font is more readable on the web. */
                    font-family:            Verdana, Geneva, "Trebuchet MS", sans-serif ;
        
                    /* Set the body font size a little smaller than the user's default browser setting. */
                    font-size:              0.8em ; 
        
                    /* Black text is easier to read. */
                    color:                  black ;
        
                    /*  More vertical space between lines for more pleasant reading.  Use a unitless font height multiplier.  
                        Length and percentage percentage values can give scrunched text due to poor inheritance behavior. */
                    line-height:            1.7 ;
                }
        
                <!-- Now prepare to add the syntax coloring style sheet from Pygment -->
        """

    # After the style sheet and up to the start of the article in the body.
    BASIC_HTML_MIDDLE = \
        """
            </style>
        </head>
        
        <body>
            <article class="content">
        """

    # After the source code listing, finish the article, body and html document.
    BASIC_HTML_END = \
        """
            </article>
        </body>
        
        </html>
        """

    def __init__(self):
        """Set up the user settings."""

        self.local_root_dir = ""

        # Import the user settings from the parameter file.
        self.get_local_root_dir()
        self.get_server_settings()

        self.precompile_regular_expressions()

    def get_server_settings(self):
        """
        Read web account private settings from a secret offline parameter file.
        These also hold patterns to match and replace in all of our source pages.
        """

        # Private file which contains my account settings.
        settings_file_name = self.local_root_dir + self.SERVER_SETTINGS_FILE_NAME
        # Recommended by
        #  https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started
        try:
            stream = open(settings_file_name, "r")
        except OSError as detail:
            logging.error(f"Cannot open the YAML file {settings_file_name:s}.  Unable to read the settings because: {str(detail):s}")
            # Rethrow the exception higher.
            raise UpdateWebException("Cannot load the settings.  See the log file for details.  Aborting... ") from detail
        # Read all the YAML documents in the file.
        yaml_contents = yaml.load_all(stream, Loader)
        yaml_document_list: list[Any] = []
        for yaml_doc in yaml_contents:
            yaml_document_list.append(yaml_doc)
        num_yaml_docs = len(yaml_document_list)
        if num_yaml_docs != 2:
            logging.error(f"Wrong number of YAML documents = {num_yaml_docs:3d} in the user settings file.  Aborting...")
            raise UpdateWebException("Cannot load the settings.  See the log file for details.  Aborting... ")

        # Load all the server settings.
        self.SERVER_NAME = yaml_document_list[0]['ftp_server_name']
        self.USER_NAME = yaml_document_list[0]['ftp_user_name']
        self.PASSWORD_NAME = yaml_document_list[0]['ftp_password']
        self.FTP_ROOT_NAME = yaml_document_list[0]['remote_directory']
        self.FILE_SIZE_LIMIT_NAME = int(yaml_document_list[0]['file_size_limit_Kb'])

        # Load all the tuples which contain patterns to match and the strings to replace, from document #1 in the YAML file.
        self.STRING_REPLACEMENT_LIST = []
        pat_rep_yaml_list = yaml_document_list[1]['pattern_match_replacement_string_list']
        for pat_rep in pat_rep_yaml_list:
            # Fetch the regular expression and compile it for speed.
            verbose_regex = pat_rep['pattern']
            pat = re.compile(verbose_regex, re.VERBOSE | re.IGNORECASE)
            # Since we use raw strings, we need to strip off leading and trailing whitespace.
            replacement_string = pat_rep['replacement_string'].strip().lstrip()
            self.STRING_REPLACEMENT_LIST.append([pat, replacement_string])

        # Load the test and verify strings.
        test_verify_strings_list = yaml_document_list[1]['test_verify_string_list']
        for test_verify_string in test_verify_strings_list:
            test_string = test_verify_string['test_string'].strip().lstrip()
            verify_string = test_verify_string['verify_string'].strip().lstrip()
            self.STRING_REPLACEMENT_TEST_VERIFY_STRING_LIST.append([test_string,verify_string])

        print("  ...done!", flush=True)
        return

    def get_local_root_dir(self):
        """Get the local website root directory on this platform."""

        # Each platform has a definite directory for the web page.
        local_web_dir_path = "/Desktop/Sean/WebSite"

        if sys.platform.startswith('darwin'):
            self.local_root_dir = str(Path.home()) + local_web_dir_path
        # My Cyperpower PC running Ubuntu Linux.
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            self.local_root_dir = str(Path.home()) + local_web_dir_path
        return

    def precompile_regular_expressions(self):
        """For speed precompile the regular expression search patterns."""
        self.COPYRIGHT_LINE            = re.compile(self.COPYRIGHT_LINE,            re.VERBOSE | re.IGNORECASE)
        self.FTP_LISTING               = re.compile(self.FTP_LISTING,               re.VERBOSE | re.IGNORECASE)
        self.TEMP_FILE_SUFFIXES        = re.compile(self.TEMP_FILE_SUFFIXES,        re.VERBOSE | re.IGNORECASE)
        self.TEMP_DIR_SUFFIX           = re.compile(self.TEMP_DIR_SUFFIX,           re.VERBOSE)
        self.SOURCE_FILE_PATTERN       = re.compile(self.SOURCE_FILE_PATTERN,       re.VERBOSE)
        self.HYPERTEXT_FILE_PATTERN    = re.compile(self.HYPERTEXT_FILE_PATTERN,    re.VERBOSE)
        self.OLD_EMAIL_ADDRESS         = re.compile(self.OLD_EMAIL_ADDRESS,         re.VERBOSE | re.IGNORECASE)
        self.FILE_TO_HIGHLIGHT_PATTERN = re.compile(self.FILE_TO_HIGHLIGHT_PATTERN, re.VERBOSE)
        self.LAST_UPDATED_LINE         = re.compile(self.LAST_UPDATED_LINE,         re.VERBOSE | re.IGNORECASE)

# ----------------------------------------------------------------------------
#  Unit test individual functions.
# ----------------------------------------------------------------------------

class UnitTest(unittest.TestCase):
    """Initialize the UnitTest class."""
    def setUp(self):
        self.user_settings = UserSettings()
        self.user_settings.get_local_root_dir()

    def tearDown(self):
        """Clean up the UnitTest class."""
        self.user_settings = None

    def test_copyright_updating(self):
        """Test copyright line updating to the current year."""
        # Prevent web cleaning from rewriting strings by splitting them up and concatenating them.
        line_before_update = "Copyright (C) 19" + "99-20" + "20" + " by Sean Erik O'Connor.  All Rights Reserved. Copyright &copy; 1999-2026 by Sean Erik O'Connor"
        line_after_update_actual = "Copyright (C) 1999-2026 by Sean Erik O'Connor.  All Rights Reserved. Copyright &copy; 1999-2026 by Sean Erik O'Connor"
        pat = self.user_settings.COPYRIGHT_LINE
        match = pat.search(line_before_update)

        if match:
            old_year = int(match.group('old_year'))
            # Same as call to self.get_current_year():
            current_year = int(time.gmtime()[0])
            if old_year < current_year:
                # We matched and extracted the old copyright symbol into the variable
                # 'symbol' using the pattern syntax (?P<symbol> \(C\) | &copy;)
                # We now insert it back by placing the special syntax
                # \g<symbol> into the replacement string.
                new_copyright = r"Copyright \g<symbol> \g<old_year>-" + str(current_year) + " by Sean Erik"
                line_after_update_computed = pat.sub(new_copyright, line_before_update)
                self.assertEqual(
                    line_after_update_actual,
                    line_after_update_computed,
                    f"newline = |{line_after_update_actual:s}| line_after_update_computed = |{line_after_update_computed:s}|")
            else:
                print( "old_year >= current_year" )
                self.fail()
        else:
            print( "no match for copyright pattern" )
            self.fail()

    def test_extract_filename_from_ftp_listing(self):
        """Test parsing an FTP listing."""
        ftp_line = "-rw-r--r--    1 1000             1000         2901 Sep 26 17:12 allclasses-frame.html"
        extracted_file_name = "allclasses-frame.html"
        pat = self.user_settings.FTP_LISTING
        match = pat.search(ftp_line)
        if match:
            filename = match.group('filename')
            self.assertEqual(
                filename,
                extracted_file_name,
                f"ftp_line = {ftp_line:s} extracted file name = {extracted_file_name:s}")
        else:
            self.fail()

    def test_get_file_time_and_date(self):
        """Test getting a file time and date."""
        # Point to an old file.
        file_name = "./Images/home.png"
        full_file_name = self.user_settings.local_root_dir + '/' + file_name
        # Get the UTC time.
        file_epoch_time = os.path.getmtime(full_file_name)
        file_time_utc = time.gmtime(file_epoch_time)[0: 6]
        # Create a datetime object for the file.
        d = datetime.datetime(file_time_utc[0], file_time_utc[1], file_time_utc[2], file_time_utc[3], file_time_utc[4], file_time_utc[5])  # datetime class;  year, month, day, hour, minute, seconds.
        # Check if the file time matches what we would see if we did ls -l <file_name> and then converted to UTC.
        computed = f"file {file_name:s} datetime {d.ctime():s}"
        actual = "file ./Images/home.png datetime Tue Jul  1 03:53:16 2025"
        self.assertEqual(computed, actual)

    def test_set_file_time_and_date(self):
        """Test setting a file time and date."""
        file_name = "./Images/home.png"
        full_file_name = self.user_settings.local_root_dir + '/' + file_name
        # Create a temporary file in the same directory.
        temp_file_name = "temporal.tmp"
        full_temp_file_name = self.user_settings.local_root_dir + temp_file_name
        try:
            with open(full_temp_file_name, 'w') as fp:
                fp.write("The End of Eternity")
        except OSError as detail:
            logging.error(f"Cannot open or write to the file {full_temp_file_name:s}: {str(detail):s}  Aborting...")
            raise UpdateWebException("Failed the unit test for setting time and date of a file.  See the log file for details.  Aborting...") from detail
        # Get the old file time.  Set the temporary file to the same time.
        file_stat = os.stat(full_file_name)
        os.utime(full_temp_file_name, (file_stat[stat.ST_ATIME], file_stat[stat.ST_MTIME]))
        # What is the temporary file's time now?
        file_epoch_time = os.path.getmtime(full_temp_file_name)
        file_time_utc = time.gmtime(file_epoch_time)[0: 6]
        d = datetime.datetime(file_time_utc[0], file_time_utc[1], file_time_utc[2], file_time_utc[3], file_time_utc[4], file_time_utc[5])  # datetime class;  year, month, day, hour, minute, seconds.
        # Is the temporary file time set properly?
        computed = f"file {file_name:s} datetime {d.ctime():s}"
        actual = "file ./Images/home.png datetime Tue Jul  1 03:53:16 2025"
        self.assertEqual(computed, actual)
        os.remove(full_temp_file_name)

    def test_difference_of_time_and_date(self):
        """Test a date difference calculation."""
        file_name = "./Images/home.png"
        full_file_name = self.user_settings.local_root_dir + '/' + file_name
        # Get the UTC time.
        file_epoch_time = os.path.getmtime(full_file_name)
        file_time_utc = time.gmtime(file_epoch_time)[0: 6]
        # Create a datetime object for the file.
        d = datetime.datetime(file_time_utc[0], file_time_utc[1], file_time_utc[2], file_time_utc[3], file_time_utc[4], file_time_utc[5])  # datetime class;  year, month, day, hour, minute, seconds.
        # Slightly change the date and time by adding 1 minute.
        d2 = datetime.datetime(file_time_utc[0], file_time_utc[1], file_time_utc[2], file_time_utc[3], file_time_utc[4], file_time_utc[5]+1)  # year, month, day, hour, minute, second
        time_delta = d2 - d
        seconds_different = time_delta.total_seconds()
        minutes_different = seconds_different / 60.0
        hours_different = minutes_different / 60.0
        days_different = hours_different / 24.0
        computed = f"difference {days_different:8.5f} days, {hours_different:8.5f} hours {minutes_different:8.5f} minutes, {seconds_different:8.5f} seconds"
        actual = "difference  0.00001 days,  0.00028 hours  0.01667 minutes,  1.00000 seconds"
        self.assertEqual(computed, actual)

    def test_pattern_match_dir_to_skip(self):
        """Test if skipping certain named directories is recoginizing the dir names."""
        dir_skip = "Primpoly-cswhfrwgwdikgzfdpiorbeaiennz"
        pat = re.compile(self.user_settings.DIR_TO_SKIP)
        if pat.search(dir_skip):
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_file_name_to_syntax_highlight(self):
        """Test if syntax highlighting recognizes file names to highlight."""
        file_name1 = "Computer/hello.lsp"
        file_name2 = "Computer/life.html"
        p = self.user_settings.FILE_TO_HIGHLIGHT_PATTERN
        if p.search(Path(file_name1).name) and p.search(Path(file_name2).name):
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_user_settings(self):
        """Test whether user settings are correctly initialized."""
        computed = f"File size limit = {int(self.user_settings.FILE_SIZE_LIMIT_NAME):d} K"
        actual = "File size limit = 50000 K"
        self.assertEqual(computed, actual, "File size limit settings are incorrect.")

    def test_check_replace_substring(self,debug=True):
        """Test the substring pattern match and replacement functions which use the list of match/replace pairs in the YAML file.
           For troubleshooting, turn on debug.
        """
        test_verify_pairs = self.user_settings.STRING_REPLACEMENT_TEST_VERIFY_STRING_LIST
        # Iterate over all test strings.
        for pair in test_verify_pairs:
            [test_string, verify_string] = pair
            if debug:
                print( f">>>>>>> next test string   = {test_string}")
                print( f">>>>>>> next verify string = {verify_string}")
            # Iterate over all patterns and replacements.
            for match_replace_tuple in self.user_settings.STRING_REPLACEMENT_LIST:
                [pat, rep_string] = match_replace_tuple
                print( f"\t-------> next pattern = {pat}") 
                print( f"\t-------> next replacement = {rep_string}") 
                match = pat.search(test_string)
                # The pattern match succeeds.
                if match:
                    try:
                        sub = pat.sub(rep_string, test_string)
                        # String replacement succeeds for this pattern/replace pair iteration.
                        if debug:
                            print( f"\t\t.......> match and replace: {test_string} ---> {sub}")
                        test_string = sub
                    except IndexError as detail:
                        print(f"\t\t.......> Caught an exception: {str(detail):s}.  Replacement failed.")
                        if debug:
                            self.assertTrue(False)
                elif debug:
                    print( f"\t\t.......> no match for pattern = {pat} in test string = {test_string}")
                # No match, so go on to the next pattern and don't change test_string.
            # Done with all pattern/replace on test string.
            # Check this test string in the list.
            self.assertEqual(test_string, verify_string, f"\ntest_string = |{test_string:s}|\nverify_string = |{verify_string:s}|\n")
            if debug:
                print( f"\t******* DONE with all pattern matches and replacements on this test/verify string pair.\n" )

# ----------------------------------------------------------------------------
#  Command line options.
# ----------------------------------------------------------------------------

class CommandLineSettings(object):
    """Get the command line options."""

    def __init__(self, user_settings, raw_args=None):
        """Get command line options"""
        command_line_parser = argparse.ArgumentParser(
            description="updateweb options")

        # Log all changes, not just warnings and errors.
        command_line_parser.add_argument(
            "-v",
            "--verbose",
            help="Turn on verbose mode to log everything",
            action="store_true")

        # Clean up the local website only.
        command_line_parser.add_argument(
            "-c",
            "--clean",
            help="Do a cleanup on the local web site only.",
            action="store_true")

        # Also upload MathJax.
        command_line_parser.add_argument(
            "-m",
            "--mathjax",
            help="""ALSO upload mathjax directory.\
            Do this if you have a new version of MathJax or if have not yet created the /mathjax remote directory on the server.\
            Recommend that you run the bash command:     find . -name '*' -exec touch {} \\;    This will ensure accurate times on the server.""",
            action="store_true")

        # Run unit tests only.
        command_line_parser.add_argument("-t", "--test",
                                         help="Run unit tests.",
                                         action="store_true")

        args = command_line_parser.parse_args(raw_args)

        if args.verbose:
            user_settings.VERBOSE = True
        if args.clean:
            user_settings.CLEAN = True
        if args.test:
            user_settings.UNITTEST = True
        if args.mathjax:
            user_settings.MATHJAX = True

# ----------------------------------------------------------------------------
#  Base class which describes my web site overall.
# ----------------------------------------------------------------------------

class WebSite(object):
    """
    Abstract class used for analyzing both local and remote (ftp server) websites.
    Contains the web-walking functions which traverse the directory structures and files.
    These will be overloaded in the subclasses with differently specialized methods for either walking a disk drive directory with ls commands or else walking a remote directory with FTP commands.
    Child classes may define additional functions which only they need.
    """

    def __init__(self, settings):
        """Set up root directories"""

        # Import the user settings.
        self.user_settings = settings

        # Queue keeps track of directories not yet processed.
        self.queue = []

        # List of all directories traversed.
        self.directories = []

        # List of files traversed, with file information.
        self.files = []

        # Find out the root directory and go there.
        self.root_dir = self.get_root_dir()
        self.go_to_root_dir(self.root_dir)

    # This is a Python decorator which says get_current_year is a class function.  And so there is no self first argument, and you can call it without creating an 
    # instance of this class.  Call it from anywhere, inside or outside the class, using WebSite.get_current_year().  You could just create a global function instead.)
    @staticmethod
    def get_current_year():
        """Get the current year."""
        return int(time.gmtime()[0])

    @staticmethod
    def get_current_two_digit_year():
        """Get the last two digits of the current year."""
        return WebSite.get_current_year() % 100

    @staticmethod
    def is_file_info_type(file_info):
        """Check if we have a file information structure or merely a simple file name."""
        try:
            if isinstance(file_info, list):
                return True
            elif isinstance(file_info, str):
                return False
            else:
                logging.error("is_file_info_type found a bad type.  Aborting...")
                raise UpdateWebException("Internal error for file type.  See the log file for details.  Aborting... ")
        except TypeError as detail:
            logging.error(f"is_file_info_type found a bad type {str(detail):s}.  Aborting...")
            raise UpdateWebException("Internal error for file type.  See the log file for details.  Aborting... ") from detail

    def get_root_dir(self):
        """Subclass:  Put code here to get the root directory"""
        return ""

    def go_to_root_dir(self, root_dir):
        """Subclass:  Put code here to go to the root directory"""
        pass  # Pythons's do-nothing statement.

    def one_level_down(self, d):
        """Subclass:  Fill in with a method which returns a list of the
        directories and files immediately beneath dir"""
        return [], []

    def walk(self, d, type_of_tree_search=TreeWalkSettings.BREADTH_FIRST_SEARCH):
        """Walk a directory in either depth first or breadth first order.  BFS is the default."""

        # Get all subfiles and subdirectories off this node.
        subdirectories, subfiles = self.one_level_down(d)

        # Add all the subfiles in order.
        for f in subfiles:

            name = self.strip_root(f)
            logging.debug(f"Webwalking:  Adding file {name[self.user_settings.FILE_NAME]:s} to list.")

            # Some files are private so skip them from consideration.
            pat = re.compile(self.user_settings.FILE_TO_SKIP)

            if pat.search(name[self.user_settings.FILE_NAME]):
                logging.debug( f"Webwalking:  Skipping private file {name[self.user_settings.FILE_NAME]:s}")
            # Don't upload any *.log files either;  we are currently writing to this file.
            elif name[self.user_settings.FILE_NAME].find(self.user_settings.LOGFILENAME) >= 0:
                logging.debug(f"Webwalking:  Skipping log file {name[self.user_settings.FILE_NAME]:s}")
            else:
                # OK to add this file to the list for possible uploading.
                self.files.append(name)

        # Queue up the subdirectories.
        for d in subdirectories:
            # Some directories are private such as .git or just temporary file
            # caches so skip them from consideration.
            pat = re.compile(self.user_settings.DIR_TO_SKIP)
            if pat.search(d):
                logging.debug(f"Webwalking:  Skipping private dir {d:s}")
            else:
                logging.debug(f"Webwalking:  Pushing dir {d:s} on the queue.")
                self.queue.append(d)

        # Search through the directories.
        while len(self.queue) > 0:
            # For breadth first search, remove from beginning of queue.
            if type_of_tree_search == TreeWalkSettings.BREADTH_FIRST_SEARCH:
                d = self.queue.pop(0)

            # For depth first search, remove from end of queue.
            elif type_of_tree_search == TreeWalkSettings.DEPTH_FIRST_SEARCH:
                d = self.queue.pop()
            else:
                d = self.queue.pop(0)

            name = self.strip_root(d)
            logging.debug(f"Webwalking:  Adding relative directory {name:s} to list, full path = {d:s}.")
            self.directories.append(name)

            self.walk(d)

    def strip_root(self, file_info):
        """Return a path, but strip off the root directory"""

        root = self.root_dir

        # Extract the file name.
        if self.is_file_info_type(file_info):
            name = file_info[self.user_settings.FILE_NAME]
        else:
            name = file_info

        # e.g. root = / and name = /Art/foo.txt yields stripped_path = Art/foo.txt
        # but root = /Sean and name = /Sean/Art/foo.txt yields stripped_path =
        # Art/foo.txt
        lenroot = len(root)
        if root == self.user_settings.DEFAULT_ROOT_DIR:
            pass
        else:
            lenroot = lenroot + 1

        stripped_path = name[lenroot:]

        if self.is_file_info_type(file_info):
            # Update the file name only.
            return [stripped_path,
                    file_info[self.user_settings.FILE_TYPE],
                    file_info[self.user_settings.FILE_DATE_TIME],
                    file_info[self.user_settings.FILE_SIZE]]
        else:
            return stripped_path

    def append_root_dir(self, root_dir, name):
        """Append the root directory to a path"""

        # e.g. root = /, and name = Art/foo.txt yields /Art/foo.txt
        # but root = /Sean, and name = Art/foo.txt yields /Sean/Art/foo.txt
        if root_dir == self.user_settings.DEFAULT_ROOT_DIR:
            return root_dir + name
        else:
            return root_dir + "/" + name

    def scan(self):
        """Scan the directory tree recursively from the root"""
        logging.debug(f"Webwalking:  Beginning recursive directory scan from root directory {self.root_dir:s}")
        self.walk(self.root_dir)

    def modtime(self, f):
        """Subclass:  Get file modification time"""
        pass

    def finish(self):
        """Quit web site"""
        logging.debug(f"Finished with WebSite object of class {type(self)}")
        pass

# ----------------------------------------------------------------------------
#  Subclass which knows about the local web site on disk.
# ----------------------------------------------------------------------------

class LocalWebSite(WebSite):
    """Walk the local web directory on local disk down from the root.
    Clean up temporary files and do other cleanup work."""

    def __init__(self, settings):
        """Go to web page root and list all files and directories."""

        # Initialize the parent class.
        WebSite.__init__(self, settings)

        self.root_dir = self.get_root_dir()
        logging.debug(f"LocalWebSite.__init__():  \tRoot directory: {self.root_dir:s}")

    def get_root_dir(self):
        """Get the name of the root directory"""
        return self.user_settings.local_root_dir

    def go_to_root_dir(self, root_dir):
        """Go to the root directory"""

        # Go to the root directory.
        logging.debug(f"LocalWebSite.go_to_root_dir():  \tchdir to root directory:  {root_dir:s}")
        os.chdir(root_dir)

        # Read it back.
        self.root_dir = os.getcwd()
        logging.debug(f"LocalWebSite.go_to_root_dir():  \tgetcwd root directory:  {self.root_dir:s}")

    def one_level_down(self, d):
        """List all files and subdirectories in the current directory, dir.  For files, collect file info
        such as time, date and size."""

        directories = []
        files = []

        # Change to current directory.
        os.chdir(d)

        # List all subdirectories and files.
        dir_list = os.listdir(d)

        if dir_list:
            for line in dir_list:
                # Add the full path prefix from the root.
                name = self.append_root_dir(d, line)
                logging.debug(f"LocalWebSite.one_level_down():  \tlocal dir or file {name:s}")

                # Is it a directory or a file?
                if os.path.isdir(name):
                    directories.append(name)
                elif os.path.isfile(name):
                    # First assemble the file information of name, time/date and size into a list.
                    # Can index it like an array.  For example,
                    # file_info = 
                    #   [ '/WebDesign/EquationImages/equation001.png',  -- The file name.
                    #      1,                                           -- Enum type FileType.FILE = 1.
                    #      datetime.datetime(2010, 2, 3, 17, 15),       -- UTC encoded in a date/time class.
                    #      4675]                                        -- File size in bytes.
                    file_info = [name,
                                 FileType.FILE,
                                 self.get_file_date_time(name),
                                 self.get_file_size(name)]
                    files.append(file_info)

        # Sort the names into order.
        if directories:
            directories.sort()
        if files:
            files.sort()

        return directories, files

    @staticmethod
    def get_file_date_time(file_name):
        """Get a local file time and date in UTC."""

        file_epoch_time = os.path.getmtime(file_name)
        file_time_utc = time.gmtime(file_epoch_time)[0: 6]
        # Create a datetime class from the UTC year, month, day, hour, minute, seconds.
        d = datetime.datetime(file_time_utc[0], file_time_utc[1], file_time_utc[2], file_time_utc[3], file_time_utc[4], file_time_utc[5])
        return d

    @staticmethod
    def get_file_size(file_name):
        """Get file size in bytes."""
        return os.path.getsize(file_name)

    @staticmethod
    def clean_up_temp_file(temp_file_name, file_name, changed):
        """Remove the original file, rename the temporary file name to the original name.
        If there are no changes, just remove the temporary file.
        """

        if changed:
            # Remove the old file now that we have the rewritten file.
            try:
                os.remove(file_name)
                logging.debug(f"Changes were made.  Removed original file {file_name:s}")
            except OSError as detail:
                logging.error(f"Cannot remove old file {file_name:s}: {str(detail):s}.  Need to remove it manually.")

            # Rename the new file to the old file name.
            try:
                os.rename(temp_file_name, file_name)
                logging.debug(f"Renamed temp file {temp_file_name:s} to original file {file_name:s}")
            except OSError as detail:
                logging.error(f"Cannot rename temporary file {temp_file_name:s} to old file name {file_name:s}: {str(detail):s}.  Need to rename manually")
        else:
            # No changes?  Remove the temporary file.
            try:
                os.remove(temp_file_name)
                logging.debug(f"No changes were made.  Removed temporary file {temp_file_name:s}")
            except OSError as detail:
                logging.error(f"Cannot remove temporary file {temp_file_name:s}: {str(detail):s}.  Need to remove it manually.")
        return

    @staticmethod
    def process_lines_of_file(in_file_name, out_file_name, process_line_function_list=None):
        """
        Process each line of a file with a list of functions.  Create a new temporary file.

        The default list is None which means make an exact copy.
        """

        # Assume no changes.
        changed = False

        # Open both input and output files for processing.  Check if we cannot do it.
        fin = None
        try:
            fin = open(in_file_name, "r")
        except IOError as detail:
            logging.error(f"process_lines_of_file():  \tCannot open file {in_file_name:s} for reading:  {str(detail):s} Aborting...")
            if fin is not None:
                fin.close()
            raise UpdateWebException("Internal error for processing a file.  See the log file for details.  Aborting... ") from detail
        fout = None
        try:
            fout = open(out_file_name, "w")
        except IOError as detail:
            logging.error(f"process_lines_of_file():  \tCannot open file {out_file_name:s} for writing:  {str(detail):s} Aborting...")
            if fout is not None:
                fout.close()
            raise UpdateWebException("Internal error for processing a file.  See the log file for details.  Aborting... ") from detail

        # Read each line of the file, aborting if there is a read error.
        try:
            line = fin.readline()

            # Rewrite the next line of the file using all the rewrite functions.
            while line:
                original_line = line
                # If we have one or more rewrite functions...
                if process_line_function_list is not None:
                    # ...apply each rewrite functions to the line, one after the other in order.
                    for processLineFunction in process_line_function_list:
                        if processLineFunction is not None:
                            line = processLineFunction(line)

                if original_line != line:
                    logging.debug(f"Rewrote the line:    >>>{original_line:s}<<< into >>>{line:s}<<< for file {in_file_name:s}")
                    changed = True

                fout.write(line)

                line = fin.readline()

            fin.close()
            fout.close()
        except IOError as detail:
            logging.error(f"File I/O error during reading/writing file {in_file_name:s} in process_lines_of_file: {str(detail):s}  Aborting...")
            raise UpdateWebException("Internal error for processing a file.  See the log file for details.  Aborting... ") from detail

        if changed:
            logging.debug(f"process_lines_of_file():  \tRewrote original file {in_file_name:s}."
                          f"Changes are in temporary copy {out_file_name:s}")

        # Return True if any lines were changed.
        return changed

    def clean(self):
        """Scan through all directories and files in the local on disk website and clean them up."""

        num_source_files_changed = 0
        num_source_files_syntax_highlighted = 0

        logging.debug("Cleaning up the local web page.")

        if self.directories is None or self.files is None:
            logging.error("Web site has no directories or files.  Aborting...")
            raise UpdateWebException("Internal error for cleaning up the local web site.  See the log file for details.  Aborting... ")

        for d in self.directories:

            if self.is_temp_dir(d):
                # Add the full path prefix from the root.
                name = self.append_root_dir(self.get_root_dir(), d)
                try:
                    logging.debug(f"Removing temp dir {self.root_dir:s} recursively")
                    shutil.rmtree(name)
                except OSError as detail:
                    logging.error(f"Cannot remove temp dir {name:s}: {str(detail):s}")

        for f in self.files:
            # Add the full path prefix from the root.
            full_file_name = self.append_root_dir(
                self.get_root_dir(), f[self.user_settings.FILE_NAME])

            # Remove all temporary files.
            if self.is_temp_file(f):
                try:
                    logging.debug(f"Removing temp file {full_file_name:s}")
                    os.remove(full_file_name)
                except OSError as detail:
                    logging.error(f"Cannot remove temp dir {full_file_name:s}: {str(detail):s}")

            # Update source code files.
            if self.is_source_or_hypertext_file(f):
                changed = self.rewrite_source_file(full_file_name)
                if changed:
                    num_source_files_changed += 1
                    logging.debug(f"Rewrote source code file {self.root_dir:s}")

            # Generate a  syntax highlighted code listing.  
            # Make it the same time and date as the original code.  Then, only if there are recent changes, we will update the remote server.
            if self.is_file_to_syntax_highlight(f):
                # syntax_highlighted_file_name = self.create_syntax_highlighted_code_listing(full_file_name, dry_run=True)
                syntax_highlighted_file_name = self.create_syntax_highlighted_code_listing(full_file_name)
                if syntax_highlighted_file_name is not None:
                    logging.debug(f"Generated a syntax highlighted source listing file {syntax_highlighted_file_name:s} for the file {full_file_name:s}")
                else:
                    logging.debug(f"Failed to generate a syntax highlighted source listing file for {full_file_name:s}")
                num_source_files_syntax_highlighted += 1

        logging.debug(f"Number of source files rewritten = {num_source_files_changed:10d}")
        logging.debug(f"Number of source files syntax highlighted = {num_source_files_syntax_highlighted:10d}")

    def is_temp_file(self, file_info):
        """Identify a file name as a temporary file"""

        file_name = file_info[self.user_settings.FILE_NAME]

        # Suffixes and names for temporary files be deleted.
        pat = self.user_settings.TEMP_FILE_SUFFIXES
        match = pat.search(file_name)
        # Remove any files containing twiddles anywhere in the name.
        if match or file_name.find(self.user_settings.VIM_TEMP_FILE_EXT) >= 0:
            return True

        return False

    def is_temp_dir(self, dir_name):
        """Identify a name as a temporary directory."""

        p = self.user_settings.TEMP_DIR_SUFFIX
        return p.search(dir_name)

    def is_source_or_hypertext_file(self, file_info):
        """ Check if the file name is a source file or a hypertext file."""

        file_name = file_info[self.user_settings.FILE_NAME]
        p1 = self.user_settings.SOURCE_FILE_PATTERN
        p2 = self.user_settings.HYPERTEXT_FILE_PATTERN
        if p1.search(file_name) or p2.search(file_name):
            return True
        else:
            return False

    def is_file_to_syntax_highlight(self, file_info):
        """Check if this file type should have a syntax highlighted source listing."""

        # Take apart the file name.
        full_file_name = file_info[self.user_settings.FILE_NAME]
        file_name = Path(full_file_name).name

        p = self.user_settings.FILE_TO_HIGHLIGHT_PATTERN
        if p.search(file_name):
            return True
        else:
            return False

    def rewrite_substring(self, line):
        """Rewrite a line containing a pattern of your choice"""

        # Start with the original unchanged line.
        rewritten_line = line

        # Do the replacements in order from first to last.
        for match_replace_tuple in self.user_settings.STRING_REPLACEMENT_LIST:
            # Get the next pattern match replacement string tuple.
            [pat, rep_string] = match_replace_tuple
            # Does it match?  Then do string substitution, else leave the line unchanged.
            match = pat.search(rewritten_line)
            if match:
                # Now we have these cases:
                #     -No capture variables at all, but just a straightforward pattern match followed by a string substitution.
                #     -One or more capture variable names in the pattern (?P<varname> ... ) along with the same corresponding match group names in replacement string \\g<varname> ... 
                #      If pat.sub() finds any inconsistency here such as the capture variable names not matching the group names, it will throw an exception.
                try:
                    sub = pat.sub(rep_string, rewritten_line)
                    rewritten_line = sub
                except IndexError as detail:
                    logging.error(f"ERROR: {str(detail):s}.  Did not find a capture variable name in the pattern (?P<varname> ... ) along with its corresponding match group name in replacement string \\g<varname> in updateweb.yaml.    Did not rewrite the line |{rewritten_line:s}|")
 
        return rewritten_line

    def rewrite_email_address_line(self, line):
        """Rewrite lines containing old email addresses."""

        # Search for the old email address.
        pat = self.user_settings.OLD_EMAIL_ADDRESS
        match = pat.search(line)

        # Replace the old address with my new email address.
        if match:
            new_address = self.user_settings.NEW_EMAIL_ADDRESS
            sub = pat.sub(new_address, line)
            line = sub

        return line

    def rewrite_copyright_line(self, line):
        """Rewrite copyright lines if they are out of date."""

        # Match the lines,
        #     Copyright (C) nnnn-mmmm by Sean Erik O'Connor.
        #     Copyright &copy; nnnn-mmmm by Sean Erik O'Connor.
        # and pull out the old year and save it.
        pat = self.user_settings.COPYRIGHT_LINE
        match = pat.search(line)

        # Found a match.
        if match:
            old_year = int(match.group('old_year'))

            # Replace the old year with the current year.
            # We matched and extracted the old copyright symbol into the variable
            # 'symbol' using the pattern syntax (?P<symbol> \(C\) | &copy;)
            # We now insert it back by placing the special syntax \g<symbol>
            # into the replacement string.
            if old_year < WebSite.get_current_year():
                new_copyright = r"Copyright \g<symbol> \g<old_year>-" + str(WebSite.get_current_year()) + " by Sean Erik"
                sub = pat.sub(new_copyright, line)
                line = sub
        return line

    def rewrite_last_update_line(self, line):
        """Rewrite the Last Updated line if the year is out of date."""

        # Match the last updated line and pull out the year.
        #      last updated 01 Jan 26.
        p = self.user_settings.LAST_UPDATED_LINE
        m = p.search(line)

        if m:
            last_update_year = int(m.group('year'))

            # Convert to four digit years.
            if last_update_year > 90:
                last_update_year += 1900
            else:
                last_update_year += 2000

            # If the year is old, rewrite to "01 Jan <current year>".
            if last_update_year < WebSite.get_current_year():
                two_digit_year = self.user_settings.TWO_DIGIT_YEAR_FORMAT % self.get_current_two_digit_year()
                sub = p.sub('last updated 01 Jan ' + two_digit_year, line)
                line = sub

        return line

    def rewrite_source_file(self, file_name):
        """Rewrite copyright lines, last updated lines, etc."""
        changed = False

        # Create a new temporary file name for the rewritten file.
        temp_file_name = file_name + self.user_settings.TEMP_FILE_EXT

        # Apply changes to all lines of the temporary file.  Apply change functions in
        # the sequence listed.
        if self.process_lines_of_file(file_name, temp_file_name,
                                      [self.rewrite_copyright_line,
                                       self.rewrite_last_update_line,
                                       self.rewrite_email_address_line,
                                       self.rewrite_substring]):
            logging.debug(f"Changed (rewritten) source file {file_name:s}")
            changed = True

        # Rename the temporary file to the original file name.  If no changes, just delete the temp file.
        self.clean_up_temp_file(temp_file_name, file_name, changed)

        return changed

    @staticmethod
    def create_syntax_highlighted_code_listing(source_file_name, **kwargs):
        """Create a syntax highlighted source listing for the file and return its name.  Return None if there is an error.
        Keep the same date/time as the original file."""

        # kwargs is a dictionary for key, value in kwargs.items():
        # for key, value in kwargs.items():
        #    if key in kwargs:
        #        print( f"kwargs:" )
        #        print( f"  key   = |{key}|")
        #        print( f"  value = |{value}|" )
        dry_run_value = kwargs.get('dry_run') 
        dry_run = False
        if dry_run_value is not None and dry_run_value is True:
            dry_run = True

        # Take apart the file name.
        file_name_without_extension = Path(source_file_name).stem
        file_extension = Path(source_file_name).suffix

        # Append *.html to the source code file name.  This will be the syntax highlighted code listing.
        syntax_highlighted_file_name = f"{source_file_name}.html"

        # In the special case of Jupyter notebooks, use the Jupyter to HTML converter.
        if file_extension == ".ipynb":
            if dry_run:
                logging.debug(f"Dry run only:  don't generate the syntax highlighted file {syntax_highlighted_file_name:s}")
                return None
            # Python manual recommends using the run() command instead of Popen().  See https://docs.python.org/3/library/subprocess.html#subprocess.run
            try:
                shell_command = f"jupyter nbconvert {source_file_name} --to html --output {syntax_highlighted_file_name}"
                # Throw an exception if we can't run the process.  
                # Capture the standard output and standar error and dump to /dev/null so it doesn't print to the command line when running this script.
                # Since the shell command is a single string, use shell=True in the run() command.
                subprocess.run([shell_command],shell=True,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as detail: 
                logging.error(f"Cannot convert the Jupyter file {source_file_name:s} to a syntax highlighted file: {str(detail):s}  Aborting...")
                return None
        # Otherwise, use the Pygments syntax highlighter.
        else:
            # First choose the language lexer from the file name itself if there's no extension.
            # Dotted file names are treated as the entire file name.
            match file_name_without_extension:
                case "makefile":
                    lexer = MakefileLexer()
                case ".bash_profile"|".bashrc"|".bash_logout":
                    lexer = BashLexer()
                case ".vimrc":
                    lexer = VimLexer()
                case ".gitignore_global" | ".gitignore" | ".gitconfig":
                    lexer = OutputLexer() # No formatting.
                case _:
                    # Choose the language lexer from the file extension.  Web stuff first, then programming languages.
                    match file_extension:
                        case ".html":
                            lexer = HtmlLexer()
                        case ".css":
                            lexer = CssLexer()
                        case ".js":
                            lexer = JavascriptLexer()
                        case ".sh":
                            lexer = BashLexer()
                        case ".py":
                            lexer = PythonLexer()
                        case ".c" | ".h":
                            lexer = CLexer()
                        case ".hpp" | ".cpp":
                            lexer = CppLexer()
                        case ".lsp":
                            lexer = CommonLispLexer()
                        case ".for" | ".FOR" | ".f":
                            lexer = FortranFixedLexer()  # Fixed format FORTRAN, not FORTRAN 90.
                        case ".txt" | ".dat":            # Generic data file;  no formatting.
                            lexer = OutputLexer()
                        case ".tex":
                            lexer = TexLexer()           # LaTeX, TeX, or related files.
                        case ".m":
                            lexer = MatlabLexer()
                        case ".yaml":
                            lexer = YamlLexer()
                        case _:
                            logging.error(f"Can't find a lexer for file {source_file_name}.  Cannot generate a syntax highlighted source listing.  Aborting...")
                            return None

            # Read the source code file into a single string.
            try:
                with open(source_file_name, 'r') as fp:
                    source_file_string = fp.read()
            except OSError as detail:
                logging.error(f"Cannot read the source code file {source_file_name:s} for syntax highlighting: {str(detail):s}  Aborting...")

            # Top level Pygments function generates the HTML for the highlighted code.
            highlighted_html_source_file_string = highlight(source_file_string, lexer, HtmlFormatter(linenos="inline"))

            # The style sheet is always the same for all languages.
            style_sheet = HtmlFormatter().get_style_defs('.highlight')

            # Write out the syntax colored file.
            if dry_run:
                logging.debug(f"Dry run only:  don't generate the syntax highlighted file {syntax_highlighted_file_name:s}")
                return None
            else:
                try:
                    # Write out the highlighted code listing in HTML with CSS style sheet attached.
                    with open(syntax_highlighted_file_name, 'w') as fp:
                        fp.write(UserSettings.BASIC_HTML_BEGIN)
                        fp.write(style_sheet)
                        fp.write(UserSettings.BASIC_HTML_MIDDLE)
                        fp.write(highlighted_html_source_file_string)
                        fp.write(UserSettings.BASIC_HTML_END)
                except OSError as detail:
                    logging.error(f"Cannot write the syntax highlighted file {syntax_highlighted_file_name:s}: {str(detail):s}  Aborting...")
        # ------- end Pygments syntax highlighter

        # Set the syntax highlighted code file to the same modification and access time and date as the source file.
        file_stat = os.stat(source_file_name)
        os.utime(syntax_highlighted_file_name, (file_stat[stat.ST_ATIME], file_stat[stat.ST_MTIME]))

        # Are the original source and the syntax highlighted code the same data and time?
        dates_and_times_source_file_name             = LocalWebSite.get_file_date_time(syntax_highlighted_file_name)
        dates_and_times_syntax_highlighted_file_name = LocalWebSite.get_file_date_time(syntax_highlighted_file_name)
        if dates_and_times_source_file_name != dates_and_times_syntax_highlighted_file_name:
            logging.error(f"Source code and syntax highlighted source don't have the same times.  source time = {dates_and_times_source_file_name.ctime():s} syntax highlighted time = {dates_and_times_syntax_highlighted_file_name.ctime():s} Aborting...")
            return None

        logging.debug(f"Generated a syntax highlighted listing {syntax_highlighted_file_name:s} for the source code file {source_file_name:s} with the same time and date = {dates_and_times_source_file_name.ctime():s}")
        return syntax_highlighted_file_name

# ----------------------------------------------------------------------------
#   Subclass which knows about the remote web site.
# ----------------------------------------------------------------------------

class RemoteWebSite(WebSite):
    """Walk the remote web directory on a web server down from the root.
       Use FTP commands:
           https://en.wikipedia.org/wiki/List_of_FTP_commands
       Use the Python ftp library:
           https://docs.python.org/3/library/ftplib.html
    """

    def __init__(self, user_settings):
        """Connect to FTP server and list all files and directories."""

        # Root directory of FTP server.
        self.root_dir = user_settings.FTP_ROOT_NAME
        logging.debug(f"Set the remote web site ftp root dir = {self.root_dir:s}")

        # Connect to FTP server and log in.
        try:
            # Turn on for troubleshooting ftp on the remote server.
            # self.ftp.set_debuglevel( 2 )
            # print( f"\nTrying ftp login to server name = {user_settings.SERVER_NAME} user name = {user_settings.USER_NAME} password =  {user_settings.PASSWORD_NAME}\n")
            self.ftp = ftplib.FTP(user_settings.SERVER_NAME)
            self.ftp.login(user_settings.USER_NAME, user_settings.PASSWORD_NAME)
        # Catch all exceptions with the parent class Exception:  all built-in,
        # non-system-exiting exceptions are derived from this class.
        except Exception as detail:
            # Extract the string message from the exception class with str().
            logging.error(f"Remote web site cannot login to ftp server: {str(detail):s}  Aborting...")
            raise UpdateWebException("Problem accessing remote web site.  See the log file for details.  Aborting... ") from detail
        else:
            logging.debug("Remote web site ftp login succeeded.")

        logging.debug(f"Remote web site ftp welcome message {self.ftp.getwelcome():s}")

        # Initialize the superclass.
        WebSite.__init__(self, user_settings)

    def go_to_root_dir(self, root_dir):
        """Go to the root directory"""

        try:
            # Go to the root directory.
            self.ftp.cwd(root_dir)
            logging.debug(f"ftp root directory (requested) = {self.root_dir:s}")

            # Read it back.
            self.root_dir = self.ftp.pwd()
            logging.debug(f"ftp root directory (read back from server): {self.root_dir:s}")

        except Exception as detail:
            logging.error(f"go_to_root_dir(): \tCannot ftp cwd or pwd root dir {root_dir:s} {str(detail):s} Aborting...")
            raise UpdateWebException("Problem accessing remote web site.  See the log file for details.  Aborting... ") from detail

    def get_root_dir(self):
        """Get the root directory name"""

        return self.root_dir

    def finish(self):
        """Quit remote web site"""
        logging.debug(f"Finished with WebSite object of class {type(self)}")
        try:
            self.ftp.quit()
        except Exception as detail:
            logging.error(f"Cannot ftp quit: {str(detail):s}")

    def one_level_down(self, d):
        """List files and directories in a subdirectory using ftp"""

        directories = []
        files = []

        try:
            # ftp listing from current dir.
            logging.debug(f"RemoteWebSite.one_level_down():  \tftp cwd: {d:s}")
            self.ftp.cwd(d)
            dir_list = []

            # Use the nonstandard -a option in LIST to show all the hidden .* files.
            # But now we have the problem that . and .. (the UNIX current and parent directories) will be in the ftp list of directories.
            # Note the second argument requires a callback function.
            self.ftp.retrlines('LIST -a', dir_list.append)

        except Exception as detail:
            logging.error(f"one_level_down(): \tCannot ftp cwd or ftp LIST dir {d:s}:  {str(detail):s} Aborting...")
            raise UpdateWebException("Problem accessing remote web site.  See the log file for details.  Aborting... ") from detail

        for line in dir_list:
            logging.debug(f"RemoteWebSite.one_level_down():  \tftp LIST: {line:s}")

            # Line should at least have the minimum FTP information.
            if len(line) >= self.user_settings.MIN_FTP_LINE_LENGTH:
                # Parse the FTP LIST and put the pieces into file_info.
                file_info = self.parse_ftp_list(line)
                logging.debug(f"RemoteWebSite.one_level_down():  \tftp parsed file information: {file_info[self.user_settings.FILE_NAME]:s}")

                # Skip over the UNIX hidden files for current and parent directories . and ..  Also skip over any NULL file names.
                if file_info[self.user_settings.FILE_NAME] == "" or file_info[self.user_settings.FILE_NAME] == "." or file_info[self.user_settings.FILE_NAME] == "..":
                    logging.debug(f"RemoteWebSite.one_level_down():  \tftp skipping the file name: {file_info[self.user_settings.FILE_NAME]:s}")
                    pass
                # For a directory, prefix the full path prefix from the root to the directory name and add to the directory list.
                elif file_info[self.user_settings.FILE_TYPE] == FileType.DIRECTORY:
                    dirname = self.append_root_dir( d, file_info[self.user_settings.FILE_NAME])
                    logging.debug(f"RemoteWebSite.one_level_down():  \tftp dir (full path): {dirname:s}")
                    directories.append(dirname)
                # For a file:  Add the full path prefix from the root to the file name.
                else:
                    file_info[self.user_settings.FILE_NAME] = self.append_root_dir( d, file_info[self.user_settings.FILE_NAME])
                    logging.debug(f"RemoteWebSite.one_level_down():  \tftp file (full path):\
                        {file_info[self.user_settings.FILE_NAME]:s}")
                    files.append(file_info)
            else:
                logging.error(f"RemoteWebSite.one_level_down():  \tFTP LIST line is too short:  {line:s}")

        directories.sort()
        files.sort()

        return directories, files

    def modtime(self, f):
        """Get the modification time of a file via ftp.  Return 0 if ftp cannot get it."""
        modtime = 0

        try:
            response = self.ftp.sendcmd('MDTM ' + f)
            # MDTM returns the last modified time of the file in the format
            # "213 YYYYMMDDhhmmss \r\n <error-response>
            # MM is 01 to 12, DD is 01 to 31, hh is 00 to 23, mm is 00 to 59, ss is 0 to 59.
            # error-response is 550 for info not available, and 500 or 501 if command cannot
            # be parsed.
            if response[:3] == '213':
                modtime = response[4:]
        except ftplib.error_perm as detail:
            logging.error(f"Cannot get file modification time from the ftp server: {str(detail):s} Aborting...")
            modtime = 0

        return modtime

    def parse_ftp_list(self, line):
        """Parse the ftp file listing and return file name, datetime and file size.

           An FTP LIST command will give output which looks like this for a file:

               -rw-r--r--    1 1000       free             4084 Jul 18 16:55 sparkCoil.png

           and for a directory:

                drwxr-xr-x    2 1000       free             4096 Jul 18 16:36 ReadingList

           FTP uses UTC for its listings; the conversion to local time is done by the OS.
           We can have problems on New Year's Eve.  For example, the local file date/time is

              Mon Jan  1 06:23:12 2018

           But the remote file date/time from FTP listing doesn't show a year even though we
           know it was written to the server in 2017.

               Mon Dec 31 03:02:00

           So we default the remote file year to current year 2018 and get

               Mon Dec 31 03:02:00 2018

           Now we think that the remote file is newer by 363.860278 days.
        """

        # Find out if we've a directory or a file.
        if line[0] == 'd':
            dir_or_file = FileType.DIRECTORY
        else:
            dir_or_file = FileType.FILE

        pattern = self.user_settings.FTP_LISTING

        # Sensible defaults.
        filesize = 0
        filename = ""
        # Default the time to midnight.
        hour = 0
        minute = 0
        seconds = 0
        # Default the date to Jan 1 of the current year.
        month = 1
        day = 1
        year = WebSite.get_current_year()

        # Extract time and date from the ftp listing.
        match = pattern.search(line)

        if match:
            filesize = int(match.group('bytes'))
            month = self.user_settings.monthToNumber[match.group('mon')]
            day = int(match.group('day'))

            # Remote file listing contains the year.  The FTP listing will omit the hour and minute.
            if match.group('year'):
                year = int(match.group('year'))
                logging.debug(f"ftp has year = {year} but is probably missing hour and minute")
            else:
                # Remote file listing omits the year.  Default the year to the current UTC time year.
                # That may be incorrect (see comments above).
                year = WebSite.get_current_year()
                logging.debug(f"ftp is missing the year;  use the current year = {year}")

            # If the FTP listing has the hour and minute, it will omit the year.
            if match.group('hour') and match.group('min'):
                hour = int(match.group('hour'))
                minute = int(match.group('min'))
                logging.debug(f"ftp has hour = {hour} and minute = {minute} so is probably missing the year")

            filename = match.group('filename')

        # Package up the time and date nicely.
        # Note if we didn't get any matches, we'll default the remote date and
        # time to Jan 1 midnight of the current year.
        d = datetime.datetime(year, month, day, hour, minute, seconds)

        return [filename, dir_or_file, d, filesize]

# ----------------------------------------------------------------------------
#  Class for synchronizing local and remote web sites.
# ----------------------------------------------------------------------------

class UpdateWeb(object):
    """Given previously scanned local and remote directories, update the remote website."""

    def __init__(
            self,
            user_settings,
            local_directory_list,
            local_file_info,
            remote_directory_list,
            remote_file_info):
        """Connect to remote site.  Accept previously scanned local and remote files and directories."""

        # Initialize from args.
        self.user_settings = user_settings
        self.local_directory_list = local_directory_list
        self.remote_directory_list = remote_directory_list
        self.local_file_info = local_file_info
        self.remote_file_info = remote_file_info

        # Initialize defaults.
        self.local_files_list = []
        self.remote_files_list = []
        self.local_file_to_size = {}
        self.local_file_to_date_time = {}
        self.remote_file_to_date_time = {}
        self.local_only_dirs = []
        self.local_only_files = []
        self.remote_only_dirs = []
        self.remote_only_files = []
        self.common_files = []

        # Connect to FTP server and log in.
        try:
            self.ftp = ftplib.FTP(self.user_settings.SERVER_NAME)
            self.ftp.login(self.user_settings.USER_NAME, self.user_settings.PASSWORD_NAME)
        except Exception as detail:
            logging.error(f"Cannot login to ftp server: {str(detail):s} Aborting...")
            raise UpdateWebException("Problem accessing remote web site.  See the log file for details.  Aborting... ") from detail
        else:
            logging.debug("ftp login succeeded.")

        logging.debug(f"ftp server welcome message:  {self.ftp.getwelcome():s}")

        # Local root directory.
        self.local_root_dir = self.user_settings.local_root_dir
        logging.debug(f"Local root directory: {self.local_root_dir:s}")

        # Root directory of FTP server.
        self.ftp_root_dir = self.user_settings.FTP_ROOT_NAME
        logging.debug(f"ftp root directory (requested) = {self.ftp_root_dir:s}")

        # Transform KB string to integer bytes.  e.g. "200" => 2048000
        self.file_size_limit = int(self.user_settings.FILE_SIZE_LIMIT_NAME) * 1024

        try:
            # Go to the root directory.
            self.ftp.cwd(self.ftp_root_dir)

            # Read it back.
            self.ftp_root_dir = self.ftp.pwd()
            logging.debug(f"ftp root directory (read back from server): {self.ftp_root_dir:s}")
        except Exception as detail:
            logging.error(f"UpdateWeb(): \tCannot ftp cwd or ftp LIST dir {self.ftp_root_dir:s} {str(detail):s} Aborting...")

    def append_root_dir(self, root_dir, name):
        """Append the root directory to a path"""

        # e.g. root = /, and name = Art/foo.txt yields /Art/foo.txt
        # but root = /Sean, and name = Art/foo.txt yields /Sean/Art/foo.txt
        if root_dir == self.user_settings.DEFAULT_ROOT_DIR:
            return root_dir + name
        else:
            return root_dir + "/" + name

    def file_info(self):
        """Create lists of file names from the file information.  Also create dictionaries which map file names onto
        dates, times, and sizes."""

        # Extract file names.
        self.local_files_list = [
            file_info[self.user_settings.FILE_NAME] for file_info in self.local_file_info]
        self.remote_files_list = [
            file_info[self.user_settings.FILE_NAME] for file_info in self.remote_file_info]

        # Use a dictionary comprehension to create key/value pairs, 
        #     (file name, file date/time)
        # which map file names onto date/time.
        self.local_file_to_date_time = {file_info[self.user_settings.FILE_NAME]: file_info[self.user_settings.FILE_DATE_TIME] for file_info in self.local_file_info}
        self.remote_file_to_date_time = {file_info[self.user_settings.FILE_NAME]: file_info[self.user_settings.FILE_DATE_TIME] for file_info in self.remote_file_info}

        # Dictionary comprehension creates a mapping of local file names onto file sizes.
        self.local_file_to_size = {file_info[self.user_settings.FILE_NAME]: file_info[self.user_settings.FILE_SIZE] for file_info in self.local_file_info}

    def update(self):
        """Scan through the local website, cleaning it up.
        Go to remote website on my servers and synchronize all files."""

        self.file_info()

        # Which files and directories are different.
        self.changes()

        # Synchronize with the local web site.
        self.synchronize()

    def changes(self):
        """Find the set of different directories and files on local and remote."""

        # Add all directories which are only on local to the dictionary.
        dir_to_type = {
            d: FileType.ON_LOCAL_ONLY for d in self.local_directory_list}

        # Scan through all remote directories, adding those only on remote or
        # on both.
        for d in self.remote_directory_list:
            if d in dir_to_type:
                dir_to_type[d] = FileType.ON_BOTH_LOCAL_AND_REMOTE
            else:
                dir_to_type[d] = FileType.ON_REMOTE_ONLY

        # Add all files which are only on local to the dictionary.
        file_to_type = {
            f: FileType.ON_LOCAL_ONLY for f in self.local_files_list}

        # Scan through all remote files, adding those only on remote or on
        # both.
        for f in self.remote_files_list:
            if f in file_to_type:
                file_to_type[f] = FileType.ON_BOTH_LOCAL_AND_REMOTE
            else:
                file_to_type[f] = FileType.ON_REMOTE_ONLY

        logging.debug("Raw dictionary dump of directories")
        for k, v in dir_to_type.items():
            logging.debug(f"\t dir:  {str(k):s}  type: {str(v):s}")

        logging.debug("Raw dictionary dump of files")
        for k, v in file_to_type.items():
            logging.debug(f"\t file: {str(k):s}  type: {str(v):s}")

        # List of directories only on local.  Keep the ordering.
        self.local_only_dirs = [
            d for d in self.local_directory_list if dir_to_type[d] == FileType.ON_LOCAL_ONLY]

        # List of directories only on remote.  Keep the ordering.
        self.remote_only_dirs = [
            d for d in self.remote_directory_list if dir_to_type[d] == FileType.ON_REMOTE_ONLY]

        # We don't care about common directories, only their changed files, if
        # any.

        # List of files only on local.  Keep the ordering.
        self.local_only_files = [
            f for f in self.local_files_list if file_to_type[f] == FileType.ON_LOCAL_ONLY]

        # List of files only on remote.  Keep the ordering.
        self.remote_only_files = [
            f for f in self.remote_files_list if file_to_type[f] == FileType.ON_REMOTE_ONLY]

        # List of common files on both local and remote.  Keep the ordering.
        self.common_files = [
            f for f in self.local_files_list if file_to_type[f] == FileType.ON_BOTH_LOCAL_AND_REMOTE]

        logging.debug("*** Directories only on local ******************************")
        for d in self.local_only_dirs:
            logging.debug(f"\t {d:s}")

        logging.debug("*** Directories only on remote ******************************")
        for d in self.remote_only_dirs:
            logging.debug(f"\t {d:s}")

        logging.debug("*** Files only on local ******************************")
        for f in self.local_only_files:
            logging.debug(f"\t {f:s}")

        logging.debug("*** Files only on remote ******************************")
        for f in self.remote_only_files:
            logging.debug(f"\t {f:s}")

        logging.debug("*** Common files ******************************")
        for f in self.common_files:
            logging.debug(f"name {f:s}")
            logging.debug(f"\tlocal time {self.local_file_to_date_time[f].ctime():s}")
            logging.debug(f"\tremote time {self.remote_file_to_date_time[f].ctime():s}")

    def synchronize(self):
        """Synchronize files and subdirectories in the remote directory with the local directory."""

        # If we have the same files in local and remote, compare their times
        # and dates.
        for f in self.common_files:
            local_file_time = self.local_file_to_date_time[f]
            remote_file_time = self.remote_file_to_date_time[f]

            # What's the time difference?
            time_delta = remote_file_time - local_file_time
            # How much difference, either earlier or later?
            seconds_different = abs(time_delta.total_seconds())
            minutes_different = seconds_different / 60.0
            hours_different = minutes_different / 60.0
            days_different = hours_different / 24.0

            # Assume no upload initially.
            upload_to_host = False

            logging.debug(f"Common file:  {f:s}.")

            # Remote file time is newer.
            # Allow 200 characters
            # Mathematics/AbstractAlgebra/PrimitivePolynomials/Project/Build/PrimpolyXCode/Primpoly/Primpoly.xcodeproj/project.xcworkspace/xcuserdata/seanoconnor.xcuserdatad/UserInterfaceState.xcuserstate

            if remote_file_time > local_file_time:
                # Remote file time is MUCH newer:  suspect time is out of joint on the server, so upload local local file to be safe.
                if minutes_different >= self.user_settings.MINUTES_NEWER_FOR_REMOTE_BEFORE_UPLOAD:
                    logging.error(f"Remote file {f:s} is MUCH newer by {minutes_different:8.1f} minutes [which exceeds the threshold = {self.user_settings.MINUTES_NEWER_FOR_REMOTE_BEFORE_UPLOAD} minutes]. Upload the file to be safe.")
                    logging.error(f"\tlocal time {local_file_time.ctime():s}")
                    logging.error(f"\tremote time {remote_file_time.ctime():s}")

                    # Set the local file to the current time.
                    full_file_name = self.append_root_dir(
                        self.local_root_dir, f)
                    if os.path.exists(full_file_name):
                        # Change the access and modify times of the file to the current time.
                        os.utime(full_file_name, None)
                        logging.error(f"Touching local file {full_file_name:s} to make it the current time")

                    upload_to_host = True
                # Remote file time is newer, but not by much.  Let's just assume a slight time mismatch on the server.  Don't upload.
                else:
                    logging.warning(f"Remote file {f:s} is only SLIGHTLY newer by {seconds_different:8.1f} seconds.  Probably just inaccurate time/date on the server.  Wait -- don't upload the file yet.")
                    logging.warning(f"\tlocal time {local_file_time.ctime():s}")
                    logging.warning(f"\tremote time {remote_file_time.ctime():s}")
                    upload_to_host = False

            # Local file time is newer.
            elif local_file_time > remote_file_time:
                # Local file time slightly newer than the remote file.  So we are pretty sure the local file really got changed vs the server file.
                if minutes_different >= self.user_settings.MINUTES_NEWER_FOR_LOCAL_BEFORE_UPLOAD:
                    logging.warning(f"Local file {f:20s} is SLIGHTLY newer by  {minutes_different:8.1f} minutes [which exceeds the threshold = {self.user_settings.MINUTES_NEWER_FOR_LOCAL_BEFORE_UPLOAD} minutes].  Uploading to remote server.")
                    logging.warning(f"\tlocal time {local_file_time.ctime():s}")
                    logging.warning(f"\tremote time {remote_file_time.ctime():s}")
                    upload_to_host = True
                else:
                    logging.warning(f"Local file {f:20s} is BARELY newer by {seconds_different:8.1f} seconds.  Probably just inaccurate time/date on the server.  Wait -- don't upload the file yet.")
                    logging.warning(f"\tlocal time {local_file_time.ctime():s}")
                    logging.warning(f"\tremote time {remote_file_time.ctime():s}")
                    upload_to_host = False

            # Cancel the upload if the file is too big for the server.
            size = self.local_file_to_size[f]
            if size >= self.file_size_limit:
                logging.error(f"upload():  Skipping upload of file {f:s} of size {size:d}; too large for server, limit is {self.file_size_limit:d} bytes")
                upload_to_host = False

            # Finally do the file upload.
            if upload_to_host:
                logging.debug(f"Uploading changed file {f:s}")
                # Suppress newline to keep the message to the console more compact.  Flush output buffer, so we can see the message right away.
                print(f"Uploading changed file {f:s}...  ", end='', flush=True)
                self.upload(f)

        # Remote directory is not in local.  Delete it.
        for d in self.remote_only_dirs:
            logging.debug(f"Deleting remote only directory {d:s}")
            print(f"Deleting remote only directory {d:s}...  ", end='', flush=True)
            self.rmdir(d)

        # Local directory missing on remote.  Create it.
        # Due to breadth first order scan, we'll create parent directories
        # before child directories.
        for d in self.local_only_dirs:
            logging.debug(f"Only on local.  Creating new remote dir {d:s}.")
            print(f"Creating new remote directory {d:s}...  ", end='', flush=True)
            self.mkdir(d)

        # Local file missing on remote.  Upload it.
        for f in self.local_only_files:
            logging.debug(f"Local only file.  Uploading {f:s} to remote.")

            #  But cancel the upload if the file is too big for the server.
            size = self.local_file_to_size[f]
            if size >= self.file_size_limit:
                logging.error(f"upload():  Skipping upload of file {f:s} of size {size:d};"
                              f" too large for server, limit is {self.file_size_limit:d} bytes")
            else:
                logging.debug(f"Uploading new file {f:s}")
                print(f"Uploading new file {f:s}...  ", end='', flush=True)
                self.upload(f)

        # Remote contains a file not present on the local.  Delete the file.
        for f in self.remote_only_files:
            logging.debug(f"Remote only file.  Deleting remote file {f:s}.")
            print(f"Deleting remote file {f:s}...  ", end='', flush=True)
            self.del_remote(f)

    def del_remote(self, relative_file_path):
        """Delete a file using ftp."""

        logging.debug(f"del_remote():  \trelative file path name: {relative_file_path:s}")

        # Parse the relative file path into file name and relative directory.
        relative_dir, file_name = os.path.split(relative_file_path)
        logging.debug(f"del_remote():  \tfile name: {file_name:s}")
        logging.debug(f"del_remote():  \trelative dir: {relative_dir:s}")
        logging.debug(f"del_remote():  \tremote root dir: {self.ftp_root_dir:s}")

        try:
            # Add the remote root path and go to the remote directory.
            remote_dir = self.append_root_dir(self.ftp_root_dir, relative_dir)
            logging.debug(f"del_remote():  \tftp cd remote dir: {remote_dir:s}")
            self.ftp.cwd(remote_dir)
        except Exception as detail:
            logging.error(f"del_remote():  \tCannot ftp chdir: {str(detail):s}  Skipping...")
        else:
            try:
                logging.debug(f"del_remote():  \tftp rm: {file_name:s}")

                # Don't remove zero length file names.
                if len(file_name) > 0:
                    self.ftp.delete(file_name)
                else:
                    logging.warning( "fdel_remote():  skipping ftp delete;  file NAME {file_name:s} had zero length")
            except Exception as detail:
                logging.error(f"del_remote():  \tCannot ftp rm: {str(detail):s}")

    def mkdir(self, relative_dir):
        """Create new remote directory using ftp."""

        logging.debug(f"mkdir():  \trelative dir path name: {relative_dir:s}")
        logging.debug(f"mkdir():  \tremote root dir: {self.ftp_root_dir:s}")

        # Parse the relative dir path into prefix dir and suffix dir.
        path, d = os.path.split(relative_dir)
        logging.debug(f"mkdir():  \tremote prefix dir: {path:s}")
        logging.debug(f"mkdir():  \tremote dir:  {d:s}")

        try:
            # Add the remote root path and go to the remote directory.
            remote_dir = self.append_root_dir(self.ftp_root_dir, path)
            logging.debug(f"mkdir():  \tftp cd remote dir: {remote_dir:s}")
            self.ftp.cwd(remote_dir)
        except Exception as detail:
            logging.error(f"mkdir():  \tCannot ftp chrdir: {str(detail):s}  Skipping...")
        else:
            try:
                logging.debug(f"mkdir():  \tftp mkd: {d:s}")
                self.ftp.mkd(d)
            except Exception as detail:
                logging.error(f"mkdir():  \tCannot ftp mkdir: {str(detail):s}")

    def rmdir(self, relative_dir):
        """Delete an empty directory using ftp."""

        logging.debug(f"rmdir():  \tintermediate dir path name: {relative_dir:s}")
        logging.debug(f"rmdir():  \tremote root dir: {self.ftp_root_dir:s}")

        # Parse the relative dir path into prefix dir and suffix dir.
        path, d = os.path.split(relative_dir)
        logging.debug(f"rmdir():  \tremote prefix dir: {path:s}")
        logging.debug(f"rmdir():  \tremote dir:  {d:s}")

        try:
            # Add the remote root path and go to the remote directory.
            remote_dir = self.append_root_dir(self.ftp_root_dir, path)
            logging.debug(f"rmdir():  \tftp cd remote dir: {remote_dir:s}")
            self.ftp.cwd(remote_dir)
        except Exception as detail:
            logging.error(f"rmdir():  \tCannot ftp chdir: {str(detail):s}  Skipping...")
        else:
            try:
                logging.debug(f"rmdir():  \tftp rmd: {d:s}")
                self.ftp.rmd(d)
            except Exception as detail:
                logging.error(f"rmdir():  \tCannot ftp rmdir dir {d:s}: {str(detail):s}.  Directory is probably not empty.  Do a manual delete.")

    def download(self, relative_file_path):
        """Download a binary file using ftp."""

        logging.debug(f"download():  \tfile name: {relative_file_path:s}")

        # Parse the relative file path into file name and relative directory.
        relative_dir, file_name = os.path.split(relative_file_path)
        logging.debug(f"download():  \tfile name: {file_name:s}")
        logging.debug(f"download():  \trelative dir: {relative_dir:s}")
        logging.debug(f"download():  \troot dir: {self.ftp_root_dir:s}")

        # Add the remote root path and go to the remote directory.
        remote_dir = self.append_root_dir(self.ftp_root_dir, relative_dir)
        logging.debug(f"download():  \tftp cd remote dir: {remote_dir:s}")

        try:
            self.ftp.cwd(remote_dir)
        except Exception as detail:
            logging.error(f"download():  \tCannot ftp chdir: {str(detail):s}  Skipping...")
        else:
            # Add the local root path to get the local file name.
            # Open local binary file to write into.
            local_file_name = self.append_root_dir(
                self.local_root_dir, relative_file_path)
            logging.debug(f"download():  \topen local file name: {local_file_name:s}")
            try:
                f = open(local_file_name, "wb")
                try:
                    # Calls f.write() on each block of the binary file.
                    # ftp.retrbinary( "RETR " + file_name, f.write )
                    pass
                except Exception as detail:
                    logging.error(f"download():  \tCannot cannot ftp retrbinary: {str(detail):s}")
                f.close()
            except IOError as detail:
                logging.error(f"download():  \tCannot open local file {local_file_name:s} for reading:  {str(detail):s}")

    def upload(self, relative_file_path):
        """Upload  a binary file using ftp."""

        logging.debug(f"upload():  \trelative file path name: {relative_file_path:s}")

        # Parse the relative file path into file name and relative directory.
        relative_dir, file_name = os.path.split(relative_file_path)
        logging.debug(f"upload():  \tfile name: {file_name:s}")
        logging.debug(f"upload():  \trelative dir: {relative_dir:s}")
        logging.debug(f"upload():  \tremote root dir: {self.ftp_root_dir:s}")

        # Add the remote root path and go to the remote directory.
        remote_dir = self.append_root_dir(self.ftp_root_dir, relative_dir)
        logging.debug(f"upload():  \tftp cd remote dir: {remote_dir:s}")

        try:
            self.ftp.cwd(remote_dir)
        except Exception as detail:
            logging.error(f"upload():  \tCannot ftp chdir: {str(detail):s}  Skipping...")
        else:
            # Add the local root path to get the local file name.
            # Open local binary file to read from.
            local_file_name = self.append_root_dir(
                self.local_root_dir, relative_file_path)
            logging.debug(f"upload():  \topen local file name: {local_file_name:s}")

            try:
                f = open(local_file_name, "rb")
                try:
                    # f.read() is called on each block of the binary file until
                    # EOF.
                    logging.debug(f"upload():  \tftp STOR file {file_name:s}")
                    self.ftp.storbinary("STOR " + file_name, f)
                except Exception as detail:
                    logging.error(f"upload():  \tCannot ftp storbinary: {str(detail):s}")
                f.close()
            except IOError as detail:
                logging.error(f"upload():  \tCannot open local file {local_file_name:s} for reading:  {str(detail):s}")

    def finish(self):
        """Log out of an ftp session"""
        logging.debug(f"Finished with UpdateWeb object of class {type(self)}")
        try:
            self.ftp.quit()
        except Exception as detail:
            logging.error(f"Cannot ftp quit because {str(detail):s}")

# ----------------------------------------------------------------------------
#  Main function
# ----------------------------------------------------------------------------

def main(raw_args=None):
    """Main program.  Clean up and update my website."""

    # Print the obligatory legal notice.
    print("""
    updateweb Version 7.3 - A Python utility program which maintains my web site.
    Copyright (C) 2007-2026 by Sean Erik O'Connor.  All Rights Reserved.

    It deletes temporary files, rewrites old copyright lines and email address
    lines in source files, then synchronizes all changes to my web sites.

    updateweb comes with ABSOLUTELY NO WARRANTY; for details see the
    GNU General Public License.  This is free software, and you are welcome
    to redistribute it under certain conditions; see the GNU General Public
    License for details.
    """)

    # Put ALL the main code into a try block!
    try:
        # ---------------------------------------------------------------------
        #  Load default settings and start logging.
        # ---------------------------------------------------------------------

        # Default user settings.
        user_settings = UserSettings()

        print( f"Running main( {raw_args} ) Python version\
               {sys.version_info[0]:d}.{sys.version_info[1]:d}.{sys.version_info[2]:d}\
               local web directory\
               {user_settings.local_root_dir}\n")
        # Get command line options such as --verbose.  Pass them back as flags in
        # user_settings.
        CommandLineSettings(user_settings, raw_args)

        # Load all unit test functions named test_* from UnitTest class, run the tests and exit.
        if user_settings.UNITTEST:
            suite = unittest.TestLoader().loadTestsFromTestCase(UnitTest)
            unittest.TextTestRunner(verbosity=2).run(suite)
            # We are done!
            print("  ...done!", flush=True)
            return

        # Start logging to file.
        if user_settings.VERBOSE:
            # Turn on logging for DEBUG and higher:  DEBUG, INFO, WARNING, ERROR, CRITICAL messages.
            loglevel = logging.DEBUG
        else:
            # Turn on logging for WARNING and higher:  WARNING, ERROR and CRITICAL messages.
            loglevel = logging.WARNING

        # Pick the log file name on the host.
        if user_settings.CLEAN:
            user_settings.LOGFILENAME = "/private/logLocal.txt"
        else:
            user_settings.LOGFILENAME = "/private/logRemote.txt"

        # Default is to skip processing or uploading MathJax files in /mathjax to the server.
        if not user_settings.MATHJAX:
            user_settings.DIR_TO_SKIP += "|mathjax"
        else:
            mathJaxPostUploadingAdvice = \
                [ "Processing and uploading new or changed mathjax files.",
                  "If you are loading MathJax for the first time --- don't forget to upload the file .htaccess manually using FileZilla or another ftp client...  ",
                  "FTP won't delete remote dir which are nonempty.  You might have to run this program several times to delete all subdirectories before the parent dir can be deleted.  Or you can manually delete with FTP.",
                  "If using FileZilla for manual deletion, change your FreeServer settings: Files->Site Manager->Transfer Settings->Limit number of simultaneous connections->Check the box.  This avoids ERROR 421 Too many connections...  ",
                "\n"
                ]
            print( mathJaxPostUploadingAdvice[0], flush=True)
            print( mathJaxPostUploadingAdvice[1], flush=True)
            print( mathJaxPostUploadingAdvice[2], flush=True)
            print( mathJaxPostUploadingAdvice[3], flush=True)
            print( mathJaxPostUploadingAdvice[4], flush=True)
            logging.debug( mathJaxPostUploadingAdvice[0], flush=True)
            logging.debug( mathJaxPostUploadingAdvice[1], flush=True)
            logging.debug( mathJaxPostUploadingAdvice[2], flush=True)
            logging.debug( mathJaxPostUploadingAdvice[3], flush=True)
            logging.debug( mathJaxPostUploadingAdvice[4], flush=True)

        # Configure the logging and start it.
        logging.basicConfig( level=loglevel, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename=user_settings.local_root_dir + user_settings.LOGFILENAME, filemode='w')
        logging.debug("********** Begin logging") 

        # ---------------------------------------------------------------------
        #  Scan the local website, finding out all files and directories.
        # ---------------------------------------------------------------------

        # Suppress newline to keep the message to the console more compact.  Flush output buffer, so we can see the message right away.
        print(f"Scanning the local web site from the root dir = {user_settings.local_root_dir}...  ", end='', flush=True)
        logging.debug(f"========================== Scanning the local web site from the root dir = {user_settings.local_root_dir}")

        local = LocalWebSite(user_settings)
        local.scan()

        # ---------------------------------------------------------------------
        # Clean up local website.
        # ---------------------------------------------------------------------

        # Clean up the directory by rewriting source code and hypertext and removing temporary files.
        print("Cleaning local web site...  ", end='', flush=True)
        logging.debug("========================== Cleaning the local web site")
        local.clean()

        # We are done with the first scan of the local web site and will dispose of it.
        local.finish()
        del local

        # ---------------------------------------------------------------------
        #  Rescan the local website since there will be changes to source
        #  files from the clean up stage.
        # ---------------------------------------------------------------------

        print(f"Rescan the local web site from root dir = {user_settings.local_root_dir}...  ", end='', flush=True)
        logging.debug(f"========================== Re-Scan the local web site from root dir = {user_settings.local_root_dir}")

        local = LocalWebSite(user_settings)

        local.scan()

        # ---------------------------------------------------------------------
        #  List all the local directories and files and their sizes.
        # ---------------------------------------------------------------------

        # Local website directories.
        local_directory_list = local.directories
        logging.debug("********** List of all the Local Directories")
        for d in local_directory_list:
            logging.debug(f"\t {d:s}")

        # Generate lists of the local website filenames only, and their sizes in byteskjjjj
        local_files_name_size_pairs = [[file_info[user_settings.FILE_NAME], file_info[user_settings.FILE_SIZE]] for file_info in local.files]
        total_number_of_files = len( local_files_name_size_pairs )
        logging.debug(f"********** List of all the Local Files from largest to smallest.  There are {total_number_of_files:15d} files.")
        local_files_name_size_pairs = sorted(local_files_name_size_pairs, key=lambda name_size: name_size[1], reverse=True)

        # Local website filenames only, and their dates and times.
        local_file_datetime_pairs = [[file_info[user_settings.FILE_NAME],file_info[user_settings.FILE_DATE_TIME]] for file_info in local.files]
        logging.debug(f"********** List of all Local Files Showing Their Date and Time")
        for file_datetime_pair in local_file_datetime_pairs:
            logging.debug(f"\t {file_datetime_pair[1].ctime():s} UTC {file_datetime_pair[0]:s}")

        # Total number of bytes in the local files.
        total_number_of_bytes = 0
        for file_size_pair in local_files_name_size_pairs:
            logging.debug(f"\t {file_size_pair[1]:10d} bytes {file_size_pair[0]:s}")
            total_number_of_bytes += file_size_pair[1]
        logging.debug(f"********** Total local file size = {total_number_of_bytes:10d} bytes = {total_number_of_bytes/(1024 ** 2):10.2f} MB (not counting skipped files and directories)")

        local.finish()

        if user_settings.CLEAN:
            logging.debug("========================== Done with local file and directory cleanup...")
            del local
            print("...done!", flush=True)
            return

        # ---------------------------------------------------------------------
        #  Scan the remote hosted web site.
        # ---------------------------------------------------------------------

        print("Scanning remote web site...  ", end='', flush=True)
        logging.debug("========================== Scanning the remote web site...")

        # Pick which website to update.
        logging.debug("Connecting to primary remote site.")
        remote = RemoteWebSite(user_settings)
        remote.scan()
        remote.finish()

        # ---------------------------------------------------------------------
        #  List all the remote server directories and files and their sizes.
        # ---------------------------------------------------------------------

        remote_directory_list = remote.directories
        logging.debug("********** Remote Directories")
        for d in remote_directory_list:
            logging.debug(f"\t {d:s}")

        # Local website filenames only, and their sizes in bytes.
        remote_files_name_size_list = [[file_info[user_settings.FILE_NAME], file_info[user_settings.FILE_SIZE]] for file_info in remote.files]
        total_number_of_files = len( remote_files_name_size_list )
        logging.debug(f"********** Remote Files [num files = {total_number_of_files:15d}]")
        remote_files_name_size_list = sorted(remote_files_name_size_list, key=lambda name_size: name_size[1], reverse=True)
        total_number_of_bytes = 0
        for file_size in remote_files_name_size_list:
            logging.debug(f"\t {file_size[1]:10d} bytes {file_size[0]:s}")
            total_number_of_bytes += file_size[1]
        logging.debug(f"\tTotal file size on remote (not counting skipped files and directories) = {total_number_of_bytes:10d} bytes = {total_number_of_bytes/(1024 ** 2):10.2f} MB")

        # ---------------------------------------------------------------------
        # Synchronize the local and remote web sites.
        # ---------------------------------------------------------------------

        print("Synchronizing remote and local web sites...  ", end='', flush=True)
        logging.debug("========================= Synchronizing remote and local web sites...")

        # Primary website.
        logging.debug("Connecting to primary remote site for synchronization.")
        sync = UpdateWeb(user_settings,
                         local.directories,
                         local.files,
                         remote.directories,
                         remote.files)

        sync.update()
        sync.finish()

        del sync
        del remote
        del local
        print("...done!", flush=True)

    except UpdateWebException as detail:
        logging.error(f"Couldn't update the web directory:  {str(detail):s}.  Aborting...")

    except RecursionError as detail:
        logging.error(f"Walking the directory tree became too deep for Python's recursion stack depth of {sys.getrecursionlimit():d} You can increase it with sys.setrecursionlimit(limit) {str(detail):s}.  Aborting...")

if __name__ == '__main__':
    """Python executes all code in this file.  Finally, we come here.  

    * If we are executing this file as a standalone Python script, 
      the name of the current module is set to __main__ and thus we'll call the main() function.

    * But if we are importing this code as a module, and calling it from another script, we will do this instead:

        import updateweb
        updateweb.main(["--test"])"""

    main()
