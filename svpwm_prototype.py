import numpy as np
import matplotlib.pyplot as plt

from definitions import *


"""


    Prototype of the SVPWM switch time computation in C.


    Max SQRT shift
    
    max U -> 11
    _T -> 11

    31 - 11 - 11 = 9

    9 -> overflow
    8 -> overflow
    7 -> works
    6 -> using this in the working code

"""
print('q31 degree: ', Q31_DEGREE)
print('+60 ° ', Q31_DEGREE_PLUS60)
print('+120 °', Q31_DEGREE_PLUS120)
print('+180 °',Q31_DEGREE_PLUS180)
print('-60 °', Q31_DEGREE_MINUS60)
print('-120 °', Q31_DEGREE_MINUS120)


#U = np.int32(1 << 11)
U = 200


SQRT_SHIFT = 6
SHIFT = SQRT_SHIFT + 11
TWO_SHIFTED = 2 << (SQRT_SHIFT + 22)
ONE_SHIFTED = 1 << (SQRT_SHIFT + 22)
SQRT3_SHIFT = np.int32(np.sqrt(3) * (1 << SQRT_SHIFT))

_T = np.int32(1 << 11)

print(SQRT3_SHIFT, _T, ONE_SHIFTED, TWO_SHIFTED)

Tph1 = np.zeros(360)
Tph2 = np.zeros(360)
Tph3 = np.zeros(360)

ualpha = np.zeros(360)
ubeta = np.zeros(360)

for angle in range(0, 360):

    q31_angle = np.int32(angle * Q31_DEGREE)

    # scaling with _T -> mapping from unity amplitude to _T amplitude
    # U / _T -> amplitude adjustment according to U
    Ualpha = np.int32(np.cos(np.deg2rad(angle)) * U * _T) * SQRT3_SHIFT
    ualpha[angle] = Ualpha
    Ubeta = np.int32(np.sin(np.deg2rad(angle)) * U * _T) << SQRT_SHIFT
    ubeta[angle] = Ubeta

    #one = np.int32(ONE_SHIFT * _T * _T)
    #two = np.int32(TWO_SHIFT * _T * _T)

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
        Tph1[angle] = (Ualpha + Ubeta + TWO_SHIFTED)  >> (SHIFT + 2)
        Tph2[angle] = (-Ualpha + 3 * Ubeta + TWO_SHIFTED) >> (SHIFT + 2)
        Tph3[angle] = (-Ualpha - Ubeta + TWO_SHIFTED) >> (SHIFT + 2)
    if sector == 2 or sector == 5:
        Tph1[angle] = (Ualpha + ONE_SHIFTED) >> (SHIFT + 1)
        Tph2[angle] = (Ubeta + ONE_SHIFTED) >> (SHIFT + 1)
        Tph3[angle] = (ONE_SHIFTED - Ubeta) >> (SHIFT + 1)
    if sector == 3 or sector == 6:
        Tph1[angle] = (Ualpha - Ubeta + TWO_SHIFTED) >> (SHIFT + 2)
        Tph2[angle] = (-Ualpha + Ubeta + TWO_SHIFTED) >> (SHIFT + 2)
        Tph3[angle] = (-Ualpha - 3 * Ubeta + TWO_SHIFTED) >> (SHIFT + 2)


#plt.plot(ualpha, label='ualpha', color='blue')
#plt.plot(ubeta, label='ubeta', color='red')

plt.plot(Tph1, label='t1', color='blue')
plt.plot(Tph2, label='t2', color='red')
#plt.plot(Tph3, label='t3', color='black')
plt.xticks([0,60,120,180,240,300,360])
#plt.title('l')
plt.legend()
plt.grid()
plt.show()


    





