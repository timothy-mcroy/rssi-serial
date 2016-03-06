import serial
import time

def start_reading(serial_connection):
    '''Starts reading RSSI values'''
    ser = serial_connection
    print("Starting first poll")
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

    print("Starting second poll!")
    count = 0
    while True:
        x = ser.readline()
        print(x)
        count+=1
        ser.write(b'M00')
        if "OPMOD" in x: 
            ser.write(b'100')
            break

    print("Starting third poll!")
    while True:
        x = ser.readline()
        print(x)
        ser.write(b'100')
        if 'SMPSET' in x:
            ser.write(b'C11')
            break

    count =0
    x = ser.readline()
    while "Channel" not in x: 
        print(x)
        x = ser.readline() 
        ser.write(b'C11')
