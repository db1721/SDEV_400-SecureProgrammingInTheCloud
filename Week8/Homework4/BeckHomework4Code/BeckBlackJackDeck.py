from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import boto3
import botocore
from botocore.exceptions import ClientError
import logging
import json
import random
import time
import decimal
import BeckBlackJackS3 as bucket
import BeckBlackJackDatabase as bjdb

#****************************************
#Definitions
#****************************************
dynamodb = boto3.resource('dynamodb')
blackjackCardsTable = dynamodb.Table('BlackJackCards')
dealerTotal = 0
playerTotal = 0
playerCards = []
dealerCards = []
playerCardsToCount = []
dealerCardsToCount = []

#****************************************
#Gets the value of the card (COMPLETED)
#****************************************
def getCardValue(card, total):
    """Assign a value to the card that is drawn"""
    if card == "2":
        return 2
    elif card == "3":
        return 3
    elif card == "4":
        return 4
    elif card == "5":
        return 5
    elif card == "6":
        return 6
    elif card == "7":
        return 7
    elif card == "8":
        return 8
    elif card == "9":
        return 9
    elif card == "10":
        return 10
    elif card == "Jack":
        return 10
    elif card == "Queen":
        return 10
    elif card == "King":
        return 10
    elif card == "Ace" and total < 11:
        return 11
    elif card == "Ace":
        return 1
    else:
        print("Error in card value")
        
#****************************************
#Sets Aces in the back (COMPELTED)
#****************************************
def setBestHand(hand):
    """Shifts Ace to end to evalutae the best hand"""
    indexCount = 0
    for card in hand:
        if card == "Ace":
            hand.pop(indexCount)
            hand.append(card)
            indexCount += 1
        else:
            indexCount += 1
    return hand

#****************************************
#Draw Random Card (COMPLETED)
#****************************************
def drawRandomCard():
    """Draws Card at random"""
    gen_num = random.randint(0, 12)
    deck = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
    return deck[gen_num]
#     fe = Key('CardID').eq(gen_num)
#     pe = "CardName"

#     response = blackjackCardsTable.scan(
#         FilterExpression=fe,
#         ProjectionExpression=pe
#         )
    
#     dbList = response['Items']
#     # a_dictionary = dbList[0]
    
#     for card in dbList:
#         return card['CardName']

#****************************************
#Draws Cards for Dealer (COMPLETED)
#**************************************** 
def dealerDraw():
    """Draws a card until the dealer reaches 17 or beats the player"""
    global dealerTotal
    global dealerCardsToCount 
    global playerTotal
    
    dealerTotal = 0
    
    while dealerTotal < 17 or dealerTotal < playerTotal:
        dealerTotal = 0
        card = drawRandomCard()
        dealerCards.append(card)
        dealerCardsToCount = setBestHand(dealerCards)
        for i in dealerCardsToCount:
            dealerTotal += getCardValue(i, dealerTotal)
        
    return dealerCards
    
#****************************************
#Shows 1 dealer card (COMPLETED)
#**************************************** 
def dealerShowFirstCard():
    """Shows only the first cards from the dealer"""
    return dealerCards[0]
    
#****************************************
#Draws Cards for Player (COMPLETED)
#**************************************** 
def playerDraw():
    """Player's initial two card draw"""
    global playerTotal
    global playerCardsToCount
    
    playerTotal = 0
    
    card1 = drawRandomCard()
    playerCards.append(card1)
    
    card2 = drawRandomCard()
    playerCards.append(card2)
    
    playerCardsToCount = setBestHand(playerCards)
    
    for card in playerCardsToCount:
        playerTotal += getCardValue(card, playerTotal)
    
    return playerCards
    
#****************************************
#Draws Player Card after hit (COMPLETED)
#**************************************** 
def playerHit():
    """Draws one card for the player"""
    global playerTotal
    global playerCardsToCount

    card = drawRandomCard()
    playerTotal += getCardValue(card, playerTotal)
    playerCards.append(card)
    
    playerCardsToCount = setBestHand(playerCards)

#****************************************
#Shows all Player Cards (COMPLETED)
#****************************************
def showAllPlayerCards():
    """Reveals all player's cards"""
    for card in playerCards:
        print(card)

#****************************************
#Checks if dealer wins loses of busts
#****************************************
def winLoseDrawBust(dealer, player, bet):
    """evaluates the players cards and returns the winning/losing amount"""
    if player == 21:
        bjdb.setPlayerWin()
        bucket.getS3object("blackjack.jpeg")
        return round(bet * 2)
    elif dealer > 21:
        bjdb.setPlayerWin()
        bucket.getS3object("youwin.jpeg")
        return round(bet * 1.5)
    elif player > 21:
        bjdb.setPlayerLoss()
        bucket.getS3object("bust.jpeg")
        return round(bet - (bet * 2))
    elif dealer < player:
        bjdb.setPlayerWin()
        bucket.getS3object("youwin.jpeg")
        return round(bet * 1.5)
    elif player < dealer:
        bjdb.setPlayerLoss()
        bucket.getS3object("dealerwins.jpeg")
        return round(bet - (bet * 2))
    elif dealer == player:
        bucket.getS3object("draw.jpg")
        return round(bet)

#****************************************
#reshuffles the deck
#****************************************
def reshuffle():
    """Resets all the variables after the hand is completed"""
    global dealerTotal
    global playerTotal
    global playerCards
    global dealerCards
    
    dealerTotal = 0
    playerTotal = 0
    playerCards = []
    dealerCards = []
    playerCardsToCount = []
    dealerCardsToCount = []
