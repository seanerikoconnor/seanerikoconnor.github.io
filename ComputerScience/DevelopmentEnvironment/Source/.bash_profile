#============================================================================= 
#
#  FILE NAME
#
#     .bash_profile
#
# DESCRIPTION
#
#     Unix startup file executed upon log in. If you want to run this file every
#     time you open a new Terminal window in Linux, you will need to change Gnome
#     settings as follows: go to Terminal->Preferences->Profiles, create a new profile 
#     Under Command enable Run command as login shell.
#
#     See also install documentation for various apps here:
#         http://seanerikoconnor.freeservers.com/WebDesign/macLinuxComputerSetupForDevelopers.html
#
#  DATE
#
#      17 Oct 24
#
#  AUTHOR
#
#      Sean Erik O'Connor
#
#============================================================================= 
#

# When you first set up your macOS system. turn on a bunch of settings, then leave them off.
#whentoexecute="once"
whentoexecute=""

#------------- Portability -------
#
# Try to determine which system we are running on.

#-----------------------------------------------------------------------------
#--- Set the path
#-----------------------------------------------------------------------------

#   Be sure to put useful scripts and executables into the home bin directory:  ~/bin
bins="/usr/local/bin:~/bin"

# You need to set the hostname to get the correct configuration loaded.
# On MacBook,
#    sudo hostname WhiteHusky"
#    sudo scutil --set LocalHostName WhiteHusky
#    sudo scutil --set ComputerName WhiteHusky
#    sudo scutil --set HostName WhiteHusky
#    In System Preferences/Sharing change 'Computer Name' to WhiteHusky if it's not already changed.
#    In your local network configuration, rename the name provided by DHCP.
# On Ubuntu Linux, to change the hostname permanently,
#    hostnamectl set-hostname Gauss

# Find out the hostname.  In cygwin bash, strip off the trailing \r introduced.   
# The alternative is to use tr -d '\r'
hostname=`python3 -c "import platform; print( platform.node() )" | sed 's/^[ \r\n\t]*$//'`
#echo "hostname=|${hostname}|"

# Find out which operating system we are running on:  macOS, Linux, Windows/Cygwin, etc.
uname=`uname -s`
#echo "uname=|${uname}|"

# macOS.  Tested on my MacBook Pro laptop mid-2015 model with Intel x86_64 architecture.
if [ "${uname}" == "Darwin" ] ; then
    platform="macos"
# Linux.  Tested on my Ubuntu Linux system running on my Cyperpower PC with a 64-bit AMD CPU.
elif [ "${uname}" == "Linux" ] ; then
    platform="linux"
# Cygwin.  For cygwin 2.2 64-bit on Windows 10 64-bit.  Not tested.  From https://en.wikipedia.org/wiki/Uname
elif [ "${uname}" == "CYGWIN_NT-10.0" ] ; then
    platform="cygwin"
else
    echo "Can't identify OS platform = ${platform}.  Exiting .bash_profile"
    exit 1
fi
#echo "Using platform = ${platform}"

if [ "${platform}" == "macos" ] ; then
    py3bin="/Library/Frameworks/Python.framework/Versions/3.14/bin"
    #printf "Using macOS System Python version path = ${PATH}\n"
# Linux.  Tested on my Ubuntu Linux system running on my Cyperpower PC with a 64-bit AMD CPU.
elif [ "${platform}" == "linux" ] ; then
    py3bin="/usr/local/bin:${HOME}/.local/bin"
    #printf "Using Ubuntu Linux Python version path = ${PATH}\n"
elif [ "${platform}" == "cygwin" ] ; then
    py3bin="/usr/local/bin"
    #printf "Using Cygwin Linux Python version path = ${PATH}\n"
fi

if [ "${platform}" == "macos" ] ; then
    # Not quite the final path -- For macOS, add the path to brew and add export brew's environment variables.
    # To see help documentation on this, run
    #     /opt/homebrew/bin/brew -h shellenv
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# CMake tool used for Blender.
cmakebin="/Applications/CMake.app/Contents/bin/"

# Latest version of make and ack.
makebin="/usr/local/bin"

# Final path.
PATH="${HOME}:${makebin}:${cmakebin}:${py3bin}:${bins}:${PATH}"
#echo "Final path = ${PATH}"
export PATH

# Python paths for additional private library modules.  See
#     https://docs.python.org/3/using/cmdline.html#environment-variables
# Even inside a virtual environment, pip will search the PYTHONPATH.  So you may have clashes between module inside and outside
# the virtual environment if you aren't careful.  Look at the pip module locations using
#     pip list -v
export PYTHONPATH="${HOME}/Desktop/Sean/WebSite/private/python_library"

# On Ubuntu Linux, run the Python virtual environment.
if [ "${platform}" == "linux" ] ; then
    #echo "Linux: set up Python virtual environment for all terminal windows"
    if [[ -f ~/.VENV/bin/activate ]] ; then
        source ~/.VENV/bin/activate  # This was commented out by conda initialize
        echo "Entering `python3 -V` virtual environment at ${VIRTUAL_ENV}. Type deactivate to exit."
    else
        echo "WARNING:  No Python virtual environment on system.  Recommend you set one up."
    fi
fi

# Make sure Python 3 is installed on your system.  Get the version and redirect from stderr to stdout.
python_version=`python3 -V 2>&1`

# Delete minor versions (numbers after the first dot), and spaces, e.g. Python 3.13 => Python3
python_version_stripped=`echo ${python_version} | sed 's/\.[0-9]*//g' | sed 's/[ \r]//g'`

#echo "Python version ${python_version} was detected"
#echo "stripped version = ${python_version_stripped}"

# Check the version and give help.
if [ "${python_version_stripped}" != "Python3" ] ; then
    echo "WARNING:  Calling   o l d   python version ${python_version} stripped ${python_version_stripped} from `which python` in path $PATH"
fi

# Default settings.
ls_color_option="-G"
desk_dir="${HOME}/Desktop"
thumb_dir="/Volumes/ALNILAM"
extra_bin_path="/usr/local/bin"

#------------- Export base directories for use by other programs -------------

# The root directory has /Sean under it and /Sean/WebSite underneath that.
export desk_dir 
export thumb_dir

#echo "Root dir |${desk_dir}|, thumb dir |${thumb_dir}|, desk_dir |${desk_dir}|"

#------------- Directory Shorthands -------------

# Top level directories
sean_dir="${desk_dir}/Sean"
app_dir="${desk_dir}/App"
export sean_dir
export app_dir

# Level 1 directories.
arts_dir="${sean_dir}/Arts"
business_dir="${sean_dir}/Business"
family_dir="${sean_dir}/Family"
science_dir="${sean_dir}/Sciences"
web_dir="${sean_dir}/WebSite"
export arts_dir
export business_dir
export family_dir
export science_dir
export web_dir

# Quickly cd to subdirectories by typing cd subdir.
# Need . in the list to avoid having to put ./ in front of directories.
export CDPATH=.:~:${sean_dir}:${pp_src_dir}

# Mac system tweaks.
if [ "${platform}" == "macos" ] ; then
    if [ "${whentoexecute}" == "once" ] ; then
        # Show hidden files in finder (needs a relaunch of finder).
        defaults write com.apple.finder AppleShowAllFiles TRUE && killall Finder

        # Remove the Auto-Hide Dock Delay
        defaults write com.apple.Dock autohide-delay -float 0 && killall Dock

        # Speed Up Mission Control Animations
        defaults write com.apple.dock expose-animation-duration -float 0.12 && killall Dock

        # Make Hidden App Icons Translucent in the Dock
        defaults write com.apple.Dock showhidden -bool YES && killall Dock

        # Change Screen Shots image type from PNG to JPG
        defaults write com.apple.screencapture type jpg && killall SystemUIServer
    fi

    # XCode location.
    # Some apps like opendiff, launched from git difftool will need to know this.
    export DEVELOPER_DIR=/Applications/Xcode.app
fi

# Finish up the aliases.
source .bashrc
