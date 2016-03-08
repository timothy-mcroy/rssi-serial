import serial
import time

def handleArg(ser, expected_prompt, arg, next_prompt, next_arg, parse_data):
    while True:
        debug =raw_input()
        cur_line = ser.readline()
        print("Expected {}, Received:".format(expected_prompt,cur_line))
        ser.write(arg)
        # If the data matches our input parser,
        #     the protocol is finished. 
        if parse_data(cur_line) is not None and next_prompt is None:
            return
        # If the next prompt has been reached, we should send it the data
        elif next_prompt is not None and next_prompt in cur_line: 
            return
        else:
            continue

def start_reading(serial_connection, protocol_args, parse_data):
    '''
    Performs setup protocol for reading RSSI data.
    Returns early without an exception if 
        the device was already transmitting.
    '''
    ser = serial_connection
    protocol_args.append((None,None))
    
    for i,(expected_prompt, arg) in enumerate(protocol_args):
        if expected_prompt is None:
            return

        next_prompt, next_arg = protocol_args[i+1]
        if parse_data("Channel: 11 ; RSSI is: -83") is None:
            print("Parser isn't working")

        handleArg(ser, expected_prompt, arg, next_prompt, next_arg, parse_data)

        

