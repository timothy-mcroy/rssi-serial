import serial
import time

def start_reading(serial_connection):
    '''Performs setup protocol for reading RSSI data.
    Returns early without an exception if 
        the device was already transmitting.
    '''
    ser = serial_connection
    print("Checking whether device is active.")
    while True:
        x = ser.readline()
        repr(x)
        print(x)
        if "Channel" in x:
            print "Sensortag was already transmitting!"
            print "Beginning recording under previous settings"
            return
        if x != '':
            ser.write(b'M00')
            break

    print("Setting OP MODE... ")
    while True:
        x = ser.readline()
        print(x)
        ser.write(b'M00')
        if "OPMOD" in x: 
            ser.write(b'100')
            break

    print("Setting transmission rate... ")
    while True:
        x = ser.readline()
        print(x)
        ser.write(b'100')
        if 'SMPSET' in x:
            ser.write(b'C11')
            break

    print("Setting Channel")
    count =0
    x = ser.readline()
    while "Channel" not in x: 
        print(x)
        x = ser.readline() 
        ser.write(b'C11')
