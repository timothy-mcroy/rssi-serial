import rssi
import serial
device1 = serial.Serial('/dev/port0', 19200, timeout=2)
device2 = serial.Serial('/dev/port1', 19200, timeout=2)

reader1 = rssi.Serial_Reader(device1)
reader2 = rssi.Serial_Reader(device2)

reader1.start()
reader2.start()

while input("Enter q to stop ") != "q":
    continue

reader1.join()
reader2.join()
