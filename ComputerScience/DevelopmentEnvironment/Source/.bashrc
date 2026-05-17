#----------------------------------------------------------------------------
#
#  TITLE
#
#      .bashrc
#
#  DESCRIPTION
#
#
#     Bourne Again Shell (bash) startup file for Unix systems.  Executed 
#     everytime we start a subshell.  Install into your home directory ~.
#     Put aliases and functions here.
#    
#     Use source .bashrc to reset the environment after you are in a
#     terminal window.  Place the line "source .bashrc" into .bash_profile
#     to execute this file's commands upon login.
#
#     To debug, use sh -x .bashrc
#
#  DATE
#
#      20 Jul 25
#
#  AUTHOR
#
#      Sean E. O'Connor
#
#----------------------------------------------------------------------------

#------------- Aliases ------------------------------------------------------
#
#   Be sure to put useful scripts and executables into the home bin directory, ~/bin or global /usr/local/bin
#

alias desk='cd ${desk_dir}'

alias app='cd ${app_dir}'

alias art='cd ${arts_dir}/Visual/Painting/OriginalWorks'
alias bus='cd ${business_dir}'
alias acc='cd ${business_dir}/Accounts'
alias fam='cd ${family_dir}'
alias lit='cd ${arts_dir}/Literature'
alias sci='cd ${science_dir}'
alias math='cd ${science_dir}/Mathematics'
alias comp='cd ${science_dir}/ComputerScience'
alias fuk='cd ${science_dir}/ComputerScience/ObsoleteSoftware/Fruit/MTWikiNew'

#------------- Git ------------------------------------------------

# Location of git repository.
export GITREPOS="${web_dir}/private/repos"

# These are all my git repositories.
alias weba='cd ${web_dir}/Art'
alias webcrc='cd ${web_dir}/CommunicationTheory/ChannelCoding/CyclicRedundancyCheckCodes'
alias webc='cd ${web_dir}/ComputerScience/DevelopmentEnvironment'
alias webfft='cd ${web_dir}/Mathematics/SignalProcessing/FastFourierTransform'
alias webf='cd ${web_dir}/Finance'
alias webl='cd ${web_dir}/ComputerScience/Automata/Life'
alias webp='cd ${web_dir}/ComputerScience/Compiler/ParserGeneratorAndParser'
alias webpp='cd ${web_dir}/Mathematics/AbstractAlgebra/PrimitivePolynomials'
alias webps='cd ${web_dir}/CommunicationTheory/PseudoNoiseSequences'
alias webu='cd ${web_dir}/private'
alias webd='cd ${web_dir}/WebPageDesign'
alias web='cd ${web_dir}'
alias webj='cd ${web_dir}/mathjax'

# Subdir of WebPageDesign git repo.
alias webm='cd ${web_dir}/WebPageDesign/MaintainWebPage'

# View the status of a git repository.
function gitshow()
{
    if [ $# == 0 ]
    then
        echo "Usage:  gitshow <git directory>"
    fi

    # Grab the function argument, bash style.
    gitdir=$1

    # Parent directory on my machine.
    parentDir=${HOME}/Desktop/Sean

    printf "\n\n"
    printf "${blueonyellow} git repository ${gitdir} ${resetcolor}\n"
    printf "\n\n"
    
    # Go into the git local snapshot.
    pushds ${parentDir}/${gitdir}

    # Pull the remote branch to get local snapshot up to date.
    printf "${redongreen}pulling:${resetcolor}\n\t"
    git pull

    # Clean and recurse into directories.  Don't babble the status.
    git clean -f -d --quiet

    # Collect garbage.  Don't babble the status.
    git gc --quiet

    # Show the branches, status, stash lists, most recent commit.
    printf "${redongreen}branches:${resetcolor}\n\t"
    git branch

    printf "${redongreen}status:${resetcolor}\n\t"
    git status

    printf "${redongreen}stashes:${resetcolor}\n\t"
    git stash list
    printf "\n"

    printf "${redongreen}last commit${resetcolor}:\n\t"
    git log -1 --name-only
    printf "${redongreen}---${resetcolor}\n\n"
    popds
}

# View all my Git repositories.
function gita()
{
    # How did I find them all on my system?
    #     find . -name '*.git' 

    # Ascii terminal colors.   Example: printf "\u1b[31;42mRedOnGreen\u1b[0mNormal"
    redongreen="\u1b[31;42m"
    redonblue="\u1b[31;44m"
    blueonyellow="\u1b[34;43m"
    whiteonblue="\u1b[37;44m"
    resetcolor="\u1b[0m"

    clear

    # Show each repository and its status.
    gitshow WebSite;                                                                                    continueOrQuit ; if [ $? == 1 ] ; then return ; else clear ; fi
    gitshow WebSite/Art ;                                                                               continueOrQuit ; if [ $? == 1 ] ; then return ; else clear ; fi
    gitshow WebSite/CommunicationTheory/ChannelCoding/CyclicRedundancyCheckCodes;                       continueOrQuit ; if [ $? == 1 ] ; then return ; else clear ; fi
    gitshow WebSite/CommunicationTheory/PseudoNoiseSequences;                                           continueOrQuit ; if [ $? == 1 ] ; then return ; else clear ; fi
    gitshow WebSite/ComputerScience/DevelopmentEnvironment;                                             continueOrQuit ; if [ $? == 1 ] ; then return ; else clear ; fi
    gitshow WebSite/Mathematics/SignalProcessing/FastFourierTransform;                                  continueOrQuit ; if [ $? == 1 ] ; then return ; else clear ; fi
    gitshow WebSite/Finance;                                                                            continueOrQuit ; if [ $? == 1 ] ; then return ; else clear ; fi
    gitshow WebSite/ComputerScience/Automata/Life;                                                      continueOrQuit ; if [ $? == 1 ] ; then return ; else clear ; fi
    gitshow WebSite/ComputerScience/Compiler/ParserGeneratorAndParser;                                  continueOrQuit ; if [ $? == 1 ] ; then return ; else clear ; fi
    gitshow WebSite/Mathematics/AbstractAlgebra/PrimitivePolynomials;                                   continueOrQuit ; if [ $? == 1 ] ; then return ; else clear ; fi
    gitshow WebSite/private;                                                                            continueOrQuit ; if [ $? == 1 ] ; then return ; else clear ; fi
    gitshow WebSite/WebPageDesign;                                                                      continueOrQuit ; if [ $? == 1 ] ; then return ; else clear ; fi
}


#------------- Blender ------------------------------------------------

# Developer version compiled from source.
alias blender='/Users/seanoconnor/blender-git/build_darwin/bin/Blender.app/Contents/MacOS/Blender'

#------------- Set prompt ---------------------------------------------
#
# Define colors for the text in a prompt.
#
startcolor="\[\e["
black="30"
red="31"
green="32"
yellow="33"
blue="34"
magenta="35"
teal="36"
white="37"
separator=";"
blackbackground="40"
redbackground="41"
greenbackground="42"
yellowbackground="43"
bluebackground="44"
magentabackground="45"
tealbackground="46"
whitebackground="47"
reset="0"
boldtext="1"
underline="4"
blink="5"
inverted="7"
endcolor="m\]"
resetcolor="\e[0m"
whiteonblue="${startcolor}${white}${separator}${bluebackground}${endcolor}"
redonblue="${startcolor}${red}${separator}${bluebackground}${endcolor}"

# Set the prompt to
# time \@, date \d, user name \u, host name \h, current directory \w
# \W basename of current directory, \$ if UID = 0 (root), use # instead of $
export PS1="${redonblue}\u:${whiteonblue}\w${resetcolor}\$ "
###echo ${PS1}


#------------- Shell options ------------------------------------------------
#
# Set vi edit mode for the command line.
# Hit <ESC> to go into vi's edit command mode:
#   h   Move cursor left
#   l   Move cursor right
#   A   Move cursor to end of line and put in insert mode
#   0   (zero) Move cursor to beginning of line (doesn't put in insert mode)
#   i   Put into insert mode at current position
#   a   Put into insert mode after current position
#   dd  Delete line (saved for pasting)
#   D   Delete text after current cursor position (saved for pasting)
#   p   Paste text that was deleted
#   j   Move up through history commands
#   k   Move down through history commands
#   u   Undo
set -o vi

# Don't wait for job termination notification
set -o notify

# Don't use ^D to exit
set -o ignoreeof

# Use case-insensitive filename globbing
shopt -s nocaseglob

# Make bash append rather than overwrite the history on disk
shopt -s histappend

# When changing directory small typos can be ignored by bash
# for example, cd /vr/lgo/apaache would find /var/log/apache
shopt -s cdspell

shopt -s cdable_vars

#------------- Completion options ------------------------------------------------
#
# These completion tuning parameters change the
# default behavior of bash_completion:

# Define to avoid stripping description in --option=description of './configure --help'
COMP_CONFIGURE_HINTS=1

# Define to avoid flattening internal contents of tar files
COMP_TAR_INTERNAL_PATHS=1

# If this shell is interactive, turn on programmable completion enhancements.
# Any completions you add in ~/.bash_completion are sourced last.
case $- in
  *i*) [[ -f /etc/bash_completion ]] && . /etc/bash_completion ;;
esac


#------------- History options ------------------------------------------------
#
# Don't put duplicate lines in the history.
export HISTCONTROL="ignoredups"

# Ignore some controlling instructions
export HISTIGNORE="ls:ls *:[   ]*:&:cd:cd ..:exit:hi:s:f:m:um"

# Whenever displaying the prompt, write the previous line to disk
export PROMPT_COMMAND="history -a"


#------------- Aliases ------------------------------------------------
#
#   If these are enabled they will be used instead of any instructions
#   they may mask.  For example, alias rm='rm -i' will mask the rm
#   application.
#
#   To override the alias instruction use a \ before, ie
#   \rm will call the real rm not the alias.
#
#   To see all aliases, type alias.
#   Use unalias to remove a definition.

# Interactive operation...
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias up='cd ..'

# Default to human readable figures
alias df='df -h'
alias du='du -hac'

# Misc :)
alias less='less -r'                          # raw control characters
alias whence='type -a'                        # where, of a sort
alias grep='grep --color'                     # show differences in colour
alias hi=history

# Some shortcuts for different directory listings
alias ls='ls -hF ${ls_color_option}'
alias dir='ls --color=auto --format=vertical'
alias ll='ls -l'                              # long list
alias la='ls -A'                              # all but . and ..
alias l='ls -CF'                              #


#------------- Utility functions ------------------------------------------------

# Push and pop directory without error messages.
function pushds
{
    command pushd "$1" > /dev/null
}

function popds
{
    command popd "$1" > /dev/null
}

# Recursive search for a string in a file.
function grepall()
{
    if [ $# == 0 ]
    then
        echo "Usage:  grepall <string>"
    fi

    # Grab the function argument, bash style.
    pat=$1

    echo "Searching all subdirectories for pattern ${pat}"

    find . -name '*.[ch]'   -exec grep -iH "${pat}" {} ';'
    find . -name '*.hpp'    -exec grep -iH "${pat}" {} ';'
    find . -name '*.cpp'    -exec grep -iH "${pat}" {} ';'
    find . -name '*.py'     -exec grep -iH "${pat}" {} ';'
    find . -name '*.lsp'    -exec grep -iH "${pat}" {} ';'
    find . -name '*.m'      -exec grep -iH "${pat}" {} ';'
    find . -name '*.js'     -exec grep -iH "${pat}" {} ';'
    find . -name '*.java'   -exec grep -iH "${pat}" {} ';'
    find . -name '*.pl'     -exec grep -iH "${pat}" {} ';'
    find . -name '*.prl'    -exec grep -iH "${pat}" {} ';'
    find . -name '*.html'   -exec grep -iH "${pat}" {} ';'
    find . -name '*.css'    -exec grep -iH "${pat}" {} ';'
    find . -name 'makefile' -exec grep -iH "${pat}" {} ';'
    find . -name '*.dat'    -exec grep -iH "${pat}" {} ';'
    find . -name '*.txt'    -exec grep -iH "${pat}" {} ';'
}

function touchall()
{
    find . -exec touch {} ';'
}

function testOptions()
{
    if [ $# == 0 ]
    then
        echo "Number of arguments to testOptions is $#"
    fi

    # No spaces around the equals allowed in bash!
    a1=$1

    echo "You said |${a1}|"

    # Compare the first 3 letters.
    if [ "${a1:0:3}" == "tes" ]
    then
        echo "You said testOptions tes"
    else
        echo "What did you say?"
    fi
}

# Launch gvim editor.
function gvim()
{
    # No file name given?
    if [ $# == 0 ]
    then
        # Remove the old file.
        fileName="${HOME}/temp.txt"
        if [ -f "${fileName}" ] ; then
            echo "Removing file ${fileName}"
            rm -rf ${fileName}
        fi

        # Remove any swap file.
        fileNameSwap="${HOME}.vim/.swp/temp.txt.swp"
        if [ -f "${fileNameSwap}" ] ; then
            echo "Removing swap file ${fileNameSwap}"
            rm -rf ${fileNameSwap}
        fi

        # Create a new file.
        echo -n > ${fileName}
        echo "Opening temporary file ${fileName}"
    else
        fileName=$1
    fi

    # Find out which operating system we are running on:  macOS, Linux, Windows/Cygwin, etc.
    uname=`uname -s`

    # macOS.  Tested on my MacBook Pro laptop mid-2015 model with Intel x86_64 architecture.
    if [ "${uname}" == "Darwin" ] ; then
        platform="macos"
    # Linux.  Tested on my Ubuntu Linux system running on my Cyperpower PC with a 64-bit AMD CPU.
    elif [ "${uname}" == "Linux" ] ; then
        platform="linux"
    # Cygwin.  For cygwin 2.2 64-bit on Windows 10 64-bit.  Not tested.  From https://en.wikipedia.org/wiki/Uname
    elif [ "${uname}" == "CYGWIN_NT-10.0" ] ; then
        platform="cygwin"
    fi
    #echo "Using platform = ${platform}"

    # Launch GUI Vim on my macOS machine.
    if [ "${platform}" == "macos" ] ; then
        open -a MacVim "${fileName}"
    # Launch GUI Vim on my Ubuntu Linux machines.
    elif [ "${platform}" == "linux" ] ; then
        /usr/bin/vim "${fileName}"
    # Cygwin
    elif [ "${platform}" == "cygwin" ] ; then
        /usr/bin/vim "${fileName}"
    else
        echo "Could not get a platform.  Guessing Linux."
        /usr/bin/vim "${fileName}"
    fi
}

# Remove temporary files.
function cleanall()
{
    if [ $# != 0 ]
    then
        echo "Usage:  cleanall"
    fi

    find . -name '*~'          -print -exec rm -f {} \;
    find . -name '._*'         -print -exec rm -f {} \;
    find . -name '.DS_Store*'  -print -exec rm -f {} \;
    find . -name 'Thumbs.db'   -print -exec rm -f {} \;
    find . -name '*.swp'       -print -exec rm -f {} \;
    find . -name '*.o'         -print -exec rm -f {} \;
    find . -name '*.class'     -print -exec rm -f {} \;
    find . -name '*.o~$'       -print -exec rm -f {} \;
    find . -name '*.o~>'       -print -exec rm -f {} \;
    find . -name '*.dSYM'      -print -exec rm -rf {} \;
    find . -name '*.obj'       -print -exec rm -rf {} \;
    find . -name '*.ncb'       -print -exec rm -rf {} \;
    find . -name '*.suo'       -print -exec rm -rf {} \;
    find . -name '*.idb'       -print -exec rm -rf {} \;
    find . -name '*.pdb'       -print -exec rm -rf {} \;
    find . -name '*.manifest'  -print -exec rm -rf {} \;
    find . -name '*.Spotlight-V100'  -print -exec rm -rf {} \;
    find . -name '*.Trash*'          -print -exec rm -rf {} \;
    find . -name '*.fseventsd'       -print -exec rm -rf {} \;
}

# Return status 0 if we hit the SPACE BAR or 1 if we hit q for QUIT.
function continueOrQuit()
{
    # See https://www.computerhope.com/unix/bash/read.htm
    #  -n1   Read only one character.
    #   -s   Don't echo keystrokes.
    #   -r   Raw input.  read backslashes and don't interpret them as escape characters.
    #   -p   Print the string prompt first before reading the line.
    read -n1 -s -r -p $'Press space to continue or q to quit...\n' key
    if [ "$key" = ' ' ]; then
        return 0
    elif [ "$key" = 'q' ]; then
        return 1
    fi
    printf "\n\n"
}
