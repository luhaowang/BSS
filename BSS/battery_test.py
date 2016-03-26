from batteryComplex import Battery
import numpy as np
import matplotlib.pyplot as plt
if __name__ == '__main__':
    a = Battery(id='1', soc = 30.0,soc_full = 89.0, soc_nom = 100.0,vmax=10, ts=0)
#     rates = np.linspace(-10, 10, 1e4)
#     outputpowers = np.zeros(rates.size)
#     for i in range(rates.size):
#         a.set_rate(rates[i]*1000)
#         outputpowers[i] = a.get_outputPower()
#     plt.plot(rates,outputpowers/1000)
#     plt.show()
    print a.get_DSOH()
    a.set_targetsoc(80.0)
    a.set_td(0.5)
    print a.cal_SOHDeg()
    print a.get_DSOH()
    print a.soc_full
    