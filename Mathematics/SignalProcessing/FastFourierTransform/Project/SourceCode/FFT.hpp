#ifndef __FFT_HPP__

/*=============================================================================
|
| NAME
|  
|      FFT.hpp
|
| DESCRIPTION
|  
|      This program does an in-place one dimensional complex discrete
|      Fourier transform.  It uses an FFT algorithm for a number of 
|      input points which is a power of two.  It works on both single
|      precision and double precision floating point numbers.
|    
| AUTHOR
|
|      Created:  Sean O'Connor   19 November 2005
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

/*
 *  We must set the size of the sine and cosine table used in the FFT.
 *  The table is called starting_multiplier.
 *     
 *  Suppose MAX is the largest number of points we would ever transform.  We set
 *
 *      MAX_TABLE_SIZE  =  LOG ( MAX ) - 1
 *                            2
 *
 *  to be the size of the table.  This table can now be used by the FFT for 
 *  any number of points from 2 up to MAX.
 *
 *  For example, if MAX_TABLE_SIZE = 14, then we can transform anywhere from 
 *  2 to 2 ^ 15 = 32,768 points, using the same sine and cosine table.
 *
 */
const int    MAX_TABLE_SIZE = 13 ;



// Derive the FFT class from an STL vector with a floating point type to be specified.
// Thus we get the vector's data manipulation attributes and
// we can substitute FFT objects into an existing software
// framework which uses vector objects in containers.
// But extend the class by adding a Fourier Transform capability.
//
template <typename FloatType>
class FastFourierTransform
      : public vector< complex<FloatType> > // Need spaces between angle brackets to satisfy compiler.
{
    public:
        // Default constructor.
        FastFourierTransform() ;
        
        // Destructor.
        ~FastFourierTransform() ;

        // Copy constructor ;
        FastFourierTransform( const FastFourierTransform & transform ) ;

        // Assignment operator.
        FastFourierTransform & operator=( const FastFourierTransform & transform ) ;

        // Fast Fourier transform capability.
        void fft( bool direction = true ) ;

    // Maybe these should be private to be safe!
    protected:
        bool direction ;

    private:
        // Table of sines and cosines whose values are created the first 
        // time any object calls the fft() member function and which are
        // shared among all subsequent objects.
        static vector< complex<FloatType> > starting_multiplier ;
        static bool called_already ;
		static const FloatType PI ;
		
		// Helper function used by FFT member function only.
        static int reverse_bits( int n, int num_bits ) ;
} ;


/*=============================================================================
|
| NAME
|  
|     FastFourierTransformException
|
| DESCRIPTION
|  
|     Helper class for recording data thrown by FastFourierTransform.
|
| BUGS
|
+============================================================================*/
       
class FastFourierTransformException : public runtime_error
{
    public:
        // This form will be used most often in a throw.
        FastFourierTransformException( const string & description )
			: runtime_error( description )
        {
        } ;

        // Throw with no error message.
        FastFourierTransformException()
			: runtime_error( "FFT exception:  " )
        {
        } ; 

} ; // end class FastFourierTransformException


/*==============================================================================
|                     Static Class Variables Initialization                    |
==============================================================================*/
 
// Static class variables must be initialized outside the class.

template <typename FloatType>                                          // Not just a class, but a template class with a parameterized type.
vector< complex<FloatType> >                                           // The data type of this static variable.
FastFourierTransform<FloatType>::starting_multiplier(MAX_TABLE_SIZE) ; // Declare the variable as a member of class having a
                                                                       // parameterized type.
                                                                       // Initialize the size to the maximum, and default to zeros.
template <typename FloatType> bool            FastFourierTransform<FloatType>::called_already = false ;
template <typename FloatType> const FloatType FastFourierTransform<FloatType>::PI             = static_cast<FloatType>(3.14159265358979323846264338327950288419716939) ;
#endif // __FFT_HPP__
