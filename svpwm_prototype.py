import numpy as np
from definitions import *

"""

    Prototype of the SVPWM switch time computation in C.


    SQRT shift should be as high as possible without causing an overflow.
    
    Using
    _T_SHIFT = 11
    max amplitude U = 2<<11

    31 - 11 - 11 = 9

    9 -> overflow
    8 -> overflow
    7 -> works
    6 -> using this in the working code

"""


_T_SHIFT = 11
_T = np.int32(1 << _T_SHIFT)

SQRT_SHIFT = 6
SHIFT = SQRT_SHIFT + _T_SHIFT
TWO_SHIFTED = 2 << (SQRT_SHIFT + 2 * _T_SHIFT)
ONE_SHIFTED = 1 << (SQRT_SHIFT + 2 * _T_SHIFT)
SQRT3_SHIFTED = np.int32(np.round(np.sqrt(3) * (1 << SQRT_SHIFT)))


def svpwm(q31_u_alpha, q31_u_beta, q31_angle):
    global _T, SQRT3_SHIFTED, SQRT_SHIFT    
    
    # scaling with _T -> mapping from unity amplitude to _T amplitude
    # U / _T -> amplitude adjustment according to U
    Ualpha = q31_u_alpha * _T * SQRT3_SHIFTED
    Ubeta = (q31_u_beta * _T) << SQRT_SHIFT

    if q31_angle > 0:
        if q31_angle < Q31_DEGREE_PLUS60:
            sector = 1
        elif q31_angle < Q31_DEGREE_PLUS120:
            sector = 2
        else:
            sector = 3
    else:
        if q31_angle < Q31_DEGREE_MINUS120:
            sector = 4
        elif q31_angle < Q31_DEGREE_MINUS60:
            sector = 5
        else:
            sector = 6
    
    #print(sector, angle, angle_q31)

    
    if sector == 1 or sector == 4:
        Tph1 = (Ualpha + Ubeta + TWO_SHIFTED)  >> (SHIFT + 2)
        Tph2 = (-Ualpha + 3 * Ubeta + TWO_SHIFTED) >> (SHIFT + 2)
        Tph3 = (-Ualpha - Ubeta + TWO_SHIFTED) >> (SHIFT + 2)
    elif sector == 2 or sector == 5:
        Tph1 = (Ualpha + ONE_SHIFTED) >> (SHIFT + 1)
        Tph2 = (Ubeta + ONE_SHIFTED) >> (SHIFT + 1)
        Tph3 = (ONE_SHIFTED - Ubeta) >> (SHIFT + 1)
    else: #if sector == 3 or sector == 6:
        Tph1 = (Ualpha - Ubeta + TWO_SHIFTED) >> (SHIFT + 2)
        Tph2 = (-Ualpha + Ubeta + TWO_SHIFTED) >> (SHIFT + 2)
        Tph3 = (-Ualpha - 3 * Ubeta + TWO_SHIFTED) >> (SHIFT + 2)


    return Tph1, Tph2, Tph3
