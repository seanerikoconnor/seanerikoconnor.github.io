C    -------------------------------------------------------------------------
C    |  File name:   fftd.for              Sean O'Connor             9-22-87 |
C    |                                                               7-01-17 |
C    ------------------------------------------------------------------------- 

C    -------------------------------------------------------------------------
C    |  VAX 11/785       VMS 4.5                   VAX EXTENDED FORTRAN 77   |
C    |  MacBook Pro      Ubuntu LTS 16.04 Linux    gfortran                  |
C    -------------------------------------------------------------------------


C  ****************************************************************************
C  *                                                                          *
C  *                            FFTD                                          *
C  *                                                                          *
C  ****************************************************************************
C
C
C  DESCRIPTION
C 
C      This program tests the subroutine FFT in the file FFT.FOR  It does a 
C      forward discrete Fourier transform (DFT).  It then does an inverse
C      transform of the forward transform to check the roundoff error.
C
C
C  INPUT 
C
C      The number of complex points in the transform.
C      Whether to do a forward (1) or inverse (-1) transform.
C      The data points (complex numbers).
C
C
C  OUTPUT
C
C      The DFT of the input.
C      The inverse DFT of the first DFT.
C
C
C  EXAMPLE 
C
C      $ ./FFTD
C
C      Enter number of complex points in transform: 4
C
C      Enter 1 (forward) or -1 (inverse) transform:  1
C
C      Enter point no.   0 (Real, Imag) >  (1,1)
C      Enter point no.   1 (Real, Imag) >  (2,2)
C      Enter point no.   2 (Real, Imag) >  (3,3)
C      Enter point no.   3 (Real, Imag) >  (4,4)
C
C      num_points =          4
C      direction  =          1
C
C      Point No.   0 = (   1.0000000000000       1.0000000000000     ) 
C      Point No.   1 = (   2.0000000000000       2.0000000000000     ) 
C      Point No.   2 = (   3.0000000000000       3.0000000000000     ) 
C      Point No.   3 = (   4.0000000000000       4.0000000000000     ) 
C
C      The transform of the input is . . .
C 
C      Point No.   0= (  5.0000000000000       5.0000000000000     ) 
C      Point No.   1= ( -2.0000000000000      0.00000000000000E+000) 
C      Point No.   2= ( -1.0000000000000      -1.0000000000000     ) 
C      Point No.   3= (-0.59604644775391E-007 -2.0000000000000     ) 
C
C      The inverse transform of the transform above is . . .
C  
C      Point No.   0= (  1.0000000000000       1.0000000000000     ) 
C      Point No.   1= (  2.0000000000000       2.0000000000000     ) 
C      Point No.   2= (  3.0000000000000       3.0000000000000     ) 
C      Point No.   3= (  4.0000000000000       4.0000000000000     ) 
C
C
C  INSTALLATION
C
C      To compile, type
C
C          $ gfortran FFTD.FOR FORTRAN FFT.FOR -o FFT
C
C      To run, type
C
C          $ ./FFTD
C       
C 
C  ****************************************************************************
C  *                                                                          *
C  ****************************************************************************

      PROGRAM fftd

C  -------------------------------------------------------------------------
C  |                            MACRO DEFINITIONS                          |
C  ------------------------------------------------------------------------- 

      PARAMETER ( MAX_NUM_POINTS = 255 )   !  Maximum number of points in FFT.


C -------------------------------------------------------------------------
C |                          LOCAL VARIABLES                              |
C -------------------------------------------------------------------------

        INTEGER i,             !  Loop counter
     $          num_points,    !  Number of points in the transform
     $          direction      !  Direction of transform 1 for forward,
                               ! -1 for inverse

        COMPLEX X( 0 : MAX_NUM_POINTS )  !  Array of complex data points
                                         !  to be transformed.


C -------------------------------------------------------------------------
C |                          PROGRAM CODE                                 |
C -------------------------------------------------------------------------

C
C    Read the number of points in the FFT
C
        WRITE( 6, 100 )
100     FORMAT ( ' Enter number of complex points in transform:  ' )

        READ ( 5 , * ) num_points      ! Free format input



C
C       Decide whether to do the forward or inverse FFT
C

        WRITE( 6, 200 )
200     FORMAT ( //, ' Enter 1 for a forward transform ', /,
     $               ' or -1 for an inverse transform: ' )

        READ ( 5, * ) direction     ! Free format input


C
C       Check to see that the number of points in the FFT
C       is valid.  If not, halt.
C

        IF ( (num_points .LE. 0) .OR. 
     $       (num_points .GT. MAX_NUM_POINTS) ) THEN
                
                WRITE( 6, 300 )
300             FORMAT( ' The number of points is out of range ')
                STOP
        
        END IF



C
C       Read in the complex data points, one by one 
C
        DO i = 0, num_points - 1

            WRITE( 6, 400 ) i
400         FORMAT ( ' Enter point no. ', I3,' (Real, Imag) > ')
            READ ( 5 , * ) X( i )      ! Free format input

        END DO


C
C       Print out the points just read in.
C

        WRITE( 6, 500 ) num_points
500     FORMAT ( //, ' num_points = ', I10, / )

        WRITE( 6, 600 ) direction
600     FORMAT ( ' direction =  ', I10, // )

        DO i = 0, num_points - 1
                
            WRITE( 6 , 700 ) i , X ( i )
700         FORMAT ( ' Point no. ', I3, ' = ( ', 2G22.14E3, ') ' )

        END DO


C
C       Call the FFT subroutine.
C
        CALL FFT( num_points, X, direction )


C
C       Print the transform results.
C
        WRITE( 6, 800 )
800     FORMAT ( //, ' The transform of the input data is . . . ', // )


        DO i = 0, num_points - 1
                
            WRITE( 6, 900 ) i , X( i )
900         FORMAT (' Point No. ', I3, '= (', 2G22.14E3, ') ' )

        END DO


C
C       Call the FFT subroutine with -direction to do the inverse transform.
C
        CALL FFT( num_points, X, -direction )



C
C       Print the inverse transform coefficients.
C
        WRITE ( 6, 1000 )
1000    FORMAT ( //,' The inverse transform ',
     $               'of the transform above is . . .', // )


        DO i = 0, num_points - 1
                
            WRITE ( 6, 1100 ) i , X( i )
1100        FORMAT (' Point No. ', I3, '= (', 2G22.14E3, ') ' )

        END DO



C
C  Test the error checking in the FFT routine.
C

C  Number of points is too large.  Currently, MAX_TABLE_SIZE in
C  subroutine FFT is 20, so we can transform up to 2 ** 21 points.

        PRINT *, ' Calling FFT with too many points.'

        CALL FFT( 2 ** 22, X, 1 )


C  Number of points is less than 2.

        PRINT *, ' Calling FFT with 1 point.'

        CALL FFT( 1, X, 1 )


C  Calling FFT with 2^ 15 + 1 points (not a power of 2)

        PRINT *, ' Calling FFT with 2 ^ 15 + 1 points'

        CALL FFT( 2 * 15 + 1, X, 1 )


C  Direction is not 1 or -1.

        PRINT *, ' Calling FFT with direction = 2'

        CALL FFT( 16, X, 2)


        STOP
        END   ! of program fftd
