import serial
from datetime import datetime
import re
import csv

from time import sleep
from numpy import array
import pyvisa
from ThorlabsPM100 import ThorlabsPM100
import pyvisa
from ThorlabsPM100 import ThorlabsPM100

class thorlab_power_meter(ThorlabsPM100):
    def __init__(self, usbID, avg_count=1, wavelength=637, bandwidth=0) -> None:
        self.m_usbID = usbID
        self.m_rm = pyvisa.ResourceManager()
        self.m_rm.list_resources()

        self.m_inst = self.m_rm.open_resource(self.m_usbID, timeout=1)
        
        # Initialize the ThorlabsPM100 with the instrument
        super().__init__(inst=self.m_inst)
        
        self.m_avg_count = avg_count
        self.m_wavelength = wavelength
        self.m_bandwidth = bandwidth

    # Getter and Setter for m_usbID
    @property
    def usbID(self):
        return self.m_usbID

    @usbID.setter
    def usbID(self, value):
        self.m_usbID = value

    # Getter and Setter for m_avg_count
    @property
    def avg_count(self):
        return self.m_avg_count

    @avg_count.setter
    def avg_count(self, value):
        self.m_avg_count = value

    # Getter and Setter for m_wavelength
    @property
    def wavelength(self):
        return self.m_wavelength

    @wavelength.setter
    def wavelength(self, value):
        self.m_wavelength = value

    # Getter and Setter for m_bandwidth
    @property
    def bandwidth(self):
        return self.m_bandwidth

    @bandwidth.setter
    def bandwidth(self, value):
        self.m_bandwidth = value

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
def record_data() -> None:
    pow_meter = thorlab_power_meter("USB0::0x1313::0x8072::P2002697::INSTR", avg_count= 1)

    
    ser = serial.Serial()
    ser.port = 'COM5'
    ser.baudrate = 115200
    ser.setDTR(False)
    ser.setRTS(False)
    ser.open()
    arr_values = []
    for _ in range(3000):
        text = str(ser.readline().decode('utf-8'))
        print(text, end='')
        print(type(text))
        pow_meter.perform_measurement(1)
        my_val = pow_meter.array_values.mean()

        # Regular expression pattern to match the frequency value
        pattern = r"Frequency: (\d+)khz"

        # Find all matches in the string and convert the found frequency value to integere
        print(re.findall(pattern, text))
        frequency = int(re.findall(pattern, text)[0])
        now = datetime.now()
        my_data = data(my_val, frequency, now)
        print(my_data)
        arr_values.append(my_data)
        sleep(0.1)
    
    arr_values = array(arr_values)
    make_csv("data.csv", arr_values)
record_data()

       
  