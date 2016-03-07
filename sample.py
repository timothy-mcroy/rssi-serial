import rssi
import serial
import re
import time
serial_connections = [
        serial.Serial('/dev/ttyACM0', 115200, timeout=2)
        ]
addresses = [None]

def reading_matcher(reading):
    '''
    Intended to match a pattern such as
    "Channel: 11 ; RSSI is: -117"

    return (int, int)
    '''
    pattern = re.compile(r'Channel: (\d+) ; RSSI is: -(\d+)')
    match = pattern.match(reading)
    if match is None:
        return match
    result = tuple(map(int,match.groups()))
    return result

readers = [rssi.Serial_Reader(connection, reading_matcher, address) 
            for connection, address in zip(serial_connections, addresses]    

while raw_input("Enter s to start recording data\n") != "s":
    continue

for reader in readers:
    reader.start()
time.sleep(60*5)
# while True:
#     end = raw_input(
# '''Enter q to stop\n
# Enter c for the current total\n''')
#     if end == "c":
#         print(rssi.Rssi.commits)
#     if end == "q":
#         print("Quitting after {} recordings".format(rssi.Rssi.commits))
#         break

print ("{} recordings made".format(rssi.Rssi.commits))
for reader in readers:
    reader.join()
