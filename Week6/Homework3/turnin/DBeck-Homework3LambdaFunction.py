from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import boto3
import botocore
from botocore.exceptions import ClientError
import logging
import json
import decimal


def lambda_handler(event, context):
    #Enter the user data to search Sports table
    main(event)
    message = finalList
    print_to_log(context)
    return {
        'message': message
    }


#****************************************
#1st level Functions/Methods for the code
#****************************************
dynamodb = boto3.resource('dynamodb')
sportsTable = dynamodb.Table('Sports')
finalList=[]
    
#****************************************
#2nd level Functions/Methods for the code
#****************************************
def searchSport(sport):
    """Searches database for sport"""
    fe = Key('SportID').between(1, 200) & Attr('Sport').eq(sport)
    pe = "Sport"

    response = sportsTable.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
        )
    
    dbList = response['Items']
    a_dictionary = dbList[0]
    
    if sport in a_dictionary:
        return True
    else:
        return False
        
def searchTeam(sport, team):
    """Searches database for sport"""
    fe = Key('SportID').between(1, 200) & Attr('Team').eq(team) & Attr('Sport').eq(sport)
    pe = "Team"

    response = sportsTable.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
        )
    
    dbList1 = response['Items']
    b_dictionary = dbList1[0]
    
    if team in b_dictionary:
        return True
    else:
        return False

    
def searchData(sport, team):
    """Searches database for data"""
    fe = Key('SportID').between(1, 200) & Attr('Sport').eq(sport) & Attr('Team').eq(team)
    pe = "Sport, Team, Score, DayofPlay"

    response = sportsTable.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
        )
    
    dbList = response['Items']

    # return print("{Sport} {Team} {Score} on {DayOfPlay}.".format(**a_dictionary))

    for s in dbList:
        finalList.append('{0} {1} on {2}'.format(s['Team'], s['Score'], s['DayofPlay']))

#****************************************
#        Executes the code
#****************************************
#Main body of the code that calls the last level of functions
def main(event):
    insertedSport = event['insertedSport']
    insertedTeam = event['insertedTeam']
    finalList.clear()
    while True:
        try:
            searchSport(insertedSport)
        except: 
            finalList.append('{0} is not in databse. Please enter a valid sport: '.format(insertedSport))
            finalList.append("      Football")
            finalList.append("      Baseball")
            finalList.append("      Hockey")
            break
        try:
            searchTeam(insertedSport, insertedTeam)
        except:
            if insertedSport == "Baseball":
                finalList.append('{0} is not in databse. Please enter a valid Baseball team: '.format(insertedTeam))
                finalList.append("      Orioles")
                finalList.append("      Rays")
                finalList.append("      Nationals")
                break
            elif insertedSport == "Football":
                finalList.append('{0} is not in databse. Please enter a valid Football team: '.format(insertedTeam))
                finalList.append("      Buccaneers")
                finalList.append("      Ravens")
                finalList.append("      Bills")
                break
            elif insertedSport == "Hockey":
                finalList.append('{0} is not in databse. Please enter a valid Hockey team: '.format(insertedTeam))
                finalList.append("      Capitals")
                finalList.append("      Golden Knights")
                finalList.append("      Lightning")
                break
        return searchData(insertedSport, insertedTeam)
        
    
def print_to_log(newContext):
    # The context object can be used as well for time and other data.
    print("Log stream name:", newContext.log_stream_name)
    print("Log group name:", newContext.log_group_name)
    print("Request ID is:",newContext.aws_request_id)
    print("Millis :",newContext.get_remaining_time_in_millis())