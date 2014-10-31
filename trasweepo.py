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
    # Start database
    global conn
    conn = sqlite3.connect('trafficData.db')
    global c
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE trafficResults
             (month, dayOfTheWeek, day, hour, minute, origin, destination, distance, duration,
             prediction  INTEGER DEFAULT 0)''')
    except:
        pass


# Sends a request to MapQuest Directions API, taking a starting address, destination address and returning the JSON
# output
def getDirections(startingAddress, destinationAddress, apiKey):
    # Formely used Google API, but traffic data is not free on it :-(
    # apiCommand = "https://maps.googleapis.com/maps/api/directions/json?origin=" + startingAddress + "&destination=" \
    # + destinationAddress + "&key=" + apiKey

    # MapQuest API much nicer in terms of being free :-)
    apiCommand = "http://www.mapquestapi.com/directions/v2/route?key=" + apiKey + "&from=" + startingAddress + "&to=" \
                 + destinationAddress

    response = urllib2.urlopen(apiCommand)
    return response


# Saves a result into the database or updates and existing result
def saveIntoDB(dBmonth, dbDoW, dBday, dBhour, dBminute, dBorigin, dBdestination, dBdistance, dBduration):
    # First, check if there is an existing record with the same date and time
    c.execute('SELECT * FROM trafficResults WHERE month=? AND day=? AND hour=? AND minute=? AND origin=?'
              'AND destination = ? AND distance=?',
              (dBmonth, dBday, dBhour, dBminute, dBorigin, dBdestination, dBdistance))

    result = c.fetchone()

    if str(result) == "None":
        # Create a new record
        result = c.execute("""INSERT INTO trafficResults(month, dayOfTheWeek, day, hour, minute, origin, destination,
        distance, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (dBmonth, dbDoW, dBday, dBhour, dBminute, dBorigin, dBdestination,
                                                dBdistance, dBduration))
        conn.commit()

        dbHourMinute = "T" + str(dBhour) + "_" + str(dBminute)
        dbMonthDay = "D" + str(dBmonth) + "_" + str(dBday)

        # Now add record to predictor DB
        addToPredictor(dBduration, dBorigin, dBdestination, dbDoW, dbHourMinute, dbMonthDay)

        print "INFO: Record added"


    else:
        # Update existing record
        c.execute(
            'UPDATE trafficResults SET duration=?, dayOfTheWeek=? WHERE month=? AND day=? AND hour=? AND minute=? AND origin=?'
            'AND destination=? AND distance=?',
            (dBduration, dbDoW, dBmonth, dBday, dBhour, dBminute, dBorigin, dBdestination, dBdistance))
        conn.commit()

        dbHourMinute = "T" + str(dBhour) + "_" + str(dBminute)
        dbMonthDay = "D" + str(dBmonth) + "_" + str(dBday)

        # Remove all weights from predictor
        removeFromPredictor(dBduration, dBorigin, dBdestination, dbDoW, dbHourMinute, dbMonthDay)

        # Now add record to predictor DB
        addToPredictor(dBduration, dBorigin, dBdestination, dbDoW, dbHourMinute, dbMonthDay)
        print "INFO: Record updated"

    # Perform prediction
    dbPrediction = makePrediction(dBorigin, dBdestination, dbDoW, dbHourMinute, dbMonthDay)

    # Update prediction field for the entry
    c.execute('UPDATE trafficResults SET prediction=? WHERE month=? AND day=? AND hour=? AND minute=? '
              'AND origin=? AND destination=? AND distance=?',
              (dbPrediction, dBmonth, dBday, dBhour, dBminute, dBorigin, dBdestination, dBdistance))
    conn.commit()

    # Print results on screen
    print str(dBmonth) + "     " + str(dBday) + "     " + str(dBhour) + "     " + \
          str(dBminute) + "       " + dBorigin + "  " + dBdestination + "     " + \
          str(dBdistance) + "     " + str(dBduration) + "     " + dbDoW + "             " + str(dbPrediction)

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

    # Get day of the week
    dayNumber = datetime.datetime.now().weekday()
    if dayNumber == 0:
        dayOfWeek = "Monday"
    elif dayNumber == 1:
        dayOfWeek = "Tuesday"
    elif dayNumber == 2:
        dayOfWeek = "Wednesday"
    elif dayNumber == 3:
        dayOfWeek = "Thursday"
    elif dayNumber == 4:
        dayOfWeek = "Friday"
    elif dayNumber == 5:
        dayOfWeek = "Saturday"
    elif dayNumber == 6:
        dayOfWeek = "Sunday"

    durationMin = int(float(duration[0]) / 60)

    # Save to database
#    print str(currentTime.month) + "     " + str(currentTime.day) + "     " + str(currentTime.hour) + "     " + \
#          str(roundedCurrentMinute) + "       " + str(startingAddress) + "  " + str(destinationAddress) + "     " + \
#          str(distance[0]) + "     " + str(durationMin) + "     " + dayOfWeek

    saveIntoDB(currentTime.month, dayOfWeek, currentTime.day, currentTime.hour, roundedCurrentMinute, startingAddress,
               destinationAddress, distance[0], durationMin)


# Runs indefinitely until a key is pressed, collecting data every five (5) minutes
# Uses a time and collectData
def infiniteRunner(startingAddress, destinationAddress, serverKey):
    counter = 0
    while counter < 210816:
        collectData(homeAddress, workAddress, serverKey)
        collectData(workAddress, homeAddress, serverKey)

        # Waits 300 seconds before each query
        time.sleep(300)
        counter = counter + 1


# Prediction Flow
# This section includes the necessary procedures for support transit time prediction based on existing data

# initPredictor
# Initializes the Predictor database which contains the following columns:
# - Duration: A possible duration for the trip.
# However, additional entries can be added.
# - Day of the Week (7 column): One column per day of the week (Sunday, Monday, etc.).
# - Hour_Minute (288 columns): One column per hour and minute, at 5-minute intervals. For example: 22_5 to represent
#   10:05 p.m.
# - Month_Day (366): One column per Month_Day combination, including February 29th. Example: Mar_12.
# - Origin: Origin address.
# - Destination: Destination address.
def initPredictor():
    #Start database
    global connPred
    connPred = sqlite3.connect('predictor.db')
    global predictor
    predictor = connPred.cursor()

    try:

        predictor.execute('''CREATE TABLE predictor
             (Duration, Origin, Destination, Sunday INTEGER DEFAULT 0, Monday INTEGER DEFAULT 0,
             Tuesday INTEGER DEFAULT 0, Wednesday INTEGER DEFAULT 0, Thursday INTEGER DEFAULT 0,
             Friday INTEGER DEFAULT 0, Saturday INTEGER DEFAULT 0)''')

        # Now, run a loop to add columns for each hour of the day and each minute at five minutes intervals
        hours = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23)
        minutes = (0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55)

        for hour in hours:
            for minute in minutes:
                hourMinute = "T" + str(hour) + "_" + str(minute)
                predictor.execute("ALTER TABLE predictor ADD COLUMN '%s' INTEGER DEFAULT 0" % hourMinute)

        # Finally, add the columns for each month_day combination
        months = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)

        for month in months:
            if ((month == 4) or (month == 6) or (month == 9) or (month == 11)):
                for day in range(1, 31):
                    monthDay = "D" + str(month) + "_" + str(day)
                    print "MonthDay:" + monthDay
                    predictor.execute("ALTER TABLE predictor ADD COLUMN '%s' INTEGER DEFAULT 0" % monthDay)
            elif (month == 2):
                for day in range(1, 30):
                    monthDay = "D" + str(month) + "_" + str(day)
                    print "MonthDay:" + monthDay
                    predictor.execute("ALTER TABLE predictor ADD COLUMN '%s' INTEGER DEFAULT 0" % monthDay)
            else:
                for day in range(1, 32):
                    monthDay = "D" + str(month) + "_" + str(day)
                    print "MonthDay:" + monthDay
                    predictor.execute("ALTER TABLE predictor ADD COLUMN '%s' INTEGER DEFAULT 0" % monthDay)

        print "INFO: Predictor database created"
    except:
        print "INFO: Predictor database already existed"


# addToPredictor
# Receives data from a new measurement and updates the corresponding weights in the Predictor database
def addToPredictor(duration, origin, destination, dayOfTheWeek, hourMinute, monthDay):
    # First, check if there is an existing record with the same duration, origin and destination
    predictor.execute('SELECT * FROM predictor WHERE duration=? AND origin=? AND destination=?',
                      (duration, origin, destination))

    result = predictor.fetchone()

    #If no record is found, then add it
    if str(result) == "None":
        # Create a new record
        result = predictor.execute("INSERT INTO predictor(Duration, Origin, Destination, " + dayOfTheWeek + ", " +
                                   hourMinute + ", " + monthDay + ") VALUES (?, ?, ?, ?, ?, ?)",
                                   (duration, origin, destination, 1, 1, 1,))

        connPred.commit()

        print "INFO: Record added to Predictor DB"
    else:
        # Update existing record, increasing weights for the corresponding fields

        #First, capture the current weights for affected field
        predictor.execute("SELECT "+ dayOfTheWeek + ", " + hourMinute + ", " + monthDay +
                          " FROM predictor WHERE Duration=? AND Origin=? AND Destination=?",
                          (duration, origin, destination))

        row = predictor.fetchone()
        dayOfTheWeekWeight = row[0] + 1
        hourMinuteWeight = row[1] + 1
        monthDayWeight = row[2] + 1

        predictor.execute(
            "UPDATE predictor SET " + dayOfTheWeek + "=?, " + hourMinute + "=?, " + monthDay +
            "=? WHERE duration=? AND origin=? AND destination=?", (dayOfTheWeekWeight, hourMinuteWeight, monthDayWeight,
                                                                   duration, origin, destination))
        connPred.commit()

        print "INFO: Record updated in Predictor DB"


# removeFromPredictor
# When a measurement is older than one year, removes its corresponding weights from the Predictor database
def removeFromPredictor(duration, origin, destination, dayOfTheWeek, hourMinute, monthDay):
    # First, check if there is an existing record with the same duration, origin and destination
    predictor.execute('SELECT * FROM predictor WHERE duration=? AND origin=? AND destination=?',
                      (duration, origin, destination))

    result = predictor.fetchone()

    #If no record is found, then ignore
    if str(result) == "None":
        pass
    else:
        # Update existing record, reducing weights for the corresponding fields

        #First, capture the current weights for affected field
        predictor.execute("SELECT "+ dayOfTheWeek + ", " + hourMinute + ", " + monthDay +
                          " FROM predictor WHERE Duration=? AND Origin=? AND Destination=?",
                          (duration, origin, destination))

        row = predictor.fetchone()
        dayOfTheWeekWeight = row[0] - 1
        hourMinuteWeight = row[1] - 1
        monthDayWeight = row[2] - 1

        predictor.execute(
            "UPDATE predictor SET " + dayOfTheWeek + "=?, " + hourMinute + "=?, " + monthDay +
            "=? WHERE duration=? AND origin=? AND destination=?", (dayOfTheWeekWeight, hourMinuteWeight, monthDayWeight,
                                                                   duration, origin, destination))
        connPred.commit()

        print "INFO: Record updated in Predictor DB - Weights decreased"


# makePrediction
# Uses data in the Predictor database to return a prediction for duration with the conditions given
def makePrediction(origin, destination, dayOfTheWeek, hourMinute, monthDay):
    # First, define starting values
    topWeight = -1

    # Go over every entry in the predictor database and determine which one has the highest weight for the
    # given conditions
    predictor.execute("SELECT Duration, "+ dayOfTheWeek + ", " + hourMinute + ", " + monthDay +
                      " FROM predictor WHERE Origin=? AND Destination=?",
                      (origin, destination))

    rows = predictor.fetchall()

    for row in rows:
        totalWeight = row[1] + row[2] + row[3]
        if totalWeight > topWeight:
            topWeight = totalWeight
            topDuration = row[0]

    return topDuration

# Main Flow
homeAddress = "72+Rock+Harbor+Lane,+Foster+City,+CA+94404"
workAddress = "3600+Mission+College+Blvd,++Santa+Clara,+CA+95054"

# Google Directions API server key
#serverKey = "AIzaSyC6oQWg74G15hWw5bab-EVX2BZNKz-cN3w"

# MapQuest Directions API server key
serverKey = "Fmjtd%7Cluurnu0yn5%2C8g%3Do5-9w8l1f"

# Start DB
initDB()

# Start Predictor DB
initPredictor()

# Print header for terminal display
print "MONTH  DAY    HOUR   MINUTE  ORIGIN                                      DESTINATION                 " \
      "                          DISTANCE DURATION   DAY OF THE WEEK     PREDICTION"

infiniteRunner(homeAddress, workAddress, serverKey)