__author__ = 'luisconejo'
# Polls traffic to and from a particular address and saves the results into a database

import urllib2
import json
import re
import datetime

# Individual procedures

# Creates the database for results. The database will have a single table with the following fields
# Month, Day, Hour, Minute (rounded to the nearest 5-minute block), origin, destination
def createDB():
    pass

# Sends a request to Google Directions API, taking a starting address, destination address and returning the JSON
# output
def getDirections(startingAddress, destinationAddress, apiKey):
    apiCommand = "https://maps.googleapis.com/maps/api/directions/json?origin=" + startingAddress + "&destination=" \
                 + destinationAddress + "&key=" + apiKey

    response = urllib2.urlopen(apiCommand)
    return response

# Saves a result into the database
def saveIntoDB(startingAddress, destinationAddress, totalTime):
    pass

# Calls getDirections for a particular route, process the output to extract the total driving time and call saveIntoDB
# to save the results to the database, adjusts the time stamp using roundTimeStamp.
def collectData(startingAddress, destinationAddress, serverKey):
    response = getDirections(startingAddress, destinationAddress, serverKey)

    # Extract trip duration from the JSON output
    data = json.load(response)
    node = data['routes'][0]['legs'][0]['duration']['text']

    # Extract time as a numeric value
    duration = re.findall('[0-9]+', str(node))

    node = data['routes'][0]['legs'][0]['distance']['text']

    # Extract distance as a numeric value
    distance = re.findall('[0-9.]+', str(node))

    # Capture current time
    currentTime = datetime.datetime.now()

    # Round down minute to the nearest multiple of five
    roundedCurrentMinute = 5 * (currentTime.minute / 5)

    #Save to database
    print "Database entry:"
    print currentTime.year
    print currentTime.month
    print currentTime.day
    print currentTime.hour
    print roundedCurrentMinute
    print startingAddress
    print destinationAddress
    print distance[0]
    print duration[0]

# Runs indefinitely until a key is pressed, collecting data every five (5) minutes
# Uses a time and collectData
def infiniteRunner(startingAddress, destinationAddress):
    pass

# Main Flow
homeAddress = "72+Rock+Harbor+Lane,+Foster+City,+CA+94404"
workAddress = "3600+Mission+College+Blvd,++Santa+Clara,+CA+95054"

# Directions API server key
serverKey = "AIzaSyC6oQWg74G15hWw5bab-EVX2BZNKz-cN3w"

collectData(homeAddress,workAddress, serverKey)