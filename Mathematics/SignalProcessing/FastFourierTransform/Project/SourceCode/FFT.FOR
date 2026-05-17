C    -------------------------------------------------------------------------
C    |  File name: fft.for               Sean O'Connor               9-23-87 |
C    ------------------------------------------------------------------------- 

C    -------------------------------------------------------------------------
C    |  VAX 11/785                 VMS 4.5         VAX EXTENDED FORTRAN 77   |
C    -------------------------------------------------------------------------

C 
C  ****************************************************************************
C  *                                                                          *
C  *                            FFT                                           *
C  *                                                                          *
C  ****************************************************************************
C
C
C  DESCRIPTION
C
C      This program does an in-place one dimensional complex discrete Fourier
C      transform.  It uses an FFT algorithm for a number of input points which
C      is a power of two.
C
C
C  INPUT 
C
C      N,  The number of complex points to be transformed.
C          N is a power of 2.  N must be at least 2;  it
C          must not exceed the dimension of array X, or the 
C          maximum size of the sine and cosine table.  (See 
C          below).
C
C      X,  The array holding the complex data X( k )
C          for k = 0, 1, . . ., N - 1 which is to be
C          transformed.  It is dimensioned in the calling
C          program.  Only the array address is passed to 
C          this subroutine.
C
C      D,  The direction of the FFT. D is 1 for a 
C          forward transform and -1 for an inverse
C          transform.
C
C
C  OUTPUT
C
C      X,  On output, X holds the complex Fourier coefficients
C          ^
C          X( k ) for k = 0, 1, . . ., N - 1.
C
C      Warning messages to the terminal under these conditions:
C
C          (1)  D is not 1 or -1
C          (2)  N is less than 2.
C          (3)  N is greater than the sine table can handle.
C          (4)  N is not a power of 2.
C
C
C  CALLING SEQUENCE
C
C         CALL FFT ( N, X, D )
C
C
C  EXAMPLE 
C
C      DIMENSION X( 0 : 3 )        ! 4 point FFT
C
C      N = 4                       ! 4 point FFT
C      D = 1                       ! Forward transform
C
C      CALL FFT( N, X, D )         ! Do the FFT
C
C      D = -1                      ! Do an inverse FFT
C
C      CALL FFT( N, X, D )
C
C   Suppose X contains the data
C
C   X ( 0 )  =  1  +  i
C   X ( 1 )  =  2  +  2 i
C   X ( 2 )  =  3  +  3 i
C   X ( 3 )  =  4  +  4 i
C 
C   then the forward FFT returns
C
C   X ( 0 ) =   5  +  5 i
C   X ( 1 ) =  -2
C   X ( 2 ) =  -1  -    i
C   X ( 3 ) =      -  2 i
C
C   and the inverse FFT returns the original data.
C
C
C  METHOD
C                                ^
C       The Fourier coefficients X( k ) are defined for k = 0, . . ., N - 1
C       by the formula
C
C                             N - 1               2 Pi i
C       ^             1       ____             -  ------ j k
C       X( k ) =  ---------   \                     N
C                   -----     /      X( j )  e
C                \ /  N       ----
C                 v           j = 0
C
C       where e is 2.1718 . . ., Pi = 3.14159. . . and i is the square root
C       of -1.
C
C       This is the formula for the forward transform.  The inverse transform
C       is the same, except that the minus sign in the exponent above is a
C       plus sign instead.
C                                    ---
C       The normalizing factor 1 / \/ N  in front was picked so that the
C       forward and inverse transforms look the same.
C
C
C  The particular type of FFT algorithm we use is a
C
C                             complex,
C                           two to the N,
C                     decimation in  frequency,
C               input in order, output bit reversed
C
C  type of FFT.  It is described in the book
C
C               THE FAST FOURIER TRANSFORM,
C               F. Oran Brigham, Prentice Hall, 1974
C
C
C  BUGS
C
C      The bit-reversal routine could be made faster by using the
C      VAX FORTRAN 77 library routines for testing, setting, clearing and
C      shifting bits:  BTEST, IBSET, IBCLR, ISHFT.
C
C      You might want to use double precision complex numbers to get more
C      accuracy.
C
C  ****************************************************************************
C  *                                                                          *
C  ****************************************************************************


        SUBROUTINE FFT( N, X, D )

        IMPLICIT NONE   ! Force declaration of all variables.


C    -------------------------------------------------------------------------
C    |                            MACRO DEFINITIONS                          |
C    ------------------------------------------------------------------------- 

        INTEGER MAX_TABLE_SIZE
        REAL    PI

        PARAMETER ( PI = 3.1415926535897932385 )

C       We must set the size of the sine and cosine table used in the FFT.
C       The table is called starting_multiplier.
C     
C       Suppose MAX is the largest FFT we would ever want
C       to perform.  Then 
C
C       MAX_TABLE_SIZE  =  LOG ( MAX ) - 1
C                             2
C
C       is the size of the table.  This table can be used by the
C       FFT for any number of points from 2 up to MAX.
C
C       For example, if MAX_TABLE_SIZE = 14, then we can transform
C       anywhere from 2 to 2 ** 15 = 32,768 points, using the same 
C       sine and cosine table.
C

        PARAMETER ( MAX_TABLE_SIZE  = 20 )
        

C -------------------------------------------------------------------------
C |                          CALLING ARGUMENTS                            |
C -------------------------------------------------------------------------

        INTEGER N            !  Number of points in transform

        COMPLEX X( 0 : * )   !  Complex data to be transformed

C    Array X is dimensioned in the calling program.  Only its starting 
C    address is passed into this subroutine.

        INTEGER D            !  Transform direction:  1 for a forward 
                             !  transform, -1 for an inverse transform.


C -------------------------------------------------------------------------
C |                          LOCAL VARIABLES                              |
C -------------------------------------------------------------------------

C  A column refers to a column of the FFT signal flow graph.  A group is
C  a collection of butterflies which have the same multiplier W^p.  A
C  butterfly is the basic computational unit of the FFT.

        INTEGER log_of_n,          ! Log base 2 of the number of points, N.
     $          column,            ! Current column.
     $          number_of_groups,  ! Number of groups in a column.
     $          group,             ! Current group number.
     $          start_of_group,    ! Array index of first butterfly in group.
     $          end_of_group,      ! Array index of last butterfly in group.
     $          butterfly_height,  ! Height of a butterfly.
     $          offset,            ! Lower branch of a butterfly.
     $          i,                 ! Loop counter.  Upper branch of butterfly.
     $          rev_i,             ! Bit-reversed array index i.
     $          REVERSE_BITS       ! Bit reversal function.


        COMPLEX product,     ! Temporary storage in a butterfly calculation.
     $          temp,        ! Same as above.
     $          increment,   ! Difference between current multiplier and next.
     $          multiplier   ! The multiplier W^p for a group of butterflies.

        COMPLEX starting_multiplier( 0 : MAX_TABLE_SIZE )   ! Table of sines
                                                            ! and cosines.

        REAL normalizer,     ! 1/\/N normalizing factor.
     $       angle           ! Current angle in sine and cosine table.


        LOGICAL called_already   ! .TRUE. if this is the second call or
                                 ! later call to this subroutine.


C -------------------------------------------------------------------------
C |                          SUBROUTINE CODE                              |
C -------------------------------------------------------------------------

C
C  Initialize the variable called_already to .FALSE. at compile time.
C  Change it to .TRUE. after the first call to this subroutine.
C  Save the value so it does not get destroyed after returning from
C  this subroutine.
C
        SAVE called_already
        DATA called_already /.FALSE./


C
C       Compute log base 2 of N. Perturb slightly to avoid roundoff error.
C       For example, INT( 4.99999999999 ) = 4 (wrong!), but
C       INT( 4.999999999 + .01 ) = 5 (correct!)
C
        log_of_n = INT( ALOG( FLOAT( N ) ) / ( ALOG( 2.0 ) )  + .01 )



C
C  Error checking.  Print a message to the terminal if any one of these
C  conditions is true:
C
C      (1) D is not 1 or -1.
C      (2) N < 2.
C      (3) log2( N ) > MAX_TABLE_SIZE + 1.
C      (4) N is not a power of 2.
C

        IF ((D .NE. 1) .AND. (D .NE. -1)) THEN

            PRINT *, ' ERROR ---  D is not 1 or -1'
            RETURN

        ELSE IF (N .LT. 2) THEN

            PRINT *, ' ERROR ---  N is less than 2. '
            RETURN

        ELSE IF ( (log_of_n - 1) .GT. MAX_TABLE_SIZE) THEN

            PRINT *, ' ERROR ---  N is larger than the sine table can'
            PRINT *, ' handle.  Increase the parameter MAX_TABLE_SIZE'
            PRINT *, ' in this subroutine and recompile.'

            RETURN

        ELSE IF ( (2 ** log_of_n) .NE. N ) THEN

            PRINT *, ' ERROR --- N is not a power of 2.'
            RETURN

        END IF


C
C  If called_already is false, generate the sine and cosine table for
C  the first time, then set called_already to .TRUE.  Now later calls to 
C  the subroutine don't recreate the sine and cosine table.
C

        IF (.NOT. called_already) THEN

            DO i = 0, MAX_TABLE_SIZE - 1
                   
                angle = - PI / ( 2 ** i )
                starting_multiplier( i ) = CEXP( CMPLX(0.0 , angle) )

            END DO

            called_already = .TRUE.

        END IF



C
C       Compute the FFT according to its signal flow graph with 
C       computations arranged into butterflies, groups of butterflies
C       with the same multiplier, and columns.
C
        butterfly_height = N / 2
        number_of_groups = 1


        DO column = 1, log_of_n

            multiplier = starting_multiplier( column - 1 )

C
C       Modify starting multiplier W^p when computing the inverse transform.
C
            IF ( D .EQ. -1 ) THEN

                multiplier = CONJG( multiplier )

            END IF

            increment = multiplier


C
C       Compute the first group.
C
            DO i = 0, butterfly_height - 1

                offset = i + butterfly_height

                temp        =  X( i ) + X( offset ) 
                X( offset ) =  X( i ) - X( offset )
                X( i )      =  temp

            END DO  ! i


C
C       Now do the remaining groups.
C
            DO group = 2, number_of_groups

                start_of_group = REVERSE_BITS( group - 1, log_of_n )
                end_of_group = start_of_group +
     $                         butterfly_height - 1


C       Compute all butterflies in a group.

                DO i = start_of_group, end_of_group

                    offset   =  i + butterfly_height
                    product  =  x( offset ) * multiplier

                    temp         = X( i ) + product
                    X( offset )  = X( i ) - product
                    X( i )       = temp

                END DO  ! i

                multiplier = multiplier * increment

            END DO ! group

            butterfly_height = butterfly_height / 2
            number_of_groups = number_of_groups * 2 

        END DO ! column


C
C       Normalize the results and permute them into order, two at a time.
C
        normalizer = 1 / SQRT( FLOAT( N ) )


        DO i = 0, N - 1

            rev_i = REVERSE_BITS( i, log_of_n )

            IF ( rev_i .GT. i ) THEN   ! exchange not yet done.

                temp       =  X( i ) 
                X( i )     =  X( rev_i ) * normalizer
                X( rev_i ) =  temp       * normalizer

           ELSE IF ( rev_i .EQ. i ) THEN  ! exchange with itself.

                X( i ) = X( i ) * normalizer

           END IF
        
        END DO ! i


        RETURN
        END   !  subroutine FFT



C  ****************************************************************************
C  *                                                                          *
C  *                            REVERSE_BITS                                  *
C  *                                                                          *
C  ****************************************************************************
C
C  DESCRIPTION
C
C      This function reverses the order of the bits in a number.
C
C  
C  INPUT
C      
C       n              The number whose bits are to be reversed.
C
C       num_bits       The number of bits in N, counting leading zeros.
C
C
C  OUTPUT
C  
C       REVERSE_BITS   The number N with all its num_bits bits reversed.
C
C
C  EXAMPLE
C
C       REVERSE_BITS( (10)  , 2 ) = (01) = 1, but
C                         2             2
C
C       REVERSE_BITS( (10)  , 3 ) = REVERSE_BITS( (010)  , 3 ) = (010)  = (10)
C                         2                            2              2       2
C
C       = 10
C
C
C  METHOD
C
C       The algorithm works by a method similar to base conversion.
C       As the low order bits are broken off, one by one, they are
C       multiplied by 2 and accumulated to generate the bit-reversed
C       number.
C
C
C  BUGS
C
C      The bit-reversal routine could be made faster by using the
C      VAX FORTRAN 77 library routines for testing, setting, clearing and
C      shifting bits:  BTEST, IBSET, IBCLR, ISHFT.
C
C
C  ****************************************************************************
C  *                                                                          *
C  ****************************************************************************

        INTEGER FUNCTION REVERSE_BITS( n, num_bits )

        IMPLICIT NONE


C -------------------------------------------------------------------------
C |                          CALLING ARGUMENTS                            |
C -------------------------------------------------------------------------

        INTEGER n, num_bits


C -------------------------------------------------------------------------
C |                          LOCAL VARIABLES                              |
C -------------------------------------------------------------------------

        INTEGER bit_num,      ! Current bit number.
     $          remainder,    ! Bits remaining to be reversed.
     $          reversed_n,   ! Bit-reversed value of n.
     $          bit,          ! The current least significant bit.
     $          MOD, INT      ! Function return types.


C -------------------------------------------------------------------------
C |                          SUBROUTINE CODE                              |
C -------------------------------------------------------------------------

        remainder = n                      ! Load n.
        reversed_n = 0                     ! Clear buffer for bit-reversed n.

        DO bit_num = 1, num_bits

            bit        = MOD( remainder, 2 )   ! Next least significant bit.
            reversed_n = bit + 2 * reversed_n  ! Shift left and add to buffer.
            remainder  = INT( remainder / 2 )  ! Remaining bits.

        END DO

        REVERSE_BITS = reversed_n

        RETURN
        END     !  subroutine REVERSE_BITS
