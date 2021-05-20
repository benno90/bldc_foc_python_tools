

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.patches import Rectangle

from svpwm_prototype import svpwm, _T
from definitions import *

DEAD_TIME = 32

fig, ax = plt.subplots()
plt.sca(ax)
plt.axis('off')

axcolor = 'lightgoldenrodyellow'
amplitudeAx = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
angleAx = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)

ph1Ax = plt.axes([0.25, 0.75, 0.65, 0.2], title='ph1')
ph2Ax = plt.axes([0.25, 0.5, 0.65, 0.2], title='ph2')
ph3Ax = plt.axes([0.25, 0.25, 0.65, 0.2], title='ph3')

amplitudeSlider = Slider(amplitudeAx, 'amplitude', 0, 1.0, valinit=0.5)
angleSlider = Slider(angleAx, 'angle', 0, 360, valinit=0)


#sO = Slider(axO, 'O', 0, 1, valinit = 1)

def plotSwitchTime(ax, T):
    global DEAD_TIME
    plt.sca(ax)
    ax.clear()

    #t = _T - T

    val = np.zeros(4096)
    valN = np.zeros(4096)
    for i in range(0, 2048):
        if i < T:
            val[i] = 1
            valN[i] = 0
        else:
            val[i] = 0
            valN[i] = 1

    for i in range(0, 2048):
        val[i + 2048] = val[2047 - i]
        valN[i + 2048] = valN[2047 - i]
    
    val_highside = np.copy(val)
    val_lowside = np.copy(valN)

    for i in range(1, 4096):
        # detect rising edge and add dead time on high side signal
        if val[i - 1] == 0 and val[i] == 1:
            for k in range(0, DEAD_TIME):
                l = i + k
                if l < 4096:
                    val_highside[l] = 0
            break

    for i in range(0, 4096):
        # detect falling edge and add dead time on low side signal
        if val[i - 1] == 1 and val[i] == 0:
            for k in range(0, DEAD_TIME):
                l = i + k
                if l < 4096:
                    val_lowside[l] = 0
            break


    plt.axis('off')
    plt.plot(val_highside, color='red', linewidth=3, label='highside')
    plt.plot(val_lowside, color='blue', linewidth=3, label='lowside')
    plt.plot(val, color='yellow', linewidth=1, label='reference')

    if ax == ph3Ax:
        plt.legend()


def plotADC_sample(ax, CCR):
    ADC_SAMPLE_TIME = 84
    ax.add_patch(Rectangle((CCR, 0), ADC_SAMPLE_TIME, 1.3))


# dyn_adc_state 1 -> measure phase 1 & 2
# dyn_adc_state 2 -> measure phase 2 & 3
# dyn adc_state_3 -> measure phase 3 & 1
def my_dyn_adc_state(switchtime):
    TRIGGER_DEFAULT = 2048
    TRIGGER_OFFSET_ADC = 100

    tph1N = _T - switchtime[0]
    tph2N = _T - switchtime[1]
    tph3N = _T - switchtime[2]
    
    if switchtime[2] > switchtime[0] and switchtime[2] > switchtime[1]:
        char_dyn_adc_state = 1
        if switchtime[2] > 1500:
            if tph1N > 2 * tph3N and tph2N > 2 * tph3N:
                CCR4 = switchtime[2] - TRIGGER_OFFSET_ADC
            else:
                CCR4 = TRIGGER_DEFAULT + tph3N - TRIGGER_OFFSET_ADC
        else:
            CCR4 = TRIGGER_DEFAULT
    elif switchtime[0] > switchtime[1] and switchtime[0] > switchtime[1]:
        char_dyn_adc_state = 2
        if switchtime[0] > 1500:
            if tph2N > 2 * tph1N and tph3N > 2 * tph1N:
                CCR4 = switchtime[0] - TRIGGER_OFFSET_ADC
            else:
                CCR4 = TRIGGER_DEFAULT + tph1N - TRIGGER_OFFSET_ADC
                #CCR4 = TRIGGER_DEFAULT
        else:
            CCR4 = TRIGGER_DEFAULT
    else:
        char_dyn_adc_state = 3
        if switchtime[1] > 1500:
            if tph1N > 2 * tph2N and tph3N > 2 * tph2N:
                CCR4 = switchtime[1] - TRIGGER_OFFSET_ADC
            else:
                CCR4 = TRIGGER_DEFAULT + tph2N - TRIGGER_OFFSET_ADC
        else:
            CCR4 = TRIGGER_DEFAULT
    
    return char_dyn_adc_state, CCR4


def dyn_adc_state(switchtime):

    #TRIGGER_OFFSET_ADC = 50
    TRIGGER_OFFSET_ADC = 100
    TRIGGER_DEFAULT = 2020

    if switchtime[2] > switchtime[0] and switchtime[2] > switchtime[1]:
        char_dyn_adc_state = 1
        # -90° .. +30°: Phase C at high dutycycles
        if switchtime[2] > 1500:
            CCR4 = switchtime[2] - TRIGGER_OFFSET_ADC
            #CCR4 = switchtime[2] + TRIGGER_OFFSET_ADC
        else:
            CCR4 = TRIGGER_DEFAULT

    if switchtime[0] > switchtime[1] and switchtime[0] > switchtime[2]:
        char_dyn_adc_state = 2
        # +30° .. 150° Phase A at high dutycycles
        if switchtime[0] > 1500:
            CCR4 = switchtime[0] - TRIGGER_OFFSET_ADC
            #CCR4 = switchtime[0] + TRIGGER_OFFSET_ADC
        else:
            CCR4 = TRIGGER_DEFAULT

    if switchtime[1] > switchtime[0] and switchtime[1] > switchtime[2]:
        char_dyn_adc_state = 3
        # +150 .. -90° Phase B at high dutycycles
        if switchtime[1] > 1500:
            CCR4 = switchtime[1] - TRIGGER_OFFSET_ADC
            #CCR4 = switchtime[1] + TRIGGER_OFFSET_ADC
        else:
            CCR4 = TRIGGER_DEFAULT

    return char_dyn_adc_state, CCR4


def updatePlot(x):
    global amplitudeSlider, angleSlider
    angle = np.int32(angleSlider.val)
    #angle = 276
    amplitude = _T * amplitudeSlider.val
    #amplitude = 0.76

    q31_angle = np.int32(angle * Q31_DEGREE)
    q31_u_alpha = np.int32(np.cos(np.deg2rad(angle)) * amplitude)
    q31_u_beta = np.int32(np.sin(np.deg2rad(angle)) * amplitude)

    Tph1, Tph2, Tph3 = svpwm(q31_u_alpha, q31_u_beta, q31_angle)

    plotSwitchTime(ph1Ax, Tph1)
    plotSwitchTime(ph2Ax, Tph2)
    plotSwitchTime(ph3Ax, Tph3)
    #
    ph1Ax.set_title('ph1')
    ph2Ax.set_title('ph2')
    ph3Ax.set_title('ph3')


    switchtime = np.array((Tph1, Tph2, Tph3))
    #char_dyn_adc_state, CCR4 = dyn_adc_state(switchtime)
    char_dyn_adc_state, CCR4 = my_dyn_adc_state(switchtime)

    if char_dyn_adc_state == 1:
        plotADC_sample(ph1Ax, CCR4)
        plotADC_sample(ph2Ax, CCR4)
    if char_dyn_adc_state == 2:
        plotADC_sample(ph2Ax, CCR4)
        plotADC_sample(ph3Ax, CCR4)
    if char_dyn_adc_state == 3:
        plotADC_sample(ph1Ax, CCR4)
        plotADC_sample(ph3Ax, CCR4)

    #print('\n--------------')
    #print(q31_u_alpha, q31_u_beta)
    #print(angle, amplitude)
    #print(Tph1, Tph2, Tph3)


amplitudeSlider.on_changed(updatePlot)
angleSlider.on_changed(updatePlot)
# sO.on_changed(update)

updatePlot(None)
plt.show()
