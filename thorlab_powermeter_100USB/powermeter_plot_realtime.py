import serial
from datetime import datetime
import re
import csv
import threading
from numpy import array
import numpy as np
import pyvisa
from ThorlabsPM100 import ThorlabsPM100
import signal
import sys
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
class thorlab_power_meter(ThorlabsPM100):
    def __init__(self, usbID, avg_count=1, wavelength=637, bandwidth=1) -> None:
        self.m_usbID = usbID
        self.m_rm = pyvisa.ResourceManager()
        self.m_rm.list_resources()

        self.m_inst = self.m_rm.open_resource(self.m_usbID, timeout=1)
        
        # Initialize the ThorlabsPM100 with the instrument
        super().__init__(inst=self.m_inst)
        
       
        super(thorlab_power_meter, self).sense.correction.wavelength = wavelength
        super(thorlab_power_meter, self).sense.average.count = avg_count
        super(thorlab_power_meter, self).input.pdiode.filter.lpass.state = bandwidth

    # Getter and Setter for m_usbID
    @property
    def usbID(self):
        return self.m_usbID

    @usbID.setter
    def usbID(self, value):
        self.m_usbID = value
        self.m_inst = self.m_rm.open_resource(self.m_usbID, timeout=1)

    # Getter and Setter for m_avg_count
    @property
    def avg_count(self):
        return super(thorlab_power_meter, self).sense.average.count

    @avg_count.setter
    def avg_count(self, value):
        super(thorlab_power_meter, self).sense.average.count = value

    # Getter and Setter for m_wavelength
    @property
    def wavelength(self):
        return super(thorlab_power_meter, self).sense.correction.wavelength

    @wavelength.setter
    def wavelength(self, value):
        super(thorlab_power_meter, self).sense.correction.wavelength = value

    # Getter and Setter for m_bandwidth
    @property
    def bandwidth(self):
        return super(thorlab_power_meter, self).input.pdiode.filter.lpass.state

    @bandwidth.setter
    def bandwidth(self, value):
        super(thorlab_power_meter, self).input.pdiode.filter.lpass.state = value

    def perform_measurement(self, num_samples) -> None:
        self.m_arr_vals = array([super(thorlab_power_meter, self).read for _ in range(num_samples)])
    
    @property
    def array_values(self) -> array:
        return self.m_arr_vals
class data(object):
    def __init__(self, value: float, freq: int, meas_time) -> None:
        self.m_val = value
        self.m_freq = freq
        self.m_meas_time = meas_time
    def __str__(self):
        return f'{self.m_val}, {self.m_freq}, {self.m_meas_time}'
    def __iter__(self):
        return iter([self.m_meas_time, self.m_freq, self.m_val])
    

def make_csv(file_name, cdr_list):
    with open(file_name, 'w') as csv_file:
        wr = csv.writer(csv_file, delimiter=",")
        for cdr in cdr_list:
            wr.writerow(cdr)

arr_values = []
xdata1, ydata1 = [], []  # For Power vs. Frequency
xdata2, ydata2 = [], []  # For Power vs. Real-time
# Initialize plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9))
plt.subplots_adjust(hspace=0.5)  # Adjust the space between plots
def plot_power_vs_freq(xdata1, ydata1, ax1):
    ln1, = ax1.plot(xdata1, ydata1, 'b-', label='Power (nW)')
    ax1.set_title('Power vs. Frequency')
    ax1.set_xlabel('Frequency (kHz)')
    ax1.set_ylabel('Power (nW)')
    ax1.legend()
    return ln1

ln1 = plot_power_vs_freq(xdata1, ydata1, ax1)

def plot_power_real_time(xdata2, ydata2, ax2):
    ln2, = ax2.plot(xdata2, ydata2, 'r-', label='Power (nW)')
    ax2.set_title('Power vs. Real-time')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Power (nW)')
    ax2.legend()
    return ln2

ln2 = plot_power_real_time(xdata2, ydata2, ax2)

def init():
    return ln1, ln2

def update(frame):
    global xdata1, ydata1, xdata2, ydata2, arr_values

    text = str(ser.readline().decode('utf-8'))
    pow_meter.perform_measurement(num_samples)
    my_val = pow_meter.array_values.mean()

    
    pattern = r"Frequency: (\d+)khz"
    frequency = int(re.findall(pattern, text)[0])
    now = datetime.now()

    xdata1.append(frequency)
    ydata1.append(my_val * 1e9)  # Assuming the power is read in watts and needs to be converted to nW
    xdata2.append(now)
    ydata2.append(my_val * 1e9)

    ax1.clear()
    ax2.clear()
    
    ln1 = plot_power_vs_freq(xdata1, ydata1, ax1)
    ln2 = plot_power_real_time(xdata2, ydata2, ax2)

    arr_values.append(data(my_val, frequency, now))
    print(data(my_val, frequency, now))
    return ln1, ln2

def record_data() -> None:
    global pow_meter, ser, arr_values
    ani.event_source.stop()
    # Save data to CSV after the recording is done
    make_csv("data.csv", arr_values)
    print("Done")
    
    # Stop data collection
    timer.cancel()
def signal_handler(sig, frame):
    print('Exiting gracefully')
    record_data()
    plt.close(fig)
    sys.exit(0)
def on_close(event):
    print("close the plot")
    signal_handler(None, None)
if __name__ == "__main__":
    pow_meter = thorlab_power_meter("USB0::0x1313::0x8072::P2002697::INSTR", avg_count=10, wavelength= 635)
    ser = serial.Serial()
    ser.port = 'COM5'
    ser.baudrate = 115200
    ser.setDTR(False)
    ser.setRTS(False)
    ser.open()
    time_meas = 200  # time measurement in seconds
    num_samples = 10
    signal.signal(signal.SIGINT, signal_handler)
    fig.canvas.mpl_connect('close_event', on_close)
    ani = FuncAnimation(fig, update, init_func=init, frames=range(time_meas), blit=True, interval=100)
    timer = threading.Timer(time_meas, record_data)
    timer.isDaemon = True
    timer.start()
    
    plt.show()