__author__ = 'luisconejo'
# Polls traffic to and from a particular address and saves the results into a database

import urllib2
import json
import re
import datetime
import sqlite3
import time

# Individual procedures

# Creates the database for results. The database will have a single table with the following fields
# Month, Day, Hour, Minute (rounded to the nearest 5-minute block), origin, destination
def initDB():
    #Start database
    global conn
    conn = sqlite3.connect('trafficData.db')
    global c
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE trafficResults
             (month, day, hour, minute, origin, destination, distance, duration)''')
    except:
        pass

# Sends a request to MapQuest Directions API, taking a starting address, destination address and returning the JSON
# output
def getDirections(startingAddress, destinationAddress, apiKey):
    # Formely used Google API, but traffic data is not free on it :-(
    # apiCommand = "https://maps.googleapis.com/maps/api/directions/json?origin=" + startingAddress + "&destination=" \
    #             + destinationAddress + "&key=" + apiKey

    # MapQuest API much nicer in terms of being free :-)
    apiCommand = "http://www.mapquestapi.com/directions/v2/route?key=" + apiKey + "&from=" + startingAddress + "&to=" \
                 + destinationAddress

    response = urllib2.urlopen(apiCommand)
    return response

# Saves a result into the database or updates and existing result
def saveIntoDB(dBmonth, dBday, dBhour, dBminute, dBorigin, dBdestination, dBdistance, dBduration):
    # First, check if there is an existing record with the same date and time
    c.execute('SELECT * FROM trafficResults WHERE month=? AND day=? AND hour=? AND minute=? AND origin=?'
              'AND destination = ? AND distance=?',
              (dBmonth, dBday, dBhour, dBminute, dBorigin, dBdestination, dBdistance))

    result = c.fetchone()

    #If word is unknown, then do a web search
    if str(result) == "None":
        # Create a new record
        result = c.execute("""INSERT INTO trafficResults(month, day, hour, minute, origin, destination,
        distance, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (dBmonth, dBday, dBhour, dBminute, dBorigin, dBdestination,
                                             dBdistance, dBduration))
        conn.commit()
        print "INFO: Record added"
    else:
        # Update existing record
        c.execute('UPDATE trafficResults SET duration=? WHERE month=? AND day=? AND hour=? AND minute=? AND origin=?'
                  'AND destination=? AND distance=?',
                  (dBduration, dBmonth, dBday, dBhour, dBminute, dBorigin, dBdestination, dBdistance))
        conn.commit()
        print "INFO: Record updated"

# Calls getDirections for a particular route, process the output to extract the total driving time and call saveIntoDB
# to save the results to the database, adjusts the time stamp using roundTimeStamp.
def collectData(startingAddress, destinationAddress, serverKey):
    response = getDirections(startingAddress, destinationAddress, serverKey)

    # Extract trip duration from the JSON output
    data = json.load(response)
    node = data['route']['realTime']

    # Extract time as a numeric value
    duration = re.findall('[0-9]+', str(node))

    node = data['route']['distance']

    # Extract distance as a numeric value
    distance = re.findall('[0-9.]+', str(node))

    # Capture current time
    currentTime = datetime.datetime.now()

    # Round down minute to the nearest multiple of five
    roundedCurrentMinute = 5 * (currentTime.minute / 5)

    #Save to database
    print str(currentTime.month) + "     " + str(currentTime.day) + "     " + str(currentTime.hour) + "     " + \
          str(roundedCurrentMinute) + "       " + str(startingAddress)  + "  " + str(destinationAddress)  + "     " + \
          str(distance[0]) + "     " + str(duration[0])

    saveIntoDB(currentTime.month, currentTime.day, currentTime.hour, roundedCurrentMinute, startingAddress,
               destinationAddress, distance[0], duration[0])

# Runs indefinitely until a key is pressed, collecting data every five (5) minutes
# Uses a time and collectData
def infiniteRunner(startingAddress, destinationAddress, serverKey):
    counter = 0
    while counter < 210816:
        collectData(homeAddress,workAddress, serverKey)
        collectData(workAddress,homeAddress, serverKey)

        # Waits 300 seconds before each query
        time.sleep(300)
        counter = counter + 1

# Main Flow
homeAddress = "72+Rock+Harbor+Lane,+Foster+City,+CA+94404"
workAddress = "3600+Mission+College+Blvd,++Santa+Clara,+CA+95054"

# Google Directions API server key
#serverKey = "AIzaSyC6oQWg74G15hWw5bab-EVX2BZNKz-cN3w"

# MapQuest Directions API server key
serverKey = "Fmjtd%7Cluurnu0yn5%2C8g%3Do5-9w8l1f"

# Start DB
initDB()

# Print header for terminal display
print "MONTH  DAY    HOUR   MINUTE  ORIGIN                                      DESTINATION                 " \
      "                          DISTANCE DURATION"

infiniteRunner(homeAddress,workAddress, serverKey)