#!/bin/bash

# cleanupdate.sh

printf "Clean up all Xcode files which are not needed\n"

# You only need /Primpoly/Primpoly.xcodeproj which is the Xcode project 
# and /Primpoly which contains a duplicate copy of the source code.

printf "Removing /Build /ModuleCache.noindex /CompilationCache.noindex /Primpoly-RANDOMLETTERS /SymbolCache.noindex / SDKStatCaches.noindex\n"
rm -rf Build
rm -rf ModuleCache.noindex
rm -rf CompilationCache.noindex
rm -rf Primpoly-*
rm -rf SymbolCache.noindex
rm -rf SDKStatCaches.noindex

printf "Copying over the source files to XCode's local copy of the source code.\n"

cp -rf ../../SourceCode/Primpoly/*.cpp Primpoly/Primpoly
cp -rf ../../SourceCode/Primpoly/*.hpp Primpoly/Primpoly

printf "Removing syntax highlighted source files\n"
rm -rf Primpoly/Primpoly/*.html

printf "Done!\n"
