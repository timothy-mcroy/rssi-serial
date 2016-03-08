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
    pattern = re.compile(r'Channel: (\d+) ; RSSI is: (.?\d+)')
    match = pattern.findall(reading)
    if len(match) == 0:
        return None
    result = tuple(map(int,match[0]))
    return result

protocol = [('', b'\n\n\n\n'),
        ('In: OPMOD:', b'RX0'),
        ('In: SAM_INTV:', b'100'),
        ('In: CHNUM:', b'C11')]
readers = [rssi.Serial_Reader(connection, reading_matcher, protocol, address) 
            for connection, address in zip(serial_connections, addresses)]    

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
est_skipped= sum(reader.times_data_failed_to_match for reader in readers)
print ('{} transmissions skipped'.format(est_skipped))
        
for reader in readers:
    reader.join()
