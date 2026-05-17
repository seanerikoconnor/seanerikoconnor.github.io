#!/usr/bin/env python3
#
#============================================================================
#
# NAME
#
#     millerRabin.py
#
# DESCRIPTION
#
#     Miller-Rabin test for primality.
#
# USAGE
#
#     To test n for primality using random number a, 
#
#     python millerRabin.py n a 1
#
# EXAMPLES
#
#     python millerRabin.py 104729 47340 1
#         Testing n = 104729 for primality using random integer x = 47340
#         Remove powers of 2
#         k = 1 n1 = 52364
#         k = 2 n1 = 26182
#         k = 3 n1 = 13091
#         q = 3 k = 13091
#         Generate and test the sequence x^(q^k) mod n. 
#         j = 0 y = 87711
#         j = 1 y = 36639
#         j = 2 y = 104728
#         Probably prime.  Found y = n-1 or j = 0 and y = 1  y = 104728 j = 2
#
#     python millerRabin.py 9999612 32423 1
#         Testing n = 9999612 for primality using random integer x = 32423
#         Remove powers of 2
#         q = 0 k = 9999611
#         Generate and test the sequence x^(q^k) mod n. 
#         Definitely composite.  Fell off the end of the loop.
#
#     ./millerRabin.py 8398 1884460498967805432001612672369307101507474835976431925948333387748670120353629453261347843140212808\
#                           570505767386771290423087216156597588216186445958479269565424431335013281 122 1
#         Testing n = 188446049896780543200161267236930710150747483597643192594833338774867012035362945326134784314021280857050576\
#                     7386771290423087216156597588216186445958479269565424431335013281 for primality using random integer x = 122
#         Remove powers of 2
#         k = 1 n1 = 942230249483902716000806336184653550753737417988215962974166693874335060176814726630673921570106404285252883693\
#                     385645211543608078298794108093222979239634782712215667506640
#         k = 2 n1 = 47111512474195135800040316809232677537686870899410798148708334693716753008840736331533696078505320214262644184\
#                     6692822605771804039149397054046611489619817391356107833753320
#         k = 3 n1 = 235557562370975679000201584046163387688434354497053990743541673468583765044203681657668480392526601071313220923\
#                     346411302885902019574698527023305744809908695678053916876660
#         k = 4 n1 = 1177787811854878395001007920230816938442171772485269953717708367342918825221018408288342401962633005356566104616\
#                     73205651442951009787349263511652872404954347839026958438330
#         k = 5 n1 = 5888939059274391975005039601154084692210858862426349768588541836714594126105092041441712009813165026782830523083\
#                     6602825721475504893674631755826436202477173919513479219165
#         q = 5 k = 5888939059274391975005039601154084692210858862426349768588541836714594126105092041441712009813165026782830523083\
#                     6602825721475504893674631755826436202477173919513479219165
#         Generate and test the sequence x^(q^k) mod n. 
#         j = 0 y = 4562627375418921997495128389472904369506849162624397308228643567229422125069828207111411946939507039364910257582\
#                     53679056110147196100972654986996407565104255499753038631160
#         j = 1 y = 181921118629873824198891977536932720607952192628256115040458970624355555142399332847486840509884746125806162856\
#                     2013490792783220259040379029588830209459993575609245826016160
#         j = 2 y = 1675291436909496660109561278257723410018131370324303168442668644288721609236515790057247572821758832994480351123\
#                     772012853725200818096891590375783891432523321208439264772913
#         j = 3 y = 1884460498967805432001612672369307101507474835976431925948333387748670120353629453261347843140212808570505767386\
#                     771290423087216156597588216186445958479269565424431335013280
#         Probably prime.  Found y = n-1 or j = 0 and y = 1  y = 18844604989678054320016126723693071015074748359764319259483333877486\
#                     70120353629453261347843140212808570505767386771290423087216156597588216186445958479269565424431335013280 j = 3
#
# AUTHOR
#
#     Sean E. O'Connor        3 Apr 2015  Version 1.0 released.
#
# NOTES
#
#    Python interpreter:               https://www.python.org/
#    Python tutorial and reference:    htttp://docs.python.org/lib/lib.html
#    Python regular expression howto:  https://docs.python.org/3.7/howto/regex.html
#
# LEGAL
#
#     millerRabin.py Version 1.0 - A Python program to do the Miller-Rabin test for primality.
#     Copyright (C) 2017-2025 by Sean Erik O'Connor.  All Rights Reserved.
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
#============================================================================

import sys

def main():

    print( "Running Python Version {0:d}.{1:d}.{2:d}".format( sys.version_info[ 0 ], sys.version_info[ 1 ], sys.version_info[ 2 ] ) )

    if len( sys.argv ) != 4:
        print( "Usage: python MillerRabin.py n x d" )
        print( "    n   the number to be tested for primality" )
        print( "    x   any random number" )
        print( "    d   nonzero turns on debug prints" )
        sys.exit()
    else:
        n = int( sys.argv[ 1 ] )
        x = int( sys.argv[ 2 ] )
        if int( sys.argv[ 3 ] ) == 0:
            debug = False
        else:
            debug = True

        if debug:
            print( "Testing n = {0:d} for primality using random integer x = {1:d}".format( n, x ) )

        if MillerRabin( n, x, debug ):
            print( "Probably prime" )
        else:
            print( "Definitely composite" )

        sys.exit( 0 )

def MillerRabin( n, x, debug ):
    n1 = n - 1

    # Remove powers of 2. 
    k = 0
    even = True 

    if debug:
        print( "Remove powers of 2" )

    while n1 % 2 == 0:
        n1 //= 2
        k += 1
        if debug:
            print( "k = {0:d} n1 = {1:d}".format( k, n1 ))

    q = n1

    if debug:
        print( "q = {0:d} k = {1:d}".format( k, n1 ) )

    y = pow( x, q, n )

    if debug:
        if debug:
            print( "Generate and test the sequence x^(q^k) mod n. " ) ;

    for j in range (0,k):
        if debug:
            print( "j = {0:d} y = {1:d}".format( j, y ))

        if (j == 0 and y == 1) or y == n-1:
            if debug:
                print( "Probably prime.  Found y = n-1 or j = 0 and y = 1  y = {0:d} j = {1:d}".format( y, j ) )
            return True

        if j > 0 and y == 1:
            if debug:
                print( "Definitely composite.  Found j > 0 and y = 1" )
            return False

        y = pow( y, 2, n )

    if debug:
        print( "Definitely composite.  Fell off the end of the loop." )
    return False

# Call the main.
if __name__ == '__main__':
    main()
