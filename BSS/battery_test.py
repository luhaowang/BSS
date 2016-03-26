from batteryComplex import Battery
import numpy as np
import matplotlib.pyplot as plt
if __name__ == '__main__':
    a = Battery('1', 10.0,100.0,10.0, 0.0)
    rates = np.linspace(-10, 10, 1e4)
    outputpowers = np.zeros(rates.size)
    for i in range(rates.size):
        a.set_rate(rates[i]*1000)
        outputpowers[i] = a.get_outputPower()
    plt.plot(rates,outputpowers/1000)
    plt.show()