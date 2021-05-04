import numpy as np
import matplotlib.pyplot as plt

from definitions import *

"""

    This script simulates the motor angle estimation with a phase locked loop (PLL).
    It can be used to tune the proportional and integral constants in the PI - controller.



"""


# ---------------------------------- bike parameter

TIC_FREQ = 16000                # pwm frequency
GEAR_RATIO = 1                  # 
POLE_PAIRS = 18                 #
WHEEL_CIRCUMFERENCE = 2.2       # in meter

# ---------------------------------- velocity profile

# currently there is only one profile 
VELOCITY_PROFILE = 1

# ----------------------------------

EXTRAPOLATION_METHOD = 1  # 1 -> linear extrapolation,   2 -> quadratic extrapolation

# ----------------------------------
# 

def TIME_TO_TICS(time):
    return int(time * TIC_FREQ)

def TICS_TO_TIME(tics):
    return float(tics / TIC_FREQ)

def DEGREE_TO_Q31DEGREE(phi):
    return phi * Q31_DEGREE

def Q31DEGREE_TO_DEGREE(phi):
    return int(phi / Q31_DEGREE)

def velocity_profile(time):
    # ret: velocity [km / h] (float)
    # param: time [s] (float)
    if VELOCITY_PROFILE == 1:
        if time < 6.0:
            return 50 * (time / 6.0)
        elif time < 10.0:
            return 50
        elif time < 12.0:
            t = time - 10.0
            return 45 * (1.0 - (t / 2.0)) + 5.0
        elif time < 17.0:
            return 5.0
        elif time < 37.0:
            t = time - 17.0
            return 25.0 + 20.0 * np.sin((2.0 * t / 20.0) * np.pi * 2.0 - np.pi / 2.0)
        elif time < 40.0:
            return 5.0
        else: 
            return 0.0
    else:
        assert(False)

def position_to_phi(x):
    # param x: position in [m]
    # ret: electrical angle in degrees
    phi = x / WHEEL_CIRCUMFERENCE * 360.0 * GEAR_RATIO * POLE_PAIRS
    return phi

def velocity_to_electrical_frequency(v):
    # param v: velocity im m/s
    # ret : frequency in Hz
    global WHEEL_CIRCUMFERENCE, POLE_PAIRS, GEAR_RATIO
    omega = v / WHEEL_CIRCUMFERENCE # wheel frequency in Hz
    omega = omega * POLE_PAIRS * GEAR_RATIO # electrical frequency in Hz
    return omega


# ----------------------------------
# some computations

print('tics for 6 kmh')
x = TIC_FREQ / (velocity_to_electrical_frequency((6.0 / 3.6)) * 6)
print(x)



print('six step threshold')

v_kmh = 10
hall_freq = velocity_to_electrical_frequency((v_kmh / 3.6) * 6)
tim2_tics = 500000 / hall_freq
print(tim2_tics)

#exit(0)

# ----------------------------------





def get_p_factor_pll(delta_tic):

    # constant p factor -> comment in order to use variable factor
    return 1 << 8

    # variable p factor
    f1 = int(250)   # large divisor at high speeds (few tics)
    f2 = int(250)    # small divisor at low speeds (more tics)
    df = f2 - f1
    t1 = int(40)
    t2 = int(296)
    dt = t2 - t1
    if delta_tic < t1:
        return f1
    elif delta_tic > t2:
        return f2
    else:
        d = delta_tic - t1
        return f1 + (d * df) // dt

def get_i_factor_pll(delta_tic):

    # constant i factor -> comment in order to use variable factor
    return 1 << 9

    # variable i factor
    f1 = int(500)
    f2 = int(500)
    df = f2 - f1
    t1 = int(40)
    t2 = int(296)
    dt = t2 - t1
    if delta_tic < t1:
        return f1
    elif delta_tic > t2:
        return f2
    else:
        d = delta_tic - t1
        return f1 + (d * df) // dt



pll_p_ = 0
pll_i_ = 0

def speed_pll(phi_ist, phi_soll, p_f_pll, i_f_pll):
    global pll_p_, pll_i_
    delta = int(phi_soll - phi_ist)
    #pll_p_ = (delta >> p_f_pll)
    pll_p_ = (delta / p_f_pll)
    #pll_i_ += (delta >> i_f_pll)
    pll_i_ += (delta / i_f_pll)
    return pll_p_ + pll_i_



next_hall_event = 60
phi_pll = int(0)
phi_per_tic = 0

phi_extrapolated_base = int(0)
phi_per_tic_extra = int(0)
phi_extrapolated = int(0)
prev_tic = int(0)
prev_prev_tic = int(0)


T_START = 0.0
T_END = 40.0
DELTA_TIME = T_END - T_START
DT = 1.0 / TIC_FREQ
N = int(DELTA_TIME * TIC_FREQ) + 1

print('T_END =', T_END)
print('N =', N)
print('DT =', DT)


TIME = np.linspace(T_START, T_END, N)
TIC = np.arange(N)
VELOCITY_KPH = [velocity_profile(t) for t in TIME]

# smooth profile
assert(len(VELOCITY_KPH) == N)
for s in range(0, 3):
    for i in range(1, N):
        VELOCITY_KPH[i] =  VELOCITY_KPH[i-1] * 0.999 + VELOCITY_KPH[i] * 0.001


VELOCITY_MPS = [(v / 3.6) for v in VELOCITY_KPH]

POSITION = np.zeros(N)
for i in range(1, N):
    POSITION[i] = POSITION[i-1] + DT * VELOCITY_MPS[i]

#plt.plot(TIME, VELOCITY_KPH, label='velocity (kmh)')
#plt.plot(TIME, POSITION, label='position (m)')
#plt.legend()
#plt.show()
#exit(0)



PHI_PLL = np.zeros(N)
PHI_EXTRA = np.zeros(N)
PHI = np.zeros(N)
ERROR_PLL = np.zeros(N)
ERROR_EXTRA = np.zeros(N)
HALL_EVT = []
HALL_EVT_TIC = []
DELTA_TIC = []


first_hall_event_flag = 1
        
hall_count = 0

for tic in range(0, N):
    time = TIME[tic]
    v = VELOCITY_MPS[tic]
    x = POSITION[tic]
    phi_degree = position_to_phi(x)
    phi_q31degree = int(DEGREE_TO_Q31DEGREE(phi_degree))

    if(phi_degree >= next_hall_event):
        hall_count += 1
        HALL_EVT.append(time)
        HALL_EVT_TIC.append(tic)
        delta_tic = tic - prev_tic
        DELTA_TIC.append(delta_tic)

        # PLL
        if first_hall_event_flag or v < (4.0 / 3.6):
            # init pll_i_
            pll_i_ = Q31_DEGREE * 60 / delta_tic
            phi_per_tic = Q31_DEGREE * 60 / delta_tic
            phi_pll = np.floor(phi_q31degree)
        else:             
            phi_per_tic = speed_pll(phi_pll, phi_q31degree, get_p_factor_pll(delta_tic), get_i_factor_pll(delta_tic))

        # extrapolation
        if EXTRAPOLATION_METHOD == 2:  # quadratic extrapolation
            phi_extrapolated_base = np.floor(phi_q31degree)
            if hall_count > 2:
                t2 = np.int(prev_prev_tic - tic)
                t1 = np.int(prev_tic - tic)
                #print(hall_count, t1, t2)
                phi_2 = np.int(-120 * Q31_DEGREE)
                phi_1 = np.int(-60 * Q31_DEGREE)
                B = (t1 * t1 * phi_2 - t2 * t2 * phi_1) // ( ( t1 - t2) * t1 * t2 )
                C = (t2 * phi_1 - t1 * phi_2) // ( ( t1 - t2) * t1 * t2 )

                #print(t1, t2, B, C)
            else:
                C = 0
                B = (60.0 * Q31_DEGREE) / float(delta_tic)

        elif EXTRAPOLATION_METHOD == 1:  # linear extrapolation
            phi_extrapolated_base = np.floor(phi_degree)
            phi_per_tic_extra = (60.0) / float(delta_tic)
        else:
            assert(False)

        prev_prev_tic = prev_tic
        prev_tic = tic
        next_hall_event += 60
        # --------------- end hall evt processing


    # extrapolation

    if first_hall_event_flag == 1:
        phi_extrapolated = 60
    else:
        if EXTRAPOLATION_METHOD == 2:
            t = (tic - prev_tic)
            phi_extrapolated_q31 = phi_extrapolated_base + B * t + C * t * t
            phi_extrapolated = Q31DEGREE_TO_DEGREE(phi_extrapolated_q31)
        elif EXTRAPOLATION_METHOD == 1:
            phi_extrapolated = phi_extrapolated_base + (tic - prev_tic) * phi_per_tic_extra
        else:
            assert(False)

    PHI_EXTRA[tic] = phi_extrapolated
    ERROR_EXTRA[tic] = phi_extrapolated - phi_degree

    # pll

    phi_pll += phi_per_tic
    phi_pll_degree = Q31DEGREE_TO_DEGREE(phi_pll)
    PHI_PLL[tic] = phi_pll_degree
    PHI[tic] = phi_degree
    ERROR_PLL[tic] = phi_pll_degree - phi_degree

    if phi_degree >= 60:
        first_hall_event_flag = 0






plt.subplot(211)
plt.plot(TIME, PHI, label='phi')
plt.plot(TIME, PHI_PLL, label='phi_pll')
plt.plot(TIME, PHI_EXTRA, label='phi_extra')
plt.plot(HALL_EVT, [0]*len(HALL_EVT), label='hall_evt', marker=2, color='black')
plt.legend()
plt.subplot(212)
plt.plot(TIME, VELOCITY_KPH, label='velocity', color='green')
plt.plot(TIME, ERROR_PLL, label='error pll', color='blue')
#plt.plot(HALL_EVT, DELTA_TIC, label='delta_tic', color='black')
plt.plot(TIME, ERROR_EXTRA, label='error extra', color='red')
#plt.plot(HALL_EVT, [0]*len(HALL_EVT), label='hall_evt', marker=2, color='black')
plt.legend()
plt.show()


