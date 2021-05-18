# Trevor Poirier
# LP Technologies Coding Challenge
# Tuesday May 18th, 2021
# Programming language chosen: Python
# Total time spent: 5 hours

import matplotlib
import matplotlib.pyplot as plt
import mysql.connector
import numpy as np
import time
from array import array
from os import getcwd
from pathlib import Path as plib

matplotlib.use('TkAgg') # Integrate matplotlib with Python's Tkinter GUI library
current_dir = plib(getcwd())
bytes_file = plib.joinpath(current_dir, 'MySQL_Data')

try:
    # Try establishing a connection to the database
    lp = mysql.connector.connect(
        host="localhost",
        auth_plugin='mysql_native_password',
        user="Trevor",
        passwd="LPTCodeChallenge",
        database="lp")
    cursor = lp.cursor()
except mysql.connector.Error as DbConnectError:
    # If unsuccessful, show user the error message
    print("\nUnable to connect to database successfully.", "\n---> " + DbConnectError.msg)


# Queries the database in MySQL and writes the result to a binary file #
def read_db_data(outfile):
    blobs_count = 0  # int: number of rows
    blobs_size = 0   # int: length in bytes of each BLOB

    with open(outfile, 'wb') as f:
        try:
            query = "SELECT trace_data, trace_time FROM test ORDER BY trace_id ASC;"
            cursor.execute(query)
            result = cursor.fetchall()
            blobs_count = len(result)
            trace_times = []

            for blob in result:
                blobs_size = len(blob[0])
                f.write(blob[0])
                trace_times.append(blob[1])

        except mysql.connector.Error as DbQueryError:
            print("\nThe provided query was not executed successfully.", "\n---> " + DbQueryError.msg)

    return blobs_count, blobs_size, trace_times


# Reads binary file directly into an array of long integers for each row of the resulting relation #
def parse_db_data(infile, blobs_count, blobs_size):
    draws = []  # list that will contain arrays for each BLOB
    with open(infile, 'rb') as f:
        for i in range(blobs_count):
            arr = array('l', f.read(blobs_size))  # Read bytes into an array - byte order is little endian by default
            arr.byteswap()                        # Change order to big endian, which is byte order of original data
            draws.append(arr)

    return draws


# Both of these lists will be utilized when drawing the graph - they determine which tick marks have values
ticks_x = ['850 MHZ', ' ', ' ', ' ', ' ', '1000 MHZ', ' ', ' ', ' ', ' ', '1150 MZ']  # ' ' = tick marks with no value
ticks_y = ['-130 dBm', '-120 dBm', '-110 dBm', '-100 dBm', '-90 dBm', '-80 dBm',
           '-70 dBm','-60 dBm', '-50 dBm', '-40 dBm', '-30 dBm']

fig = plt.figure("LP Technologies")      # Assign the matplotlib figure to a variable
ax = fig.add_subplot()  # Initialize a subplot (axes) for more customization later

num_blobs, size_blobs, time_stamps = read_db_data(bytes_file)
data = parse_db_data(bytes_file, num_blobs, size_blobs)

doubles = []
# Iterate over the 50 individual arrays within the outer list
for blob in data:
    points = []
    # Iterate over the long integers within each of the 50 individual arrays
    for point in blob:
        points.append(point / 1000)
    doubles.append(points)

while True:    # Begin while loop to ensure the drawings are repeated until user exits the application
    plt.ion()  # Enable interactive mode where figures are automatically shown
    for i in range(len(doubles)):
        fig.patch.set_facecolor('black')  # Set window background color to black
        ax.patch.set_facecolor('black')   # Set graph background color to black
        x = np.arange(850, 1150.5, 0.5)   # Generate an array of values for x axis with same dimensions as y axis
        y = doubles[i]

        # Points of reference to place the additional labels on the graph appropriately
        left, width = 0.25, 0.5
        bottom, height = 0.25, 0.5
        right = left + width
        top = bottom + height

        # Creation of the 3 additional labels found in the example, including the trace_time
        time_display = ax.text(
                               0.5 * (left+right),
                               0.00675 * (bottom + top),
                               "Trace Time: {}".format(str(time_stamps[i])),  # Text to display
                               horizontalalignment='center',
                               verticalalignment='bottom',
                               fontsize=8, color='limegreen',
                               transform=ax.transAxes)
        top_left_label = ax.text(
                                 0.25 * left, 0.9225 * (bottom + top),
                                 "New BW Segment",  # Text to display
                                 horizontalalignment='left',
                                 verticalalignment='top',
                                 fontsize=8, color='limegreen',
                                 fontweight='bold',
                                 transform=ax.transAxes)
        top_right_label = ax.text(
                                 0.968 * (left + right),
                                 0.9225 * (bottom + top),
                                 "244",  # Text to display
                                 horizontalalignment='right',
                                 verticalalignment='top',
                                 fontsize=8, color='limegreen',
                                 fontweight='bold',
                                 transform=ax.transAxes)

        # Change each "spine" or outer edge of the graph to gray dashed line
        ax.spines['top'].set_linestyle('dashed')
        ax.spines['top'].set_edgecolor('gray')
        ax.spines['left'].set_linestyle('dashed')
        ax.spines['left'].set_edgecolor('gray')
        ax.spines['right'].set_linestyle('dashed')
        ax.spines['right'].set_edgecolor('gray')
        ax.spines['bottom'].set_linestyle('dashed')
        ax.spines['bottom'].set_edgecolor('gray')

        # Set lower and upper limits of each of the axes
        plt.xlim(850, 1150)
        plt.ylim(-130, -30)

        # For both, first argument is all of the tick marks to be shown
        # Second argument adds a number (and its units) to specific tick marks 
        plt.xticks(range(850, 1180, 30), ticks_x, color='white') 
        plt.yticks(range(-130, -20, 10), ticks_y, color='white')
        
        plt.grid(color='gray', linestyle='--')          # Show gray dashed gridlines according to xticks and yticks
        plt.plot(x, y, color='yellow', linewidth=0.75)  # Show the trace for the current index
        plt.pause(1.0)                                  # Display the current trace for 1 second
        plt.cla()                                       # Clear the current trace to display the next one

    time.sleep(2.0)  # Hold for a couple seconds after last trace before starting over
