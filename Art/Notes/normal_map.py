#!/usr/bin/env python3

# Import system libraries.

import os    # Operating system support.
import sys   # read/write I/O
import math  # Math library
import numpy as np  # NumPy array library.
import matplotlib.pyplot as plt  # MatPlot library plotting

geometric_normal_color = np.array((128, 128, 255))
shading_normal_color   = np.array((157, 105, 250))

def color_to_normal( color ):
    offset = 128 * np.array((1, 1, 1))
    scale = 128
    return (color -offset) / scale

def angle( n1, n2 ):
    return math.acos( np.dot( n1, n2 ) ) * 180.0 / math.pi

n1 = color_to_normal( geometric_normal_color )
n2 = color_to_normal( shading_normal_color )

print( f"geometric normal = {np.array2string( n1, precision=2, floatmode='fixed' )} \n\tcolor = {np.array2string( geometric_normal_color)}" )
print( f"shading_normal   = {np.array2string( n2, precision=2, floatmode='fixed' )} \n\tcolor = {np.array2string( shading_normal_color)}" )
print( f"angle            = {angle(n1, n2):8.2f}" )


# Main program.
# But you can run on the unit test on the command line or in PyCharm IDE for debugging.
if __name__ == '__main__':
    """Python executes all code in the file, so all classes and functions get defined first.  Finally we come here.  
    If we are executing this file as a Python script, the name of the current module is set to main,
    thus we'll call the main() function.

    Just a stub here.
    """

