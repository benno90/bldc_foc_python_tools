import numpy as np
import matplotlib.pyplot as plt


"""

    SVPWM switch time computations according to the ST User Manual UM1052
        "STM32F PMSM single/dual FOC SDK v4.3"


"""

FLOAT = 1

if FLOAT:
    _SQRT3 = np.sqrt(3)
    _T = 1.0
else:
    _SQRT3 = 28
    #_T = 1 << 11
    _T = 2028


switchtime = np.zeros(3)


def svpwm(q31_u_alpha, q31_u_beta):
    global _T, _SQRT3, switchtime
    if FLOAT:
        q31_U_alpha = (_SQRT3 *_T * q31_u_alpha)
    else:
        q31_U_alpha = (_SQRT3 *_T * q31_u_alpha) >> 4

    #q31_U_beta = -_T * q31_u_beta
    q31_U_beta = _T * q31_u_beta
    X = q31_U_beta

    if FLOAT:
        Y = (q31_U_alpha+q31_U_beta) / 2.0  #>>1
        Z = (q31_U_beta-q31_U_alpha) / 2.0  #>>1
    else:
        Y = (q31_U_alpha+q31_U_beta) >> 1
        Z = (q31_U_beta-q31_U_alpha) >> 1

    #Sector 1 & 4
    if ((Y>=0 and Z<0 and X>0) or (Y < 0 and Z>=0 and X<=0)):
        if FLOAT:
            switchtime[0] = ((_T+X-Z) / (2.0 * _T)) + (_T / 2.0)
            switchtime[1] = switchtime[0] + Z / _T
            switchtime[2] = switchtime[1] - X / _T
        else:
            switchtime[0] = ((_T+X-Z)>>12) + (_T>>1)
            switchtime[1] = switchtime[0] + (Z>>11)
            switchtime[2] = switchtime[1] - (X>>11)

    #Sector 2 & 5
    if ((Y>=0 and Z>=0) or (Y<0 and Z<0) ):
        if FLOAT:
            switchtime[0] = ((_T+Y-Z) / (2.0 * _T)) + (_T / 2.0)
            switchtime[1] = switchtime[0] + (Z / _T)
            switchtime[2] = switchtime[0] - (Y / _T)
        else:
            switchtime[0] = ((_T+Y-Z)>>12) + (_T>>1)
            switchtime[1] = switchtime[0] + (Z>>11)
            switchtime[2] = switchtime[0] - (Y>>11)

    #Sector 3 & 6
    if ((Y<0 and Z>=0 and X>0) or (Y >= 0 and Z<0 and X<=0)):
        if FLOAT:
            switchtime[0] = ((_T+Y-X) / (2.0 * _T)) + (_T / 2.0)
            switchtime[2] = switchtime[0] - (Y / _T)
            switchtime[1] = switchtime[2] + (X / _T)
        else:
            switchtime[0] = ((_T+Y-X)>>12) + (_T>>1);
            switchtime[2] = switchtime[0] - (Y>>11)
            switchtime[1] = switchtime[2] + (X>>11)



t1 = []
t2 = []
t3 = []

for i in range(0, 360):
    alpha = i * np.pi / 180.0
    if FLOAT:
        A = 1.0
        u_alpha = np.cos(alpha) * A
        u_beta = np.sin(alpha) * A
    else:
        A = 1980
        u_alpha = int(np.cos(alpha) * A)
        u_beta = int(np.sin(alpha) * A)
    svpwm(u_alpha, u_beta)
    t1.append(switchtime[0])
    t2.append(switchtime[1])
    t3.append(switchtime[2])




plt.plot(t1, label='t1', color='blue')
plt.plot(t2, label='t2', color='red')
#plt.plot(t3, label='t3', color='grey')
plt.title('lishui svpwm')
plt.legend()
plt.grid()
plt.show()
