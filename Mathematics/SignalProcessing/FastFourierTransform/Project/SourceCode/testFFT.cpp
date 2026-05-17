/*=============================================================================
|
| NAME
|  
|      testFFT.cpp
|
| DESCRIPTION
|  
|      Test program for FFT.cpp
|    
| AUTHOR
|
|      Sean O'Connor
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
#include <cmath>        // Basic math functions.
#include <complex>      // Complex data type and operations.
#include <vector>       // STL vector class.
#include <fstream>      // File stream I/O.
#include <algorithm>    // Iterators.
#include <string>       // STL string class.
#include <stdexcept>    // Exceptions.
#include <limits>       // Numeric limits, e.g. floating point.
#include <iomanip>      // Floating point formating.

using namespace std ;   // Let us omit the std:: prefix for every STL class.
using namespace std::complex_literals ;  // Let's us do complex c = 1 +2i 

#include "FFT.hpp"      // Our own FFT stuff.

// Pick just one.
#define SIMPLE_WAY_TO_READ_NUMBERS_FROM_FILE
//#define COMPLICATED_WAY_TO_READ_NUMBERS_FROM_FILE
//#define HARDCODED_DATA

string legalNotice
(
    "\n"
    "FFT Version 1.2 - An FFT utility in C++.\n"
    "Copyright (C) 2005-2026 by Sean Erik O'Connor.  All Rights Reserved.\n"
   "\n"
    "FFT comes with ABSOLUTELY NO WARRANTY; for details see the\n"
    "GNU General Public License.  This is free software, and you are welcome\n"
    "to redistribute it under certain conditions; see the GNU General Public License\n"
    "for details.\n\n"
) ;


/*=============================================================================
|
| NAME
|  
|     main
|
| DESCRIPTION
|
|     This program tests the FFT implementation by performing forward and
|     inverse transforms on the data and testing error conditions.
|    
| INPUT
|   
|     File containing 
|        
|       - Number of complex points in the transform.
|       - The data points (complex numbers).
|
|    OUTPUT
|    
|       - DFT of the input.
|       - inverse DFT of the first DFT.
|    
|    EXAMPLE
|
|        From the command line, call
|
|        $  FastFourierTransform fftIn.txt fftOut.txt
| 
|        where the input file fftIn.txt contains
|
|        4
|        (1, 1)
|        (2, 2)
|        (3, 3)
|        (4, 4)
|     
|        and the output file fftOut.txt contains
|
|        num_points = 4
|        Point num. 0= (1,1)
|        Point num. 1= (2,2)
|        Point num. 2= (3,3)
|        Point num. 3= (4,4)
|        The transform of the input data is . . . 
|        
|        Point num. 0 =  (5,5)
|        Point num. 1 =  (-2,-1.11022e-016)
|        Point num. 2 =  (-1,-1)
|        Point num. 3 =  (0,-2)
|        The inverse transform of the transform above is . . .
|        
|        Point num. 0 = (1,1)
|        Point num. 1 = (2,2)
|        Point num. 2 = (3,3)
|        Point num. 3 = (4,4)
|        Point num. 0 = (1,1)
|        Point num. 1 = (2,2)
|        Point num. 2 = (3,3)
|        Point num. 3 = (4,4)
|
|        Calling FFT with too many points.
|        FFT has too many points for its sin/cos table
|
+============================================================================*/

int main( int argc, char * argv[] )
{
    cout << legalNotice ;

    int num_points = 0 ;   // Number of points in the transform.
    int i = 0 ;

    // Open file streams for input and output getting file names
    // from the command line.
    if (argc != 3)
    {
        cerr << "Error:  Missing the names of the input and output "
                 "files or too many files on the command line." ;
        return 1 ;
    }

    char * inputFileName  = argv[ 1 ] ;
    char * outputFileName = argv[ 2 ] ;

    fstream fin ( inputFileName,  ios::in  ) ;
    fstream fout( outputFileName, ios::out ) ;

    // Set a really high precision for our printouts.
    // Of course some binary numbers will have repeating decimals, but we are checking to see if we get the same rounding results
    // different computer architectures.
    fout << scientific << setprecision( 100 ) << setw( 100 );

    if (!(fin.is_open() && fout.is_open()))
    {
        cerr << "Error:  Problem opening the input or output files. "
                "Check the file names and permissions." ;
        return 1 ;
    }

    try
    {
        //////////////////////////////////////////////////////////////////////////
        /// Single precision FFT
        //////////////////////////////////////////////////////////////////////////

        // Create our DFT object.
        FastFourierTransform<float> dft_single ;

        // Clear the fft object.
        dft_single.clear() ;

        // Read lines until end of file.
        while (!fin.eof())
        {
            // Read the number of points in the transform.
            fin >> num_points ;

            //  Check to see that the number of points in the FFT is valid.
            if (num_points <= 0)
                throw FastFourierTransformException( "The number of points is out of range.\n" ) ;

            // Read in the complex data points from file into the vector.
            for (i = 0 ;  i < num_points ;  ++i)
            {
                complex<float> c ;
                fin >> c ;

                dft_single.push_back( c ) ;
            }
        }
   
        fout << "* * * * * * Single precision FFT" << endl ; 

        //  Print out the points just read in.
        fout << "\n\n\nNumber of points = " << num_points << endl ;

        for (i = 0 ;  i <= num_points - 1 ;  ++i)
            fout <<  "Point num. " << i << " = " << dft_single[ i ] << endl ;

        // Try a forward FFT.
        dft_single.fft( true ) ;

        //  Print the transform results.
        fout << "\n\nThe discrete Fourier transform of the input data is . . . \n\n" ;

        for (i = 0 ;  i <= num_points - 1 ;  ++i)
            fout << "Point num. " << i << " =  " << dft_single[ i ] << endl ;

        //  Try an inverse transform to get the input data back, with roundoff error.
        dft_single.fft( false ) ;

        // Print the inverse transform.
        fout << "\n\nThe inverse transform of the transform above is . . .\n\n" ;

        for (i = 0 ;  i <= num_points - 1 ;  ++i)
            fout << "Point num. " << i << " = " << dft_single[ i ] << endl ;

        //////////////////////////////////////////////////////////////////////////
        /// Double precision FFT
        //////////////////////////////////////////////////////////////////////////

        fout << endl << endl << endl << "* * * * * * Double precision FFT" << endl ; 

        // Create our DFT object.
        FastFourierTransform<double> dft_double ;

        // Clear the fft object.
        dft_double.clear() ;

#if defined( SIMPLE_WAY_TO_READ_NUMBERS_FROM_FILE ) || defined( COMPLICATED_WAY_TO_READ_NUMBERS_FROM_FILE )
        // Rewind the input file to the begining.
        fin.clear() ;              // Forget we hit the end of file.
        fin.seekg( 0, ios::beg ) ; // Move to the start of the file.
#endif // defined( SIMPLE_WAY_TO_READ_NUMBERS_FROM_FILE ) || defined( COMPLICATED_WAY_TO_READ_NUMBERS_FROM_FILE )

#ifdef COMPLICATED_WAY_TO_READ_NUMBERS_FROM_FILE
        // Store the lines of file as a vector of strings.
        vector<string> buffer ;
        buffer.clear() ;

        // Add each line of the file to the vector.
        string line_of_file ;
        while (getline( fin, line_of_file ))
            buffer.push_back( line_of_file ) ;

        // Now the whole file is in memory.
        // Parse the first line which is the number of points.
        istringstream is ;
        is.clear() ;
        is.str( buffer[ 0 ] ) ;
        is >> num_points ;

        //  Check to see that the number of points in the FFT is valid.
        if (num_points <= 0)
            throw FastFourierTransformException( "The number of points is out of range.\n" ) ;

        // Now parse all the other lines which are the data points.
        int line_num = 1 ;
        while (line_num < buffer.size())
        {
            // Get the next line in memory and advance.
            string line_of_file = buffer[ line_num++ ] ;

            // Parse the complex number.
            istringstream is ;
            is.clear() ;
            is.str( line_of_file ) ;
            complex<double> c ;
            is >> c ;

            dft_double.push_back( c ) ;
        }
#endif // COMPLICATED_WAY_TO_READ_NUMBERS_FROM_FILE

#ifdef SIMPLE_WAY_TO_READ_NUMBERS_FROM_FILE
        if (!fin.eof())
        {
            // Read the number of points in the transform.
            fin >> num_points ;

            //  Check to see that the number of points in the FFT is valid.
            if (num_points <= 0)
            {
                ostringstream os ;
                os << "The number of points = " << num_points << " is out of range.\n" ;
                throw FastFourierTransformException( os.str() ) ;
            }
         }

        // Read in the complex data points from file into the vector.
        for (int index = 1 ;  index <= num_points ;  ++index)
        {
            complex<double> c = 0.0 + 0.0i ; // Floating literals default to double.
    
            if (!fin.eof())
               fin >> c ;
            else
            {
                ostringstream os ;
                os << "The number of data points was too short.\n" ;
                throw FastFourierTransformException( os.str() ) ;
            }

            dft_double.push_back( c ) ;
        }
#endif // SIMPLE_WAY_TO_READ_NUMBERS_FROM_FILE

#ifdef HARDCODED_DATA
        num_points = 16 ;
        dft_double.push_back( 1.0  +  1.0i ) ;
        dft_double.push_back( 2.0  +  2.0i ) ;
        dft_double.push_back( 3.0  +  3.0i ) ;
        dft_double.push_back( 4.0  +  4.0i ) ;
        dft_double.push_back( 5.0  +  5.0i ) ;
        dft_double.push_back( 6.0  +  6.0i ) ;
        dft_double.push_back( 7.0  +  7.0i ) ;
        dft_double.push_back( 8.0  +  8.0i ) ;
        dft_double.push_back( 9.0  +  9.0i ) ;
        dft_double.push_back( 10.0 + 10.0i ) ;
        dft_double.push_back( 11.0 + 11.0i ) ;
        dft_double.push_back( 12.0 + 12.0i ) ;
        dft_double.push_back( 13.0 + 13.0i ) ;
        dft_double.push_back( 14.0 + 14.0i ) ;
        dft_double.push_back( 15.0 + 15.0i ) ;
        dft_double.push_back( 16.0 + 16.0i ) ;
#endif // HARDCODED_DATA

        //  Print out the points just read in.
        fout << "\n\n\nNumber of points = " << num_points << endl ;

        for (i = 0 ;  i <= num_points - 1 ;  ++i)
            fout <<  "Point num. " << i << "= " << dft_double[ i ] << endl ;

        // Try a forward FFT.
        dft_double.fft( true ) ;

        //  Print the transform results.
        fout << "\n\nThe discrete Fourier transform of the input data is . . . \n\n" ;

        for (i = 0 ;  i <= num_points - 1 ;  ++i)
            fout << "Point num. " << i << " =  " << dft_double[ i ] << endl ;

        //  Try an inverse transform to get the input data back, with roundoff error.
        dft_double.fft( false ) ;

        // Print the inverse transform.
        fout << "\n\nThe inverse transform of the transform above is . . .\n\n" ;

        for (i = 0 ;  i <= num_points - 1 ;  ++i)
            fout << "Point num. " << i << " = " << dft_double[ i ] << endl ;

        // =======================================
        // Test the copy constructor.
        // =======================================

        fout << "\n\nTest the copy constructor" << endl ;
    
        FastFourierTransform copy_of_dft_single( dft_single ) ;
        for (i = 0 ;  i <= num_points - 1 ;  ++i)
            fout << "Point num. " << i << " = " << copy_of_dft_single[ i ] << endl ;

        // =======================================
        // Floating point implementation details.
        // =======================================

        // Set a really high precision for our printouts.
        fout << scientific << setprecision( 50 ) << setw( 60 ) << endl ;
        fout << "= floating point epsilons =" << endl ;
        fout << "single precision floating point epsilon = " << numeric_limits<float>::epsilon() << endl ;
        fout << "single precision test: (1.0f + 0.999999f * epsilon) - 1.0f = " << ((1.0f + 0.5f * numeric_limits<float>::epsilon()) - 1.0f) << endl ;
        fout << "single precision test: (1.0f + epsilon - 1.0f              = " << ((1.0f + numeric_limits<float>::epsilon()) - 1.0f) << endl << endl ;

        fout << "double precision floating point epsilon = " << numeric_limits<double>::epsilon() << endl ;
        fout << "double precision test: (1.0f + 0.999999 * epsilon) - 1.0f = " << ((1.0f + 0.5f * numeric_limits<double>::epsilon()) - 1.0f) << endl ;
        fout << "double precision test: (1.0f + epsilon - 1.0f             = " << ((1.0f + numeric_limits<double>::epsilon()) - 1.0f) << endl;

        // =======================================
        // Test error conditions.  Only the first will execute due to
        // the throw, so comment out and recompile to test them all.
        // =======================================

        //  Number of points is less than 2.
        fout << "\n\nCalling FFT with 1 point.\n" ;

        // Make sure we flush all the data to file, when we're debugging. Then close the files.
        fout << flush ;
        fin.close() ;
        fout.close() ;

        FastFourierTransform<double> dft_single2 ;
        dft_single2.push_back( complex<double>(1.0, 2.0) ) ;
        dft_single2.fft( true ) ;
    }

    // Catch exceptions and print their text explanations.
    // Clean up resources.
    catch( FastFourierTransformException & e )
    {
        fout << "FFT exception:  " << e.what() << endl ;

        fin.close() ;
        fout.close() ;

        return 1 ;
    }
    catch( runtime_error & e )
    {
        fout << "Unexpected runtime exception:  Please email the author." << e.what() << endl ;

        fin.close() ;
        fout.close() ;

        return 1 ;
    }
   catch( ... )
    {
        fout << "Unexpected exception:  Please email the author." << endl ;

        fin.close() ;
        fout.close() ;

        return 1 ;
    }


    return 0 ;

} /* ====================== end of function main ============================ */
