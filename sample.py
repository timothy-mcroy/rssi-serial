import rssi
import serial
import re
import time
import os

devices = ['/dev/'+port for port in os.listdir('/dev/') 
        if 'ACM' in port
        and int(port[-1]) % 2 == 0 ]

serial_connections = [
        serial.Serial(port, 115200, timeout=2)
        for port in devices]

addresses = [None]*len(serial_connections)

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

def close_connections():
    for conn in serial_connections:
        conn.close()
import sys

protocol = [ '', 'In: OPMOD:', 'In: SAM_INTV:', 'In: CHNUM:']
args = []
for arg_num, prompt in enumerate(protocol):
    arg = raw_input(" {} :: {} : ".format(arg_num, prompt))
    args.append(bytes(arg))

protocol_args = zip(protocol, args)
args_map = dict(protocol_args)
if args_map["In: OPMOD:"] not in ["RX0", "RX1", "TX0", "TX1"]:
    print("OPMOD -{}- invalid!".format(args_map["In: OPMOD:"]))
    close_connections()
    sys.exit(1)

if not args_map["In: SAM_INTV:"].isdigit():
    print("-{}- is not a number".format(args_map["In: SAM_INTV:"]))
    close_connections()
    sys.exit(1)

chan_num = args_map["In: CHNUM:"]
if len(chan_num) == 0:
    print("Channel number is required")
    close_connections()
    sys.exit(1)

chan_num = chan_num[1:]
if not chan_num.isdigit():
    print("{} is not a valid channel number".format(chan_num))
    close_connections()
    sys.exit(1)

if int(chan_num) not in range(11, 26+1):
    print("{} is not within the range 11 and 26".format(chan_num))
    close_connections()
    sys.exit(1)


readers = [rssi.Serial_Reader(connection, reading_matcher, protocol_args, address) 
            for connection, address in zip(serial_connections, addresses)]    

print ("Collected all parameters. Starting polling.")

for reader in readers:
    reader.start()

time.sleep(15)
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
