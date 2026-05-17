SHELL := /bin/bash # Call shell from /usr/bin/sh instead of /bin/sh. Need this so that commands pushd and popd will be found.
#========================================================================
#
# NAME
# 
#     makefile
#
# DESCRIPTION
# 
#     Makefile for MAC OS, Ubuntu Linux Unix systems and 
#     Windows/Cygwin for compiling and testing Primpoly.
#
#     Build the executables by running
#
#         make
#
#     To clean up executables, object files, and archives run
#
#         make clean
#
#     To run regression tests do
#
#         make test
#
#     To create an archive bundle of source code
#
#         make archive
#
#  LEGAL
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
# You can put debug print code here if you wish.
ifeq ($(OPTIMIZATION), on)
CPP_DEBUG_FLAGS = -O3
C_DEBUG_FLAGS = -O3
# Turn off optimization.  Turn on ALL debug print code.  
# You can do this also from source in Primpoly.hpp
else
CPP_DEBUG_FLAGS = -g3 \
	-D DEBUG_PP_PRIMITIVITY \
	-D DEBUG_PP_SLOW_PRIMITIVITY_CHECK \
	-D DEBUG_PP_POLYNOMIAL \
	-D DEBUG_PP_PARSER \
	-D DEBUG_PP_PRIMALITY_TESTING \
	-D DEBUG_PP_FACTOR \
	-D DEBUG_PP_ARITH \
	-D DEBUG_PP_BIGINT \
	-D DEBUG_PP_FORCE_UNIT_TEST_FAIL
#-D DEBUG_PP_FORCE_MEMORY_OVERLOAD
C_DEBUG_FLAGS = -g3 \
	-D DEBUG_PP_PRIMPOLY
endif


#============================== ALL Compile and Link Flags =======================

# Gather all C++ and C flags together.
CPP_FLAGS = $(ARCH) $(CPP_DEBUG_FLAGS) $(CPP_INC) $(CPP_OPTIONS)
C_FLAGS   = $(ARCH) $(C_DEBUG_FLAGS)   $(C_INC) $) $(C_OPTIONS)



#============================== Root directories =============================

# Source file root directories.
CPP_SRC_DIR = ../SourceCode/Primpoly
C_SRC_DIR   = ../SourceCode/PrimpolyC

# Object file root directories.
CPP_OBJ_DIR = Bin
C_OBJ_DIR   = BinC

# Executable file root directories.
CPP_BIN_DIR = Bin
C_BIN_DIR   = BinC


#============================== Include Files =======================

# Include files.
ifeq ($(PLATFORM), cygwin)
CPP_INC = -I /usr/include -I "/usr/lib/gcc/x86_64-pc-cygwin/4.9.2/include/c++"
C_INC   = -I /usr/include -I "/usr/lib/gcc/x86_64-pc-cygwin/4.9.2/include"
endif


#============================== List of Files ================================

# Object files.
CPP_OBJ =		$(CPP_OBJ_DIR)/ppArith.o \
				$(CPP_OBJ_DIR)/ppBigInt.o \
				$(CPP_OBJ_DIR)/ppOperationCount.o \
				$(CPP_OBJ_DIR)/ppFactor.o \
				$(CPP_OBJ_DIR)/ppParser.o \
				$(CPP_OBJ_DIR)/ppPolynomial.o \
				$(CPP_OBJ_DIR)/ppUnitTest.o

C_OBJ = 		$(C_OBJ_DIR)/ppArith.o \
				$(C_OBJ_DIR)/ppFactor.o \
				$(C_OBJ_DIR)/ppHelperFunc.o \
				$(C_OBJ_DIR)/ppIO.o \
				$(C_OBJ_DIR)/ppOrder.o \
				$(C_OBJ_DIR)/ppPolyArith.o

# Main program object files.
CPP_OBJ_MAIN = $(CPP_OBJ_DIR)/Primpoly.o
C_OBJ_MAIN   = $(C_OBJ_DIR)/Primpoly.o

# Main program executables.
CPP_BIN_MAIN = $(CPP_BIN_DIR)/Primpoly.exe
C_BIN_MAIN   = $(C_BIN_DIR)/PrimpolyC.exe

# Archive of source code and build scripts.
CPP_C_ARCHIVE = Primpoly.tar.gz


#============================== Implicit Rules ===============================

# Link all object files to executables.
$(CPP_BIN_MAIN): $(CPP_OBJ_MAIN) $(CPP_OBJ)
	$(CPPLINK) $(LFLAGS) $(CPP_OBJ_MAIN) $(CPP_OBJ) -o $(CPP_BIN_MAIN) $(CPP_LIBS)

$(C_BIN_MAIN): $(C_OBJ_MAIN) $(C_OBJ)
	$(CCLINK) $(LFLAGS) $(C_OBJ_MAIN) $(C_OBJ) -o $(C_BIN_MAIN) $(C_LIBS)

# C++ and C source file compilation to object files.
$(CPP_BIN_DIR)/%.o : $(CPP_SRC_DIR)/%.cpp
	$(CPP) -c $(CPP_FLAGS) $< -o $@

$(C_BIN_DIR)/%.o : $(C_SRC_DIR)/%.c
	$(CC) -c $(C_FLAGS) $< -o $@

# List of all file.o : file.hpp dependencies.
Primpoly.o:			Primpoly.hpp ppArith.hpp ppOperationCount.hpp ppBigInt.hpp ppFactor.hpp ppParser.hpp ppPolynomial.hpp ppUnitTest.hpp
ppArith.o:			Primpoly.hpp ppArith.hpp ppOperationCount.hpp ppBigInt.hpp ppFactor.hpp ppParser.hpp ppPolynomial.hpp ppUnitTest.hpp
ppBigInt.o:			Primpoly.hpp ppOperationCount.hpp ppBigInt.hpp ppArith.hpp ppFactor.hpp ppParser.hpp ppPolynomial.hpp ppUnitTest.hpp
ppOperationCount.o:	Primpoly.hpp ppOperationCount.hpp ppBigInt.hpp ppArith.hpp ppFactor.hpp ppParser.hpp ppPolynomial.hpp ppUnitTest.hpp
ppFactor.o:			Primpoly.hpp ppFactor.hpp ppArith.hpp ppOperationCount.hpp ppBigInt.hpp ppParser.hpp ppPolynomial.hpp ppUnitTest.hpp
ppParser.o:			Primpoly.hpp ppParser.hpp ppArith.hpp ppOperationCount.hpp ppBigInt.hpp ppFactor.hpp ppPolynomial.hpp ppUnitTest.hpp
ppUnitTest.o:		Primpoly.hpp ppUnitTest.hpp ppArith.hpp ppOperationCount.hpp ppBigInt.hpp ppFactor.hpp ppParser.hpp ppPolynomial.hpp

ppArith.c: 			Primpoly.h
ppOrder.c: 			Primpoly.h
ppHelperFunc.c: 	Primpoly.h
ppFactor.c: 		Primpoly.h
ppPolyArith.c: 		Primpoly.h
Primpoly.c: 		Primpoly.h
ppIO.c: 			Primpoly.h

#============================== Targets ======================================

# Make the executables.
# Also copy the factor tables to the location of the executable.
c:	$(C_BIN_MAIN)

cpp:	$(CPP_BIN_MAIN)
	cp ../SourceCode/Primpoly/FactorTables/c02minus.txt $(CPP_BIN_DIR)
	cp ../SourceCode/Primpoly/FactorTables/c03minus.txt $(CPP_BIN_DIR)
	cp ../SourceCode/Primpoly/FactorTables/c05minus.txt $(CPP_BIN_DIR)
	cp ../SourceCode/Primpoly/FactorTables/c07minus.txt $(CPP_BIN_DIR)
	cp ../SourceCode/Primpoly/FactorTables/c11minus.txt $(CPP_BIN_DIR)

# Make all executables.
makeAllExes: c cpp

help:
	@echo Makefile for MAC OS, Ubuntu Linux Unix systems and Windows/Cygwin for compiling and testing Primpoly.
	@echo "Build the executables by running"
	@echo "    make"
	@echo "To remove executables, object files and archive file run"
	@echo "    make clean"
	@echo "To run regression tests do"
	@echo "    make test"
	@echo "To create an archive bundle of the source code and scripts run"
	@echo "    make archive"

# Run all tests.
test: testcpp testc

# Test the C++ program against known good results.
#     Change directory to the executable and run it there so it can find the factor table files it needs.
#     @ in front of the shell command line prevents it from being printed to the console as make runs.
#     - in front of the tells make to ignore a non-zero return code from a shell command.
#     Use sed to remove version and copyright lines which would make the comparision fail every time we change versions.
testcpp:
	@echo "Running automated tests for Primpoly, C++ version."
	-@echo "2  2"    && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN)    2  2 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  > ../test.txt
	-@echo "2 17"    && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN)    2 17 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "2 43"    && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN)    2 43 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "2 62"    && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN)    2 62 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "3 20"    && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN)    3 30 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "5 22"    && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN)    5 22 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "7 16"    && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN)    7 16 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "17 14"   && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN)   17 14 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "137 7"   && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN)  137  7 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "223 8"   && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN)  223  8 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "557 6"   && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN)  557  6 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "-sc 2 4" && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN) -sc 2 4 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "-sc 3 5" && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN) -sc 3 5 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "-a 2 5"  && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN) -a  2 5 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "-t x 1"  && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN) -t "x 1"| sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" | sed -e "s/line[ ]*[0-9][0-9]*//" >> ../test.txt
	-@echo "-t x^4 + x + 1"        && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN) -t "x^4 + x + 1"           | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "-t x^3 + x + 2, 3"     && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN) -t "x^3 + x + 2, 3"        | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	-@echo "x ^ 2 + x + 10, 32749" && cd $(CPP_BIN_DIR) && ../$(CPP_BIN_MAIN) -t "x ^ 2 + x + 10, 32749" | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d" >> ../test.txt
	diff test.txt knownGood.txt
	-@cd ..
	-@echo "Done!"

# Test the C program against known good results.
testc:
	-@echo "Running automated tests for Primpoly, C version."
	-@echo "2 2"     && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN)     2  2 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"   > ../testc.txt
	-@echo "2 17"    && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN)     2 17 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  >> ../testc.txt
	-@echo " 2 43"   && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN)     2 43 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  >> ../testc.txt
	-@echo "2 62"    && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN)     2 62 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  >> ../testc.txt
	-@echo "3 3"     && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN)     3 30 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  >> ../testc.txt
	-@echo "5 22"    && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN)     5 22 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  >> ../testc.txt
	-@echo "7 16"    && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN)     7 16 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  >> ../testc.txt
	-@echo "17 14"   && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN)    17 14 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  >> ../testc.txt
	-@echo "137 7"   && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN)   137  7 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  >> ../testc.txt
	-@echo "223 8"   && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN)   223  8 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  >> ../testc.txt
	-@echo "557 6"   && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN)   557  6 | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  >> ../testc.txt
	-@echo "-sc 2 4" && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN) -sc 2 4  | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  >> ../testc.txt
	-@echo "-sc 3 5" && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN) -sc 3 5  | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  >> ../testc.txt
	-@echo "-a 2 5"  && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN)  -a 2 5  | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  >> ../testc.txt
	-@echo "-t x 1"  && cd $(C_BIN_DIR) && ../$(C_BIN_MAIN) -t "x 1" | sed -e "s/Primpoly Version[ ]*[0-9]*\.[0-9]*//" | sed -e "/Copyright.*/d"  >> ../testc.txt
	diff testc.txt knownGoodC.txt
	-@echo "Done!"

# Remove all C and C++ object files, executables, factor tables and archives.  
#     - in front of the tells make to ignore a non-zero return code from a shell command.  So we don't stop if any files are missing.
#     @ in front of the shell command line prevents it from being printed to the console as make runs.
clean:
	-@echo "Cleaning up object files and executables"
	-@echo "Sorry, you'll have to manually clean the XCode files."
	-rm $(CPP_OBJ) $(CPP_OBJ_MAIN) $(CPP_BIN_MAIN) $(CPP_BIN_DIR)/c*.txt    # Clean C++ version object files and executables.
	-rm $(C_OBJ) $(C_OBJ_MAIN) $(C_BIN_MAIN)                                # Clean C version object files and executables.
	-rm test.txt testc.txt $(CPP_BIN_DIR)/unitTest.log                      # Clean test files.
	-rm -rf PrimpolyXCode/PrimpolyXCode/                                    # Clean up XCode as much as possible.
	-rm -rf PrimpolyXCode/Build/
	-rm -rf PrimpolyXCode/Index/
	-rm $(CPP_C_ARCHIVE)

# Archive the source code and build scripts. 
#    -Clean up all object files and executables first. 
#    -Create one *.tar.gz bundle for all the source code. 
#    -Exclude .git repository files and all the XCode files.
#    -Make executes each command in a separate shell, so pushd and popd wouldn't take effect if they were on separate lines.
#    -Make the single line look prettier by escaping the newlines.
#    -Why pushd?  Because tar won't compress correctly if I call tar in the Project/Build directory and tell tar to use 
#     the directory ../../Project.  So I pushd to the PrimitivePolynomials dir, call tar with Project dir and 
#     copy the archive down to Build/Project.
archive: clean
	-@echo "Creating an archive of all source code and build scripts in the /Build directory"
	-pushd ../.. ;\
    tar --exclude=".git" --exclude="PrimpolyXCode" -czvf $(CPP_C_ARCHIVE) Project ;\
    mv $(CPP_C_ARCHIVE) Project/Build/$(CPP_C_ARCHIVE) ;\
    popd
