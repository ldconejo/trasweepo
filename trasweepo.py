__author__ = 'luisconejo'
# Polls traffic to and from a particular address and saves the results into a database

# Individual procedures

# Creates the database for results
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
# to save the results to the database
def collectData():
    pass

# f