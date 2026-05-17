/*=============================================================================
|
| NAME
|  
|      FFT.cpp
|
| DESCRIPTION
|  
|      This program does an in-place one dimensional complex discrete
|      Fourier transform.  It uses an FFT algorithm for a number of 
|      input points which is a power of two.  It's implemented in C++
|      as a derived class of the STL vector type.
|    
| AUTHOR
|
|      Sean O'Connor   19 November 2005
|
| LEGAL
|
|     FFT Version 1.6 - An FFT utility library in C++.
|     Copyright (C) 2005-2026 by Sean Erik O'Connor.  All Rights Reserved.
|
|     This program is free software: you can redistribute it and/or modify
|     it under the terms of the GNU General Public License as published by
|     the Free Software Foundation, either version 3 of the License, or
|     (at your option) any later version.
|
|     This program is distributed in the hope that it will be useful,
|     but WITHOUT ANY WARRANTY; without even the implied warranty of
|     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
|     GNU General Public License for more details.
|
|     You should have received a copy of the GNU General Public License
|     along with this program.  If not, see <http://www.gnu.org/licenses/>.
|     
|     The author's address is seanerikoconnor!AT!gmail!DOT!com
|     with !DOT! replaced by . and the !AT! replaced by @
|     
+============================================================================*/

/*------------------------------------------------------------------------------
|                                Include Files                                 |
------------------------------------------------------------------------------*/

#include <iostream>     // Basic stream I/O.
#include <fstream>      // File stream I/O.
#include <sstream>      // String stream I/O.
#include <cmath>        // Basic math functions.
#include <complex>      // Complex data type and operations.
#include <vector>       // STL vector class.
#include <algorithm>    // Iterators.
#include <string>       // STL string class.
#include <stdexcept>    // Exceptions.
#include <numbers>      // Constants like pi_v<float type>

using namespace std ;   // Let us omit the std:: prefix for every STL class.

#include "FFT.hpp"      // Our own FFT stuff.


/*=============================================================================
|
| NAME
|  
|     FastFourierTransform
|
| DESCRIPTION
|  
|     Default constructor.  Just call the base class constructor for
|     the vector type, then initialize the derived class field.
|    
+============================================================================*/

template <typename FloatType>
FastFourierTransform<FloatType>::FastFourierTransform() 
    : vector< complex<FloatType> >()
    , direction( false )
{
        // Get the sine and cosine tables initialized.
 /// MAX_TABLE_SIZE ) ;
        starting_multiplier.clear();
}


/*=============================================================================
|
| NAME
|  
|     ~FastFourierTransform
|
| DESCRIPTION
|  
|     Destructor.  Doesn't need to do much.
|    
+============================================================================*/

template <typename FloatType>
FastFourierTransform<FloatType>::~FastFourierTransform()
{
}



/*=============================================================================
|
| NAME
|  
|     FastFourierTransform
|
| DESCRIPTION
|  
|     Copy constructor.
|    
+============================================================================*/

template <typename FloatType>
FastFourierTransform<FloatType>::FastFourierTransform( const FastFourierTransform & transform ) 
    : vector< complex<FloatType> >( transform ) // Initialize base class first.
{
    // Copy derived class stuff.
    direction = transform.direction ;
}


/*=============================================================================
|
| NAME
|  
|     =
|
| DESCRIPTION
|  
|     Assignment operator.
|    
+============================================================================*/

template <typename FloatType>
FastFourierTransform<FloatType> & FastFourierTransform<FloatType>::operator=( const FastFourierTransform & transform )
{
    // Check for initializing to oneself:  pass back a reference to the unchanged object.
    if (this == &transform)
    {
        // Pass back the object so we can concatenate assignments.
        return *this ;
    }

    // Call base class assignment operator first.
    FastFourierTransform<FloatType>::operator=( transform ) ;

    // Assignment for derived class fields.
    direction = transform.direction ;


    // Pass back the object so we can concatenate assignments.
    return *this ;
}


/*=============================================================================
|
| NAME
|  
|     fft
|
| DESCRIPTION
|  
|
|    This member function does an in-place one dimensional complex
|    discrete Fourier transform.  It uses an FFT algorithm for a number
|    of input points which is a power of two.
|    
| PARAMETERS
|
|     direction  The direction of the FFT, true for a forward transform and 
|     false for an inverse transform.
|
| EXCEPTIONS
|
|     Throws FastFourierTransform type exceptions for the cases where
|
|         -Number of points in the transform is less than 2.
|         -Number of points is greater than the sine/cosine table can handle.
|         -Number of points is not a power of 2.
|
| EXAMPLE 
|
|     Suppose the vector contains the data
|
|         X ( 0 )  =  1  +  i
|         X ( 1 )  =  2  +  2 i
|         X ( 2 )  =  3  +  3 i
|         X ( 3 )  =  4  +  4 i
|
|    then the forward FFT returns
|
|         X ( 0 ) =   5  +  5 i
|         X ( 1 ) =  -2
|         X ( 2 ) =  -1  -    i
|         X ( 3 ) =      -  2 i
|
|    and the inverse FFT returns the original data to within roundoff.
|  
|                             ^
|    The Fourier coefficients X( k ) are defined for k = 0, . . ., N - 1
|    by the formula
|
|                          N - 1               2 Pi i
|    ^             1       ____             -  ------ j k
|    X( k ) =  ---------   \                     N
|                -----     /      X( j )  e
|             \ /  N       ----
|              v           j = 0
|
|    where e is 2.1718 . . ., Pi = 3.14159. . . and i is the square root
|    of -1.
|
|    This is the formula for the forward transform.  The inverse transform
|    is the same, except that the minus sign in the exponent above is a
|    plus sign instead.
|                                 ---
|    The normalizing factor 1 / \/ N  in front was picked so that the
|    forward and inverse transforms look the same.
|
|    The particular type of FFT algorithm we use is a
|
|                               Complex,
|                             Two to the N,
|                       Decimation in  frequency,
|                 Input in order, output bit reversed
|
|     type of FFT.  It is described in the book
|
|                  THE FAST FOURIER TRANSFORM,
|                  F. Oran Brigham, Prentice Hall, 1974
|
|     Also see my notes for an in-depth explanation.
|
| BUGS
|  
|   The bit-reversal routine could be made faster by using bit shifting
|   operations.
|
|   You might want to use long double precision complex numbers to get more
|   accuracy.
|
|   Check for a power of 2 probably ought to use the machine's floating point
|   epsilon (computed automatically).
|
+============================================================================*/

template <typename FloatType>
void FastFourierTransform<FloatType>::fft( bool direction ) 
{
// Number of complex points in the FFT from the vector's size.
unsigned int N = this->size() ;

/*
 *  Compute log base 2 of N. Perturb slightly to avoid roundoff error.
 *  For example, (int)( 4.99999999999 ) = 4 (wrong!), but
 *  (int)( 4.999999999 + .01 ) = 5 (correct!)
 */
int log_of_n = (int) ( log( (FloatType) N ) / ( log( 2.0 ) )  + .01 ) ;


/*
 *  Error checking.  Print a message to the terminal if any one of these
 *  conditions is true:
 *
 *       N < 2.
 *       log2( N ) > MAX_TABLE_SIZE + 1.
 *       N is not a power of 2.
 */
if (N < 2)
{
    ostringstream os ;
    os << "FFT has less than two points.  N = " << N << " file: " << __FILE__ << " line: " << __LINE__ ;;
    throw FastFourierTransformException( os.str() ) ;
}
else if ( (log_of_n - 1) > MAX_TABLE_SIZE)
{
    ostringstream os ;
    os << "FFT has too many points for its sin/cos table. Table size = " << MAX_TABLE_SIZE << " file: " << __FILE__ << " line: " << __LINE__ ;
    throw FastFourierTransformException( os.str() ) ;

}
else if ( (int) pow( 2.0, log_of_n ) != N )
{
    ostringstream os ;
    os << "Number of points in the FFT is not a power of 2.  N = " << N << " file: " << __FILE__ << " line: " << __LINE__ ;;
    throw FastFourierTransformException( os.str() ) ;
}


/*
 *  If called_already is false, generate the sine and cosine table for
 *  the first time, then set called_already to true.  Now later calls to 
 *  this function don't recreate the sine and cosine table.
 */
if (!called_already)
{
    for (int i = 0 ;  i <= MAX_TABLE_SIZE - 1 ;  ++i)
    { 
        // Current angle in sine and cosine table.
        FloatType angle = -PI / pow( (FloatType) 2, (FloatType) i ) ;

        // e^t = cos t + i sin t
        starting_multiplier[ i ] = complex<FloatType>(cos(angle), sin(angle)) ;
    }

    called_already = true ;
}



/*
 *  Compute the FFT according to its signal flow graph with 
 *  computations arranged into butterflies, groups of butterflies
 *  with the same multiplier, and columns.
 */
int butterfly_height = N / 2 ;
int number_of_groups = 1 ;


/*
 *  A column refers to a column of the FFT signal flow graph.  A group is
 *  a collection of butterflies which have the same multiplier W^p.  A
 *  butterfly is the basic computational unit of the FFT.
 */
for (int column = 1 ;  column <= log_of_n ;  ++column)
{
    // The multiplier W^p for a group of butterflies.
    complex<FloatType> multiplier = starting_multiplier[ column - 1 ] ;

    //  Modify starting multiplier W^p when computing the inverse transform.
    if (direction == false) 
        multiplier = conj( multiplier ) ;

    // Difference between current multiplier and next.
    complex<FloatType> increment = multiplier ;

    //  Compute the first group.
    for (int i = 0 ;  i <= butterfly_height - 1 ;  ++i)
    {
        // Lower branch of a butterfly.
        int offset = i + butterfly_height ;

        complex<FloatType> temp = (*this)[ i ] + (*this)[ offset ] ;
        (*this)[ offset ]    = (*this)[ i ] - (*this)[ offset ] ;
        (*this)[ i ]         = temp ;
    }

    //  Now do the remaining groups.
    for (int group = 2 ;  group <= number_of_groups ;  ++group)
    {
        // Array index of first butterfly in group.
        int start_of_group = reverse_bits( group - 1, log_of_n ) ;

        // Array index of last butterfly in group. 
        int end_of_group   = start_of_group + butterfly_height - 1 ;

        //  Compute all butterflies in a group.
        for (int i = start_of_group ;  i <= end_of_group ;  ++i)
        {
            int offset   =  i + butterfly_height ;

            // Temporary storage in a butterfly calculation.
            complex<FloatType> product = (*this)[ offset ] * multiplier ;

            complex<FloatType> temp    = (*this)[ i ] + product ;
            (*this)[ offset ]       = (*this)[ i ] - product ;
            (*this)[ i ]            = temp ;

         }

         multiplier *= increment ;
    } // end group

    butterfly_height = butterfly_height / 2 ;
    number_of_groups = number_of_groups * 2  ;

} // end column



// Normalize the results by \/ N and permute them into order, two at a time.
FloatType normalizer = (FloatType) 1.0 / sqrt( (FloatType) N ) ;


for (int i = 0 ;  i <= N - 1 ;  ++i)
{
    // Bit-reversed array index i.
    int rev_i = reverse_bits( i, log_of_n ) ;

    if ( rev_i > i )  // Exchange is not yet done.
    {
	   complex<FloatType> temp = (*this)[ i ] ;
       (*this)[ i ]          = (*this)[ rev_i ] * normalizer ;
       (*this)[ rev_i ]      = temp * normalizer ;
	}
    else if ( rev_i == i ) // exchange with itself
    { 
       (*this)[ i ]          = (*this)[ i ] * normalizer ;
    }
}

return ;

} /* ====================== end of function fft ============================= */



/*=============================================================================
|
| NAME
|  
|     reverse_bits
|
| DESCRIPTION
|
|     This function reverses the order of the bits in a number.
|
| INPUT
|
|     n              The number whose bits are to be reversed.
|     num_bits       The number of bits in N, counting leading zeros.
|
| OUTPUT
|
|                    The number N with all its num_bits bits reversed.
|
| EXAMPLE CALLING SEQUENCE
|
|     reverse_bits( (10)  , 2 ) = (01) = 1, but
|                       2             2
|
|     reverse_bits( (10)  , 3 ) = reverse_bits( (010)  , 3 ) = (010)  = (10)
|                       2                            2              2       2
|     = 10
|
|
| METHOD
|
|     The algorithm works by a method similar to base conversion.
|     As the low order bits are broken off, one by one, they are
|     multiplied by 2 and accumulated to generate the bit-reversed
|     number.
|
| BUGS
|
|    The bit-reversal routine could be made faster by using C shift operators.
|
+============================================================================*/

template <typename FloatType>
int FastFourierTransform<FloatType>::reverse_bits( int n, int num_bits )
{
    int
        remainder = n,   // Bits remaining to be reversed.     
        reversed_n = 0 ; // Bit-reversed value of n.          

    for (int bit_num = 1 ;  bit_num <= num_bits ;  ++bit_num)
    {
        int bit    = remainder % 2 ;           /* Next least significant bit.   */
        reversed_n = bit + 2 * reversed_n  ;   /* Shift left and add to buffer. */
        remainder  = (int)( remainder / 2 ) ;  /* Remaining bits.               */
    }

    return( reversed_n ) ;

} /* ===================== end of function reverse_bits ===================== */


/*==============================================================================
|                     Forced Template Instantiations                           |
==============================================================================*/

// C++ doesn't automatically generate templated classes or functions until they
// are first used.  So depending on the order of compilation, the linker may say
// the templated functions are undefined.
//
// Therefore, explicitly instantiate ALL templates here:

template      FastFourierTransform<float>::FastFourierTransform() ;
template      FastFourierTransform<float>::FastFourierTransform( const FastFourierTransform<float> & ) ;
template      FastFourierTransform<float>::~FastFourierTransform() ;
template void FastFourierTransform<float>::fft( bool ) ;

template      FastFourierTransform<double>::FastFourierTransform() ;
template      FastFourierTransform<double>::FastFourierTransform( const FastFourierTransform<double> & ) ;
template      FastFourierTransform<double>::~FastFourierTransform() ;
template void FastFourierTransform<double>::fft( bool ) ;

