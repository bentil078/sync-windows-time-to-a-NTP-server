#!/usr/bin/env python3

import socket
import struct
import sys
import time
import datetime
import win32api

# List of servers in order of attempt of fetching
server_list = ['time.google.com', '0.pool.ntp.org', 'time.windows.com', 'time.nist.gov', 'europe.pool.ntp.org', 'time-a-g.nist.gov', 'pool.ntp.org']

'''
Returns the epoch time fetched from the NTP server passed as argument.
Returns none if the request is timed out (5 seconds).
'''
def gettime_ntp(addr='europe.pool.ntp.org'):
    TIME1970 = 2208988800      # Thanks to F.Lundh
    client = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    data_byte = '\x1b' + 47 * '\0'
    data = data_byte.encode('utf-8')
    try:
        # Timing out the connection after 5 seconds, if no response received
        client.settimeout(5.0)
        client.sendto( data, (addr, 123))
        data, address = client.recvfrom( 1024 )
        if data:
            epoch_time = struct.unpack( '!12I', data )[10]
            epoch_time -= TIME1970
            return epoch_time
    except socket.timeout:
        return None

# Get country code and add epoch offset value to it
# https://www.epochconverter.com/timezones
def get_country_code(country):
    codes = {'CA': -18000, 'US': -14400, 'TKY': +32400 }
    offset = 0
    for key, value in codes.items():
        if key == country:
            offset = value
        else:
            pass
    return offset


if __name__ == "__main__":
    # Iterates over every server in the list until it finds time from any one.
    for server in server_list:
        epoch_time = gettime_ntp(server)
        if epoch_time is not None:
            #Get country code eg. CA, US
            offset_value = get_country_code('TKY')

            # new epoch value with offset
            epoch_time += offset_value

            # SetSystemTime takes time as argument in UTC time. UTC time is obtained using utcfromtimestamp()
            utcTime = datetime.datetime.utcfromtimestamp(epoch_time)
            win32api.SetSystemTime(utcTime.year, utcTime.month, utcTime.weekday(), utcTime.day, utcTime.hour, utcTime.minute, utcTime.second, 0)
            # Local time is obtained using fromtimestamp()
            localTime = datetime.datetime.fromtimestamp(epoch_time)
            print("Time updated to: " + localTime.strftime("%Y-%m-%d %H:%M") + " from " + server)
            break
        else:
            print("Could not find time from " + server)

