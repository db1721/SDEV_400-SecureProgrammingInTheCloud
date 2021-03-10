from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import boto3
import botocore
from botocore.exceptions import ClientError
import logging
import json
import decimal
import random

#****************************************
#Definitions
#****************************************
dynamodb = boto3.resource('dynamodb')
blackjackTable = dynamodb.Table('BlackJack')
playerName = "Test"
playerID = 1

#****************************************
#Count ID (COMPLETED)
#****************************************
def countID():
    """Counts ID's to make ID for new User"""
    num = 1
    fe = Key('PlayerID').between(1, 100)

    response = blackjackTable.scan(
        FilterExpression=fe
        )
    
    dbList = response['Items']
    # b_dictionary = dbList[0]

    for i in dbList:
        num += 1
        
    return num
    
#****************************************
#Search for player in Database (COMPLETED)
#****************************************
def searchForPlayer(player):
    """Searches database for user"""
    global playerName
    global playerID
    
    fe = Key('PlayerID').between(1,100) & Attr('PlayerName').eq(player)
    pe = "PlayerID, PlayerName"

    response = blackjackTable.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
        )
    
    dbList = response['Items']
    # a_dictionary = dbList[0]
    
    for p in dbList:
        if p['PlayerName'] == player:
            playerName = player
            playerID = p['PlayerID']
            return True
        else:
            return False
            
#****************************************
#Add User (COMPLETED)
#****************************************        
def addUser(newPlayer):
    """Add users to database"""
    global playerName
    global playerID
    
    makeID = countID()
    playerName = newPlayer
    playerID = makeID
    populate = blackjackTable.put_item(
        Item={
                "PlayerID": makeID,
                "PlayerName": newPlayer,
                "Chips": "500"
        }
    )
    return populate
    
#****************************************
#Retreives chip count (COMPLETED)
#**************************************** 
def getPlayerChips(playerName):
    """Searches database for player's chip count"""
    fe = Key('PlayerID').between(1,100) & Attr('PlayerName').eq(playerName)
    pe = "PlayerName, Chips"

    response = blackjackTable.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
        )
    
    dbList = response['Items']
    a_dictionary = dbList[0]
    
    for p in dbList:
        return p['Chips']
        
    
#****************************************
#Saves new chip count (COMPLETED)
#**************************************** 
def setPlayerChips(newChipCount):
    """Searches database to change player's chip count"""
    global playerName
    global playerID
    
    response = blackjackTable.update_item(
        Key={
            'PlayerID': playerID,
            'PlayerName': playerName
        },
        UpdateExpression="SET #Chips = :c",
        ExpressionAttributeNames= {
            '#Chips': 'Chips',
        },
        ExpressionAttributeValues={
            ':c': str(newChipCount)
        },
        ReturnValues="UPDATED_NEW"
    )
    return response
    
#****************************************
#Saves new win record (COMPLETED)
#**************************************** 
def setDBPlayerWin(win):
    """Saves new win record"""
    global playerName
    global playerID
    
    response = blackjackTable.update_item(
        Key={
            'PlayerID': playerID,
            'PlayerName': playerName
        },
        UpdateExpression="SET #Wins = :w",
        ExpressionAttributeNames= {
            '#Wins': 'Wins',
        },
        ExpressionAttributeValues={
            ':w': int(win)
        },
        ReturnValues="UPDATED_NEW"
    )
    return response
    
#****************************************
#Saves new loss record (COMPLETED)
#**************************************** 
def setDBPlayerLoss(loss):
    """Saves new loss record"""
    global playerName
    global playerID
    
    response = blackjackTable.update_item(
        Key={
            'PlayerID': playerID,
            'PlayerName': playerName
        },
        UpdateExpression="SET #Losses = :l",
        ExpressionAttributeNames= {
            '#Losses': 'Losses',
        },
        ExpressionAttributeValues={
            ':l': int(loss)
        },
        ReturnValues="UPDATED_NEW"
    )
    return response
    
#****************************************
#Retreives win record (COMPLETED)
#**************************************** 
def getPlayerWins():
    """Searches database for win record"""
    fe = Key('PlayerID').between(1,100) & Attr('PlayerName').eq(playerName)
    pe = "PlayerName, Wins"

    response = blackjackTable.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
        )
    
    dbList = response['Items']
    a_dictionary = dbList[0]
    
    for p in dbList:
        return p['Wins']
        
#****************************************
#Retreives loss record (COMPLETED)
#**************************************** 
def getPlayerLosses():
    """Searches database for player's loss record"""
    fe = Key('PlayerID').between(1,100) & Attr('PlayerName').eq(playerName)
    pe = "PlayerName, Losses"

    response = blackjackTable.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
        )
    
    dbList = response['Items']
    a_dictionary = dbList[0]
    
    for p in dbList:
        return p['Losses']
        
#****************************************
#Saves new loss record (COMPLETED)
#**************************************** 
def setPlayerLoss():
    """Sets new loss record"""
    num = getPlayerLosses()
    temp = num + 1
    setDBPlayerLoss(temp)
    
#****************************************
#Saves new loss record (COMPLETED)
#**************************************** 
def setPlayerWin():
    """Sets new win record"""
    num = getPlayerWins()
    temp = num + 1
    setDBPlayerWin(temp)
    
    
#****************************************
#Creates the table in DynamoDB (COMPLETED)
#****************************************  
def createTable():
    """Searches database for data"""
    createdTable = dynamodb.create_table(
    TableName='BlackJack',
    KeySchema=[
        {
            'AttributeName': 'PlayerID',
            'KeyType': 'HASH'  #Partition key
        },
        {
            'AttributeName': 'PlayerName',
            'KeyType': 'RANGE'  #Sort key
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'PlayerID',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'PlayerName',
            'AttributeType': 'S'
        },

    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 100,
        'WriteCapacityUnits': 100
    }
    )
    return createdTable