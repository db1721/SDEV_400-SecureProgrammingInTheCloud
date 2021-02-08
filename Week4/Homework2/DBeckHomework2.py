from __future__ import print_function # Python 2/3 compatibility
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import boto3
import botocore
from botocore.exceptions import ClientError
import logging
import json
import decimal

#****************************************
#1st level Functions/Methods for the code
#****************************************
dynamodb = boto3.resource('dynamodb')
classesTable = dynamodb.Table('Classes')

def createTable():
    createdTable = dynamodb.create_table(
    TableName='Classes',
    KeySchema=[
        {
            'AttributeName': 'CourseID',
            'KeyType': 'HASH'  #Partition key
        },
        {
            'AttributeName': 'Subject',
            'KeyType': 'RANGE'  #Sort key
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'CourseID',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'Subject',
            'AttributeType': 'S'
        },

    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
    )
    return createdTable

def populateTable(courseID, subject, catologNo, title):
    populate = classesTable.put_item(
        Item={
                "CourseID": courseID,
                "Subject": subject,
                "CatologNo": catologNo,
                "Title": title
        }
    )
    return populate
    
#****************************************
#2nd level Functions/Methods for the code
#****************************************
def searchSubject(subject, catologNo):
    """Searches database for subject"""
    fe = Key('CourseID').between(1, 10) & Attr('Subject').eq(subject) & Attr('CatologNo').eq(catologNo)
    pe = "Subject, CatologNo, Title"

    response = classesTable.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
        )
    
    dbList = response['Items']
    a_dictionary = dbList[0]

    return print("The title of {Subject} {CatologNo} is {Title}.".format(**a_dictionary))

def checkAgain():
    runAgainChoice = (input("Would you like to search for another tile? (Y or N):\n"))
    try:
        if runAgainChoice == "Y":
            run()
        elif runAgainChoice == "N":
            selected_exit()
        else:
            print("Please make a valid choice to select another title")
    except:
        print("Please make a valid choice to select another title")

def selected_exit():
    """Exits the program"""
    print("\nThank you for using the Catalog Search program")
    print("\n***************************************************************")
#****************************************
#        Executes the code
#****************************************
#Main body of the code that calls the last level of functions
def getSubject():
    try:
        selectedChoice = (input("Enter the Subject:\n"))
        if selectedChoice == "print":
            print("Table status:", createdTable.table_status)
        elif selectedChoice == "check":
            for table in dynamodb.tables.all():
                print(table)
        elif selectedChoice == "create":
            try:
                createTable()
            except:
                print("Table has already been created")
        elif selectedChoice == "add":
            try:
                courseID = int(input("CourseID?:"))
                subject = (input("Subject?:"))
                catologNo = (input("CatologNo?:"))
                title = (input("Title?:"))
                populateTable(courseID, subject, catologNo, title)
                print("Item {0}{1} {2} was added".format(subject, catologNo, title))
            except:
                print("Error in populating")
        elif selectedChoice == "list":
            for table in dynamodb.tables.all():
                print(table)
        else:
            return selectedChoice
    except: 
        print("Error Occured in Main!")

def getCatalog():
    while True:
        try:
            catologChoice = (input("Enter the CatologNo:\n"))
            if catologChoice == "":
                raise Exception("Try Again")
            else:
                return catologChoice
        except:
            print ('Please enter a valid catolog Number')
        
def run():
    while True:
        try:
            while True:
                subject = getSubject()
                catolog = getCatalog()
                try:
                    searchSubject(subject, catolog)
                    break
                except:
                    print("Class does not exist")
            checkAgain()
            break
        except:
            print (searchSubject(subject, catolog))
        
run()