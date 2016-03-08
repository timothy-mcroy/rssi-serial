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

protocol = [ '', 'In: OPMOD:', 'In: SAM_INTV:', 'In: CHNUM:']
args = []
for arg_num, prompt in enumerate(protocol):
    arg = raw_input(" {} :: {} : ".format(arg_num, prompt))
    args.append(bytes(arg))

protocol_args = zip(protocol, args)
readers = [rssi.Serial_Reader(connection, reading_matcher, protocol_args, address) 
            for connection, address in zip(serial_connections, addresses)]    

while raw_input("Enter s to start recording data\n") != "s":
    continue

for reader in readers:
    reader.start()
time.sleep(5)
# while True:
#     end = raw_input(
# '''Enter q to stop\n
# Enter c for the current total\n''')
#     if end == "c":
#         print(rssi.Rssi.commits)
#     if end == "q":
#         print("Quitting after {} recordings".format(rssi.Rssi.commits))
#         break

print ("{} recordings made".format(rssi.Signal_Repository.commits))
est_skipped= sum(reader.times_data_failed_to_match for reader in readers)
print ('{} transmissions skipped'.format(est_skipped))
        
for reader in readers:
    reader.join()
