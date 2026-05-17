#============================================================================= 
#
#  FILE NAME
#
#     .bash_logout
#
# DESCRIPTION
#
#     bash shell executed upon logout.
#     Install into your home directory ~.
#
#  DATE
#
#      24 Aug 24
#
#  AUTHOR
#
#      Sean Erik O'Connor
#
#============================================================================= 
#
# Clean up history.
#
rm -f ~/.bash_history
#rm -f ~/.viminfo

# Find out which operating system we are running on:  macOS, Linux, Windows/Cygwin, etc.
uname=`uname -s`
# We are running on Linux.  Tested on my Ubuntu Linux system running on my Cyperpower PC with a 64-bit AMD CPU.
if [ "${uname}" == "Linux" ] ; then
    # When leaving the console clear the screen to increase privacy.
    # See https://unix.stackexchange.com/questions/451069/why-is-there-a-call-to-clear-console-in-bash-logout
    # Do this by checking the level of subshell.
    if [ "$SHLVL" = 1 ]; then
        [ -x /usr/bin/clear_console ] && /usr/bin/clear_console -q
    fi
fi
