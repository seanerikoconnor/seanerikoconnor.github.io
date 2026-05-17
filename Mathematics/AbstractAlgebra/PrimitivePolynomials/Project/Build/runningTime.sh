#!/bin/bash
#============================================================================
#
# NAME
#
#     runningTime.sh
#
# DESCRIPTION
#
#     Measure primitive polynomial running time.
#
# USAGE
#
#     Collect data using
#
#         ./runningTime.sh
#
#     Plot the times using the script
#
#         ./plotRunningTime.sh
#
# NOTES
#
#     numpy:                            http://www.numpy.org
#     matplotlib                        https://matplotlib.org
#     Python interpreter:               http://www.python.org
#     Python tutorial and reference:    htttp://docs.python.org/lib/lib.html
#
# LEGAL
#
#     Primpoly Version 16.4 - A Program for Computing Primitive Polynomials.
#     Copyright (C) 1999-2026 by Sean Erik O'Connor.  All Rights Reserved.
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
#     with the !DOT! replaced by . and the !AT! replaced by @
#
#============================================================================

# ----------------------------------------
# Collect timing results for Primpoly
# ----------------------------------------

function TimePrimpoly()
{
    time ${PRIMPOLYEXE} 2   2
    time ${PRIMPOLYEXE} 2  10
    time ${PRIMPOLYEXE} 2  30
    time ${PRIMPOLYEXE} 2  50
    time ${PRIMPOLYEXE} 2  70
    time ${PRIMPOLYEXE} 2  90
    time ${PRIMPOLYEXE} 2 100
    time ${PRIMPOLYEXE} 2 120
    time ${PRIMPOLYEXE} 2 140
    time ${PRIMPOLYEXE} 2 145
    time ${PRIMPOLYEXE} 2 150
    time ${PRIMPOLYEXE} 2 160
    time ${PRIMPOLYEXE} 2 180
    time ${PRIMPOLYEXE} 2 200
    time ${PRIMPOLYEXE} 2 202
    time ${PRIMPOLYEXE} 2 210
    time ${PRIMPOLYEXE} 2 300
}

function TimeExe()
{
    PRIMPOLYEXE="Bin/Primpoly.exe"

    if [ -f ${PRIMPOLYEXE} ] ; then
        TimePrimpoly
    else
        echo "File ${PRIMPOLYEXE} not found"
        exit 1
    fi
}

# Actually run the timing.
TimeExe
