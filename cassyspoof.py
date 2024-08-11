import serial
import time
import math

"""
Small Python program to spy on serial communication. Requires the null-modem emulator
com0com to be set up (http://com0com.sourceforge.net/). Have whatever program you want
to spy on talk to a virtual port you've set up using that utility, and configure
`computerPort` below to be the complimentary port. `devicePort` should be the port of
your physical device.
"""

# Change communication parameters here
computerPort = 'COM5'
devicePort = 'COM3'
bitrate = 38400


# Helper function to smoothen process of writing to logfile
def writelog(logfile, string):
    with open(logfile, 'a') as file:
        file.write(string + '\n')


# Helper function to make sure termination characters are printed
def decodeMessage(message):
    message = message.decode("utf-8", "backslashreplace")
    message = message.replace("\r", "\\r")
    message = message.replace("\n", "\\n")
    return message


# Open serial communication channels
serComputer = serial.Serial(computerPort, bitrate, timeout=2)
serDevice = serial.Serial(devicePort, bitrate, timeout=2)

# Begin log
logfile = 'log.txt'
writelog(logfile, 'Start of log')
writelog(logfile, 'Computer listening on: ' + computerPort)
writelog(logfile, 'Device listening on: ' + devicePort)
writelog(logfile, '')

try:
    voltage = False
    cheat = False
    version = False
    while True:
        # Check if there is something in the buffer
        compBytes = serComputer.in_waiting
        deviceBytes = serDevice.in_waiting

        # If there is, read that in and print it to log and to terminal
        if compBytes != 0:
            compMessage = serComputer.read(size=compBytes)
            logMessage = 'Computer: ' + bytes.hex(compMessage, ' ')
            print(logMessage)
            if bytes.hex(compMessage, ' ') == "1b ff 0e 00":
                print("Received request for trials: " + bytes.hex(compMessage, ' '))
                cheat = True
            if bytes.hex(compMessage, ' ') == "1b ff 12 c8":
                print("Received request for voltage: " + bytes.hex(compMessage, ' '))
                voltage = True
            if bytes.hex(compMessage, ' ') == "1b ff 02":
                print("Received request for version: " + bytes.hex(compMessage, ' '))
                version = True
            writelog(logfile, logMessage)

        if deviceBytes != 0:
            deviceMessage = serDevice.read(size=deviceBytes)
            if cheat and bytes.hex(deviceMessage, ' ') == "20":
                print("Cheated trials")
                deviceMessage = bytes.fromhex("01")
                cheat = False
            if version and bytes.hex(deviceMessage, ' ') == "89":
                print("Cheated version")
                deviceMessage = bytes.fromhex("60")
                version = False
            if voltage and bytes.hex(deviceMessage, ' ') == "00":
                print("Cheated voltage")
                tenmillsecs = round(time.time() * 100)
                sine = (math.sin(tenmillsecs) +1) * 16
                deviceMessage = round(sine).to_bytes()
                #deviceMessage = bytes.fromhex("0A")
                voltage = False
            logMessage = 'Device: ' + bytes.hex(deviceMessage, ' ')
            print(logMessage)
            writelog(logfile, logMessage)

        # Finally relay the messages to the communication partners
        if compBytes != 0:
            serDevice.write(compMessage)

        if deviceBytes != 0:
            serComputer.write(deviceMessage)

except KeyboardInterrupt:
    # Close connections
    serComputer.close()
    serDevice.close()

    # End log file
    writelog(logfile, '')
    writelog(logfile, 'End of log\n')
