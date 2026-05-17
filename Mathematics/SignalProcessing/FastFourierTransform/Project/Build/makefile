#========================================================================
#
# NAME
# 
#     makefile
#
# DESCRIPTION
# 
#     Makefile for UNIX systems and Windows + Cygwin for compiling 
#     and testing CRCDemo.
#
#     Run from a command window by calling
#
#         make
#
#     To compile and test the program, type
#
#         make test
#
#
#  LEGAL
#
#     FFT Version 1.6 -  An FFT utility library in C++.
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
#=============================================================================

# Put this pseudo-target first so make without command line options executes it.
all: makeAllExes


#============================== Configuration ================================

# Find out which operating system we are running on:  macOS, Linux, etc.
UNAME := $(shell uname -s)

# macOS.  Tested on my MacBook Pro laptop mid-2015 model with Intel x86_64 architecture, also my MacBook Pro 2021 M1 Max ARM CPU.
ifeq ($(UNAME), Darwin)
PLATFORM = mac
endif

# Linux.  Tested on my Ubuntu Linux system running on my Cyperpower PC with a 64-bit AMD CPU.
ifeq ($(UNAME), Linux)
PLATFORM = linux
endif

# Cygwin.  For cygwin 2.2 64-bit on Windows 10 64-bit.  Not tested.  From https://en.wikipedia.org/wiki/Uname
ifeq ($(UNAME), CYGWIN_NT-10.0)
PLATFORM = cygwin
endif

# Default platform is macOS
ifndef PLATFORM
PLATFORM = mac
endif


#============================== Compiler, Linker, and CPU architecture =======================

# Type of compiler to use.
# Mac uses the clang C++/C compiler, same as XCode.
ifeq ($(PLATFORM), mac)
CPP     = clang++
CPPLINK = clang++
CC      = clang++ -x c
CCLINK  = clang 
# Ubuntu Linux uses the gcc C++/C compiler.
else ifeq ($(PLATFORM), linux)
CPP     = g++
CPPLINK = g++
CC      = gcc -x c
CCLINK  = gcc
# Windows uses the GNU C++/C compiler.
else ifeq ($(PLATFORM), cygwin)
CPP     = g++
CPPLINK = g++
CC      = gcc
CCLINK  = gcc
endif

# Architecture (CPU type).
ifeq ($(PLATFORM), mac)
# The new MacBook Pro uses Apple Silicon CPU based on ARM.  
ARCH = -arch arm64
# If you specify x86 architecture, the executable will still run due to Apple's Rosetta 2 Intel to ARM code translation, 
# but much more slowly than if you use the native CPU architecture.
#ARCH = -arch x86_64
else ifeq ($(PLATFORM), linux)
ARCH = 
else ifeq ($(PLATFORM), cygwin)
ARCH =
endif



#============================== Compiler and Linker Settings, Libraries =======================

# Compile the C++20 standard and its libraries.
ifeq ($(PLATFORM), cygwin)
CPP_OPTIONS = -std=c++20
CPP_LIBS = -L"/usr/lib" 
C_OPTIONS =
C_LIBS = -L"/usr/lib" 
else ifeq ($(PLATFORM), mac)
CPP_OPTIONS = -std=c++20 -stdlib=libc++
C_OPTIONS =
CPP_LIBS = 
C_LIBS =
else ifeq ($(PLATFORM), linux)
CPP_OPTIONS = -std=c++20 -D USE_EXPERIMENTAL_FILESYSTEM_GNU_CPP
C_OPTIONS =
CPP_LIBS = -lm -lstdc++fs 
C_LIBS = -lm -lstdc++fs
endif

# Link flags.
ifeq ($(PLATFORM), mac)
LFLAGS = $(ARCH)
else ifeq ($(PLATFORM), linux)
LFLAGS =
endif

#============================== Optimization =======================

# Select on = optimized code for speed.  off = compile for debugging
OPTIMIZATION = on

# Use the highest optimization level unless weird stuff happens.
ifeq ($(OPTIMIZATION), on)
CPP_DEBUG_FLAGS = -O3
else
CPP_DEBUG_FLAGS = -g3
endif


#============================== ALL Compile and Link Flags =======================

# Gather all C++ and C flags together.
CPP_FLAGS = $(ARCH) $(CPP_DEBUG_FLAGS) $(CPP_INC) $(CPP_OPTIONS)
C_FLAGS   = $(ARCH) $(C_DEBUG_FLAGS)   $(C_INC) $) $(C_OPTIONS)


#============================== Root directories =============================

# Source file root directories.
CPP_SRC_DIR	= ../SourceCode

# Object file root directories.
CPP_OBJ_DIR 	= Bin

# Executable file root directories.
CPP_BIN_DIR		= Bin


#============================== Include Files =======================

# Include files.
ifeq ($(PLATFORM), cygwin)
CPP_INC = -I /usr/include -I "/usr/lib/gcc/x86_64-pc-cygwin/4.9.2/include/c++"
endif


#============================== List of Files ================================

# Object files.
CPP_OBJ  		= $(CPP_OBJ_DIR)/FFT.o

# Main program object files.
CPP_OBJ_MAIN 	= $(CPP_OBJ_DIR)/testFFT.o

# Main program executables.
CPP_BIN_MAIN		= $(CPP_BIN_DIR)/testFFT.exe


#============================== Implicit Rules ===============================

# Link all object files to executables.
$(CPP_BIN_MAIN): $(CPP_OBJ_MAIN) $(CPP_OBJ)
	$(CPPLINK) $(LFLAGS) $(CPP_OBJ_MAIN) $(CPP_OBJ) -o $(CPP_BIN_MAIN) $(CPP_LIBS)

# C++ and C source file compilation to object files.
$(CPP_BIN_DIR)/%.o : $(CPP_SRC_DIR)/%.cpp
	$(CPP) -c $(CPP_FLAGS) $< -o $@

# List of all file.o : file.h dependencies.
FFT.o: FFT.cpp fft.h
testFFT.o: testFFT.cpp fft.h


#============================== Targets ======================================

# Make all the executables.
makeAllExes: $(CPP_BIN_MAIN)

# Run tests.
test: $(CPP_BIN_MAIN)
	echo "Testing FFT.  Return status = 1 because test throws an exception, but ignore it."
	-$(CPP_BIN_MAIN) fftIn.txt fftOut.txt
	@echo "Comparing output to MacBook results [you should see no differences]"
	@diff fftOut.txt fftOut-macOS-ARM-M1max-clang.txt
	@echo "Done"
	@echo "Comparing output to Ubuntu results [you should see no differences]"
	@diff fftOut.txt fftOut-UbuntuLinux-AMD-x86_64-gcc.txt
	@echo "Done"

# Remove all C and C++ object files and binaries and output files.
#     - in front of the tells make to ignore a non-zero return code from a shell command.  So we don't stop if any files are missing.
#     @ in front of the shell command line prevents it from being printed to the console as make runs.
clean:
	-@echo "Cleaning up object files and executables"
	-rm fftOut.txt
	-rm $(CPP_OBJ) $(CPP_OBJ_MAIN) $(CPP_BIN_MAIN) 
