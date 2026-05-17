#!/usr/bin/env python3
# ^shebang:  load the correct Python interpreter and environment.
#============================================================================
#
# NAME
#
#     PrimpolyRunningTimeAnalysis.py
#
# DESCRIPTION
#
#     Primitive polynomial running time plots in Python using Sympy and Numpy.
#
# USAGE
#
#     Better to run this from the Jupyter notebook:
#
#         jupyter lab PrimpolyRunningTimeAnalysis.ipynb
#
#     But you could also run it directly using Python:
#
#         chmod +x PrimpolyRunningTimeAnalysis.py
#         ./PrimpolyRunningTimeAnalysis.py
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

import os   # Path 
import sys  # argc, argv, read/write I/O
import platform # platform, uname
import re  # Regular expression support
import math
import numpy as np
import pylab as py
import subprocess
import pickle                  # Python's own data file format.
from deepdiff import DeepDiff  # Deep difference for complicated data structures.

def write_to_pickle_file( data, file_name ):
    """Write data to a pickle file."""
    try:
        with open(file_name, 'wb') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

        if not os.path.exists( file_name ):
            print( f"ERROR:  Problem writing to {file_name} file doesn't exist." )
            return None

    except Exception as detail:
        print( "ERROR:  Problem writing to file {file_name}  Caught RuntimeError exception; detail = {detail}")
        return None


def read_from_pickle_file( file_name ):
    """Read data from a pickle file."""

    if not os.path.exists( file_name ):
        print( f"ERROR:  {file_name} does not exist" )
        return None
    try: 
        with open( file_name, 'rb') as f:
            data = pickle.load(f)
    except Exception as detail:
        print( "ERROR:  Problem reading file {file_name} Caught RuntimeError exception; detail = {detail}")
        return None

    return data
    
def data_differences( data1, data2 ):
    """Return the differences between to dictionaries."""

    changes = DeepDiff(data1, data2)
    return changes


def get_float_pattern():
    """Generate a regular expression which matches floating point numbers.

    Regular expressions format for Python is referenced here:  https://docs.python.org/3/howto/regex.html

    From [how to extract floating number from string](https://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string)
    Some people, when confronted with a problem, think 'I know, I'll use regular expressions.'  Now they have two problems.
         -Jamie Zawinski <jwz@netscape.com> wrote on Tue, 12 Aug 1997 13:16:22 -0700:
     """

    float_pattern = r"""
            [-+]?                       # Optional sign:   + or - or nothing
            (?:
                (?: \d* \. \d+)         # .1 .12, 1.2 1.23
                |
                (?: \d+ \.?)            # 1. 12. 1 12
            )
            (?: [Ee] [+-]? \d+ )?       # Optional exponent:  e1 e-2
            """

    return float_pattern


def parse_primpoly_timing_output(line_of_file, **kwargs):
    """
    Parse the output of the command
        time Primipoly p n 
    to get the running time.
    """

    real_time = None 

    # kwargs is a dictionary.
    for key, value in kwargs.items():
        if key in kwargs:
            print( f"key = {key} value = {value}" )

    debug = False
    debug_value = kwargs.get("debug")
    if debug_value is not None and debug_value is True:
        debug = True

    if line_of_file is None or len(line_of_file) == 0:
        return None

    #first_char = line_of_file[0]
    # print("first char = ", first_char)

    # Don't forget to backslash the vertical bar:  \| since we want to match this char.
    # Match all spaces with \s+ even those within a line.
    # Tremendous speedup if we check the first char in the line before applying regular expressions.
    #if first_char == 'X':
    pattern1 = fr"""
                  real
                  \s+
                  (?P<real_time>
                      {get_float_pattern()}
                  )
               """

    pattern2 = fr"""
                real
                \s+
                (?P<real_time>
                    {get_float_pattern()}
                )
               """
    if debug:
        print(f"pattern1 = {pattern1}")
        print(f"pattern2 = {pattern2}")
        print(f"line of file =\n|{line_of_file}|")

    p1 = re.compile(pattern1, re.VERBOSE | re.IGNORECASE)
    p2 = re.compile(pattern2, re.VERBOSE | re.IGNORECASE)

    # Try both matches.
    m1 = p1.search(line_of_file)
    m2 = p2.search(line_of_file)

    if m1:
        real_time = float(m1.group('real_time'))
        if debug:
            print( "Match pattern 1. real_time = {real_time}")
    elif m2:
        real_time = float(m2.group('real_time'))
        if debug:
            print( "Match pattern 2. real_time = {real_time}")

    return real_time


def time_primpoly(**kwargs):

    # kwargs is a dictionary.
    for key, value in kwargs.items():
        if key in kwargs:
            print( f"key = {key} value = {value}" )

    # Enable debugging?
    debug = False
    debug_value = kwargs.get("debug")
    if debug_value is not None and debug_value is True:
        debug = True

    # All the degrees we wish to test.
    degrees = [   2,  10,  30, 50, 70, 90, 100, 120, 140, 145, 150, 160, 180, 200, 202, 210, 300, 400, 500, 550 ]
    times   = []

    p = 2
    for n in degrees:
        # Run time Primpoly and collect the outputs.
        print( f"Primpoly p = {p} n = {n}", file=sys.stderr )
        
        standard_output = None
        standard_error = None

        # Set up the executable and the arguments for Linux.  Try that first.
        executableFileName="Bin/Primpoly.exe"
        timeCommand="/usr/bin/time" 
        timeOptions = "-f 'real %e'"  # %e is Wall clock time in seconds
        completed_process=subprocess.run([timeCommand, timeOptions, executableFileName, str(p), str(n)], capture_output=True)
        if completed_process.returncode == 0:
            standard_output = completed_process.stdout.decode("utf-8")
            standard_error = completed_process.stderr.decode("utf-8")
        else:
            if debug:
                print("Could not run Linux version of time Primpoly.  Running macOS version of time Primpoly")
            # Didn't work?  Set up the executable and the arguments for macOS.  Try that next.
            executableFile="Bin/Primpoly.exe"
            timeCommand="time"
            completed_process=subprocess.run([timeCommand, executableFileName, str(p), str(n)], capture_output=True)
            if completed_process.returncode == 0:
                standard_output = completed_process.stdout.decode("utf-8")
                standard_error = completed_process.stderr.decode("utf-8")
            # Still didn't work?  Then abort.
            else:
                print( "ERROR:  Could not run time command on the Primpoly executable.  Did you build it with make?  Aborting..." )
                return None

        if debug:
            for line in standard_output.split('\n'):
                print( f">>> {line}" )
            for line in standard_error.split('\n'):
                print( f"!!! {line}" )

        # Parse the results to get the running time.
        running_time_sec = parse_primpoly_timing_output(standard_error)
        if running_time_sec is None:
            print( "ERROR:  Could not parse the running time.  Aborting..." )
            return None
        else:
            print( f"\trunning time = {running_time_sec}", file=sys.stderr )
            
        times.append( running_time_sec )
   
    return degrees, times


def plot_running_times( file_name, **kwargs ):
    """Plot the running times"""

    debug = False
    debug_value = kwargs.get("debug")
    if debug_value is not None and debug_value is True:
        debug = True

    if (timing_data := read_from_pickle_file( file_name )) == None:
        print( f"ERROR:  No data in the running times file or no file {file_name}")
        return
    elif debug:
        print( f"timing data (computer name, degrees and times = \n\t{timing_data}" )

    try:
        py.figure('Primpoly Running Time', figsize=(20,10))
        py.title('Running Time vs Degree for Mod 2 Primitive Polynomials') 
        py.xlabel('Polynomial Degree') 
        py.ylabel('Running Time, Seconds') 
        py.semilogy()

        legends = []
        for computer_name, degrees_and_times in timing_data.items():
            degrees, times = degrees_and_times
            if debug:
                print(f"degrees = {degrees}")
                print(f"times   = {times}")
                print(f"name    = {computer_name}")
            
            py.plot( degrees, times )
            legends.append( computer_name )

        py.legend(legends)
        py.show()
        return
    except Exception as err:
        print( f"ERROR:  Plotting went haywire for file {file_name}.  Caught a general Exception {err}" )
        return

def compute_running_time_and_record(file_name): 
    """Time my primitive polynomial program and record the times."""

    # Do we have any previously recorded timing data?  If not, create an empty dictionary for it.
    if (timing_data := read_from_pickle_file( file_name )) == None:
        timing_data = {}

    # Find out which type of computer system we are running on.
    if platform.uname().system == 'Darwin' and platform.uname().machine == 'arm64' and platform.uname().processor == 'arm':
        computer_name = "MacBook Pro 2021 Apple M1 Max macOS"
    elif platform.uname().system == 'Linux' and platform.uname().machine == 'x86_64' and platform.uname().processor == 'x86_64':
        computer_name = "CyberPowerPC Model C Series AMD Intel Ubuntu/Linux 22.04 LTS Jammy Jellyfish"
    else:
        computer_name = None
        print( f"ERROR:  unknown computer type" )
        return

    # Run the timing analysis.
    degrees, times = time_primpoly()

    if computer_name not in timing_data:
        # If we don't yet have data for this computer, create a new dictionary entry.
        timing_data[ computer_name ] = [degrees, times]
    else:
        # Else overwrite the old timing data.
        timing_data[ computer_name ] = [degrees, times]

    # Record to file.
    write_to_pickle_file( timing_data, file_name )

#    timing_data_results = read_from_pickle_file( file_name )
#    diff = data_differences( timing_data, timing_data_results )
#    if diff is None or len(diff) == 0:
#        print( "no differences" )


def update_running_times_and_plot_all():
    """Read the running time from file and plot it"""

    print( "Running Python Version {0:d}.{1:d}.{2:d}".format( sys.version_info[ 0 ], sys.version_info[ 1 ], sys.version_info[ 2 ] ) )

    file_name = "primpoly_running_time.pickle"

    # Compute running time on this system and record to file.
    compute_running_time_and_record(file_name)

    # Plot all running times so far recorded.
    plot_running_times(file_name)

if __name__ == '__main__':
    """ If you run this as a standalone program:
             chmod +x PrimpolyRunningTimeAnalysis.py
             ./PrimpolyRunningTimeAnalysis.py
    """

    update_running_times_and_plot_all()
