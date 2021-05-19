import numpy as np
import matplotlib.pyplot as plt

from definitions import *
from svpwm_prototype import *

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


#print(SQRT3_SHIFTED, _T, ONE_SHIFTED, TWO_SHIFTED)
#U = np.int32(1 << 11)
U = np.int(2048 * 0.76)



Tph1 = np.zeros(360)
Tph2 = np.zeros(360)
Tph3 = np.zeros(360)

ualpha = np.zeros(360)
ubeta = np.zeros(360)

for angle in range(0, 360):
#for angle in range(276, 277):


    q31_angle = np.int32(angle * Q31_DEGREE)
    q31_u_alpha = np.int32(np.cos(np.deg2rad(angle)) * U)
    q31_u_beta = np.int32(np.sin(np.deg2rad(angle)) * U) 

    Tph1[angle], Tph2[angle], Tph3[angle] = svpwm(q31_u_alpha, q31_u_beta, q31_angle)
    #print(q31_u_alpha, q31_u_beta, Tph2[angle])



#plt.plot(ualpha, label='ualpha', color='blue')
#plt.plot(ubeta, label='ubeta', color='red')

plt.plot(Tph1, label='t1', color='blue')
plt.plot(Tph2, label='t2', color='red')
plt.plot(Tph3, label='t3', color='black')
plt.xticks([0,60,120,180,240,300,360])
#plt.title('l')
plt.legend()
plt.grid()
plt.show()


    





