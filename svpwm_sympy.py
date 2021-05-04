import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# symbolic computations with sympy
# https://docs.sympy.org/latest/index.html


"""

    SVPWM switch time computations from scratch with symbolic computations

"""

def dot(u, v):
    return u.transpose() * v

sp.init_printing()

m = 2 / sp.sqrt(3)
a, b = sp.symbols('a b')
u = sp.Matrix([[a], [b]])
sp.pprint(u)


# definition of the basis vectors

v1 = sp.Matrix([[2 / sp.sqrt(3)], [0]])
print('\nbasis vector v1:')
sp.pprint(v1)

v2 = sp.Matrix([[1 / sp.sqrt(3)], [1]])
print('\nbasis vector v2:')
sp.pprint(v2)

v3 = sp.Matrix([[-1 / sp.sqrt(3)], [1]])
print('\nbasis vector v3:')
sp.pprint(v3)

v4 = sp.Matrix([[-2 / sp.sqrt(3)], [0]])
print('\nbasis vector v4:')
sp.pprint(v4)

v5 = sp.Matrix([[-1 / sp.sqrt(3)], [-1]])
print('\nbasis vector v5:')
sp.pprint(v5)

v6 = sp.Matrix([[1 / sp.sqrt(3)], [-1]])
print('\nbasis vector v6:')
sp.pprint(v6)

# sector 1
print('\n\n----------------- sector1\n')

sp.pprint(dot(u, v1))
sp.pprint(dot(u, v2))
print('')
M = sp.Matrix()
M = M.col_insert(0,v1)
M = M.col_insert(1,v2)
xs1 = M.inv() * u
sp.pprint(xs1)

# v1 - (1 0 0)
# v2 - (1 1 0)
ts1_0 = 1 - xs1[0] - xs1[1]
ts1_1 = xs1[0] + xs1[1] + ts1_0 / 2
ts1_2 = xs1[1] + ts1_0 / 2
ts1_3 = ts1_0 / 2
print('symbolic switching times')
sp.pprint(ts1_1)
sp.pprint(ts1_2)
sp.pprint(ts1_3)

# sector 2
print('\n\n----------------- sector2\n')

sp.pprint(dot(u, v2))
sp.pprint(dot(u, v3))
print('')
M = sp.Matrix()
M = M.col_insert(0,v2)
M = M.col_insert(1,v3)
xs2 = M.inv() * u
sp.pprint(xs2)
# v2 = (1 1 0)
# v3 = (0 1 0)
ts2_0 = 1 - xs2[0] - xs2[1]
ts2_1 = xs2[0] + ts2_0 / 2
ts2_2 = xs2[0] + xs2[1] + ts2_0 / 2
ts2_3 = ts2_0 / 2 
print('symbolic switching times')
sp.pprint(ts2_1)
sp.pprint(ts2_2)
sp.pprint(ts2_3)

# sector 3
print('\n\n----------------- sector3\n')

sp.pprint(dot(u, v3))
sp.pprint(dot(u, v4))
print('')
M = sp.Matrix()
M = M.col_insert(0,v3)
M = M.col_insert(1,v4)
xs3 = M.inv() * u
sp.pprint(xs3)
# v3 = (0 1 0)
# v4 = (0 1 1)
ts3_0 = 1 - xs3[0] - xs3[1]
ts3_3 = xs3[1] + ts3_0 / 2
ts3_2 = xs3[0] + xs3[1] + ts3_0 / 2
ts3_1 = ts3_0 / 2 
print('symbolic switching times')
sp.pprint(ts3_1)
sp.pprint(ts3_2)
sp.pprint(ts3_3)

# sector 4
print('\n\n----------------- sector4\n')

sp.pprint(dot(u, v4))
sp.pprint(dot(u, v5))
print('')
M = sp.Matrix()
M = M.col_insert(0,v4)
M = M.col_insert(1,v5)
xs4 = M.inv() * u
sp.pprint(xs4)
# v4 = (0 1 1)
# v5 = (0 0 1)
ts4_0 = 1 - xs4[0] - xs4[1]
ts4_1 = ts4_0 / 2 
ts4_2 = xs4[0] + ts4_0 / 2
ts4_3 = xs4[0] + xs4[1] + ts4_0 / 2
print('symbolic switching times')
sp.pprint(ts4_1)
sp.pprint(ts4_2)
sp.pprint(ts4_3)

# sector 5
print('\n\n----------------- sector5\n')

sp.pprint(dot(u, v5))
sp.pprint(dot(u, v6))
print('')
M = sp.Matrix()
M = M.col_insert(0,v5)
M = M.col_insert(1,v6)
xs5 = M.inv() * u
sp.pprint(xs5)
# v5 = (0 0 1)
# v6 = (1 0 1)
ts5_0 = 1 - xs5[0] - xs5[1]
ts5_2 = ts5_0 / 2 
ts5_1 = xs5[1] + ts5_0 / 2
ts5_3 = xs5[0] + xs5[1] + ts5_0 / 2
print('symbolic switching times')
sp.pprint(ts5_1)
sp.pprint(ts5_2)
sp.pprint(ts5_3)

# sector 6
print('\n\n----------------- sector6\n')

sp.pprint(dot(u, v6))
sp.pprint(dot(u, v1))
print('')
M = sp.Matrix()
M = M.col_insert(0,v6)
M = M.col_insert(1,v1)
xs6 = M.inv() * u
sp.pprint(xs6)
# v6 = (1 0 1)
# v1 = (1 0 0)
ts6_0 = 1 - xs6[0] - xs6[1]
ts6_2 = ts6_0 / 2 
ts6_3 = xs6[0] + ts6_0 / 2
ts6_1 = xs6[0] + xs6[1] + ts6_0 / 2
print('symbolic switching times')
sp.pprint(ts6_1)
sp.pprint(ts6_2)
sp.pprint(ts6_3)


# ---------------------- X, Y and Z term

"""

def X(alpha, beta):
    return 2.0 * alpha / np.sqrt(3)

def Y(alpha, beta):
    return alpha / np.sqrt(3) + beta

def Z(alpha, beta):
    return alpha / np.sqrt(3) - beta



x = np.zeros(360)
y = np.zeros(360)
z = np.zeros(360)


for i in range(0, 360):
    alpha = np.cos(np.deg2rad(i))
    beta = np.sin(np.deg2rad(i))

    # a shift of 1 / sqrt(3) allows for determination of the sectors by the signs of x, y and z
    shift = 1.0 / np.sqrt(3)

    x[i] = X(alpha, beta) + shift
    y[i] = Y(alpha, beta) + shift
    z[i] = Z(alpha, beta) + shift

plt.plot(x, label='x', color='blue')
plt.plot(y, label='y', color='red')
plt.plot(z, label='z', color='black')
plt.xticks([0,60,120,180,240,300,360])
#plt.title('l')
plt.legend()
plt.grid()
plt.show()


"""

# ------------------- switchtime computation


Tph1 = np.zeros(360)
Tph2 = np.zeros(360)
Tph3 = np.zeros(360)

def getSector(angle):
    angle = angle % 360
    if angle >= 0 and angle < 60:
        return 1
    if angle >= 60 and angle < 120:
        return 2
    if angle >= 120 and angle < 180:
        return 3
    if angle >= 180 and angle < 240:
        return 4
    if angle >= 240 and angle < 300:
        return 5
    if angle >= 300 and angle < 360:
        return 6

for i in range(0, 360):
    alpha = np.cos(np.deg2rad(i))
    beta = np.sin(np.deg2rad(i))

    sector = getSector(i);

    if sector == 1 or sector == 4:
        # sector 1 and sector 4 have the same switching time formulas
        Tph1[i] = ts1_1.subs([(a,alpha), (b,beta)])
        Tph2[i] = ts1_2.subs([(a,alpha), (b,beta)])
        Tph3[i] = ts1_3.subs([(a,alpha), (b,beta)])
    if sector == 2 or sector == 5:
        Tph1[i] = ts2_1.subs([(a,alpha), (b,beta)])
        Tph2[i] = ts2_2.subs([(a,alpha), (b,beta)])
        Tph3[i] = ts2_3.subs([(a,alpha), (b,beta)])
    if sector == 3 or sector == 6:
        Tph1[i] = ts3_1.subs([(a,alpha), (b,beta)])
        Tph2[i] = ts3_2.subs([(a,alpha), (b,beta)])
        Tph3[i] = ts3_3.subs([(a,alpha), (b,beta)])



plt.plot(Tph1, label='t1', color='blue')
plt.plot(Tph2, label='t2', color='red')
plt.plot(Tph3, label='t3', color='black')
plt.xticks([0,60,120,180,240,300,360])
#plt.title('l')
plt.legend()
plt.grid()
plt.show()



        
