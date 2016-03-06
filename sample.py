import rssi
import serial
import re
import time
device1 = serial.Serial('/dev/ttyACM0', 115200, timeout=2)

def reading_matcher(reading):
    '''Intended to match a pattern such as
    "Channel: 11 ; RSSI is: -117"

    return (int, int)
    '''
    pattern = re.compile(r'Channel: (\d+) ; RSSI is: -(\d+)')
    match = pattern.match(reading)
    if match is None:
        return match
    result = tuple(map(int,match.groups()))
    return result

reader1 = rssi.Serial_Reader(device1, reading_matcher)

while raw_input("Enter s to start recording data\n") != "s":
    continue

reader1.start()

time.sleep(5)
while True:
    end = raw_input(
'''Enter q to stop\n
Enter c for the current total\n''')
    if end == "c":
        print(rssi.Rssi.commits)
    if end == "q":
        print("Quitting after {} recordings".format(rssi.Rssi.commits))
        break

reader1.join()
