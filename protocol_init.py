def handleArg(ser, expected_prompt, arg, next_prompt, parse_data):
    '''
    Repeatedly inputs the argument with respect to a prompt.
    When the next_prompt is detected, this function will quit.
    
    Parse_data is used to detect whether the serial connection
    is transmitting the expected output.  If that is the case and
    the next_prompt is None, we assume that this is the last argument
    of the protocol. 
    '''
    print("Handling prompt {}".format(expected_prompt))
    while True:
        cur_line = ser.readline()
        ser.write(arg)
        # If the data matches our input parser,
        #     the protocol is finished. 
        if parse_data(cur_line) is not None and next_prompt is None:
            return
        # If the next prompt has been reached, the current prompt was 
        #     handled
        elif next_prompt is not None and next_prompt in cur_line: 
            return


def start_reading(serial_connection, protocol_args, parse_data):
    '''
    Performs setup protocol for reading RSSI data.
    Returns early without an exception if 
        the device was already transmitting.
    '''
    ser = serial_connection
    # Having the list end at None, None lets us know that it is finished
    protocol_args.append((None,None))
    
    for i,(expected_prompt, arg) in enumerate(protocol_args):
        if expected_prompt is None:
            return

        next_prompt, next_arg = protocol_args[i+1]
        handleArg(ser, expected_prompt, arg, next_prompt, parse_data)

        

