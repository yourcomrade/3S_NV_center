# 3S_NV_center
This is folder contains all code for the 3S NV center project. This project is to demonstrate the simplifed version of the ODMR. 
The folder ADF4351 contains all C++ file to program ADF4351, which is the low-cost signal generator for the setup. It contains 2 versions: example version and the version using esp32 to control ADF4351.
The camera folder contains all data and files, and dll libraries for the CMOS camera from Thorlab. This camera is used to measure light intensity and stored in the data in the csv file.
The folder thorlab powermeter is for 2 files: a thorlab example for Python API usage and a custom Python which collects data from Thorlab powermeter and collect frequecy via serial port from esp32. It plots 2 plots: frequency vs power and power vs real-time. After that, it writes datetime, frequency, and power output into a csv file.
It is important to know that these code files are tested and worked in Window 10 and Window 11. 