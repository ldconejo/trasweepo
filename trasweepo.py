__author__ = 'luisconejo'
# Polls traffic to and from a particular address and saves the results into a database

# Individual procedures

# Creates the database for results. The database will have a single table with the following fields
# Month, Day, Hour, Minute (rounded to the nearest 5-minute block), origin, destination
def createDB():
    pass

# Sends a request to Google Directions API, taking a starting address, destination address and returning the JSON
# output
def getDirections(startingAddress, destinationAddress):
    pass

# Saves a result into the database
def saveIntoDB(startingAddress, destinationAddress, totalTime):
    pass

# Calls getDirections for a particular route, process the output to extract the total driving time and call saveIntoDB
# to save the results to the database, adjusts the time stamp using roundTimeStamp.
def collectData(startingAddress, destinationAddress):
    pass

# Rounds a time stamp to match one particular day-of-the-year-hour-minute combination. These will be space five minutes
# from each other. There are 288 readings per day with a maximum of 366 days per year, that gives a fixed database size
# of 105408, doubled to 210816 entries, as time in both directions will be calculated.
def roundTimeStamp():
    pass

# Runs indefinitely until a key is pressed, collecting data every five (5) minutes
# Uses a time and collectData
def infiniteRunner(startingAddress, destinationAddress):
    pass