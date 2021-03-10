from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import boto3
import botocore
from botocore.exceptions import ClientError
import logging
import json
import decimal
import random
import time
import BeckBlackJackDatabase as bjdb
import BeckBlackJackS3 as bjs3
import BeckBlackJackDeck as deck
import BeckBlackJackS3 as bucket

#****************************************
#Definitions/Variables
#****************************************
dynamodb = boto3.resource('dynamodb')
blackjackTable = dynamodb.Table('BlackJack')
setPlayerHandTotal = 0
setPlayerWins = 0
setPlayerLoss = 0
setPlayerChips = "500"
playerBet = 20
playerWinnings = 10
keepPlaying = True
newDeal = True

#****************************************
#5th level Functions/Methods for the code
#****************************************
def revealWinLose():
    """Reveals if the player wins or loses"""
    print("\nDealer Draws: ")
    time.sleep(.5)
    for card in deck.dealerCards:
        print(card, sep=' ', end=' ', flush=True); time.sleep(1)
    time.sleep(.5)
    print("\n\nDealer total is {0}".format(deck.dealerTotal))
    print("Player total is {0}".format(deck.playerTotal))
    
def revealWinLoseNoDealerDraw():
    print("Player total is {0}".format(deck.playerTotal))

#****************************************
#4th level Functions/Methods for the code
#****************************************
def runPlayerChoice(choice):
    """Accepts choice to hit or stand"""
    global continueDraw
    if choice == "H" or choice == "h" or choice == "Hit" or choice == "hit":
        deck.playerHit()
        print("Player Draws:", ' '.join(deck.playerCards))
        print("Player Total: {1} || Dealer First Card: {0} ".format(deck.dealerCards[0], deck.playerTotal))
    elif choice == "S" or choice == "s" or choice == "Stand" or choice == "stand":
        continueDraw = False
        revealWinLose()
    else:
        print("Please enter Hit or Stand")

def placeBet():
    """receives input for bet amount"""
    global playerBet
    isInt = True
    while isInt == True:
        try:
            bet = int(input("\nPlace your bet: "))
            isInt = False
        except:
            print("Please enter an integer")
    playerBet = bet
    
#****************************************
#3rd level Functions/Methods for the code
#****************************************
def dealerStart():
    """Shows dealer's first card"""
    global continueDraw
    continueDraw = True
    deck.dealerDraw()
    print("\nDealer Draws: {}".format(deck.dealerShowFirstCard()))

def playerInitialDraw():
    """Shows player's first draw"""
    global playerCards
    playerCards = deck.playerDraw()
    print("Player Draws: {0} {1}".format(playerCards[0], playerCards[1]))
    time.sleep(.5)
    print("Player Total: {1} || Dealer First Card: {0} ".format(deck.dealerCards[0], deck.playerTotal))
    
def getPlayerChoice():
    """Get hit or stand choice from the player"""
    choice = input("Hit(H) or Stand(S): ")
    return choice
    
def getPlayAgainChoice():
    """Asks user if they want to play again"""
    global newDeal
    
    t = True
    while t == True:
        choice = input("Play Again?: ")
        if choice == "Y" or choice == "y" or choice == "Yes" or choice == "yes":
            newDeal = True
            t = False
            return newDeal
        elif choice == "N" or choice == "n" or choice == "No" or choice == "no":
            newDeal = False
            return newDeal
        else:
            print("Please enter Yes or No")
    
def calculateChips():
    """Calculates winnings"""
    global playerWinnings
    playerWinnings = 0
    global setPlayerChips
    global playerBet
    playerWinnings = deck.winLoseDrawBust(deck.dealerTotal, deck.playerTotal, playerBet)
    setPlayerChips = int(setPlayerChips) + playerWinnings
    bjdb.setPlayerChips(str(setPlayerChips))
    print("Result: {0} || You now have ${1} in chips\n".format(playerWinnings, setPlayerChips))
        
def shuffleDelay():
    """Shuffle loading screen"""
    deck.reshuffle()
    w = "\nSHUFFLING...\n"
    for l in w:
        print(l, end=' ', flush=True); time.sleep(.15)

#****************************************
#2nd level Functions/Methods for the code
#****************************************
def addUserText(playerName):
    """checks if the user wnats tobe added to the database"""
    while True:
        user = input("{} is not in database. Would you like to add user? (Y or N): ".format(playerName))
        if user == "Y" or user == "Yes" or user == "y" or user == "yes":
            bjdb.addUser(playerName)
            bjdb.setDBPlayerWin(0)
            bjdb.setDBPlayerLoss(0)
            print("{} was added and given 500 chips to start".format(playerName))
            break
        elif user == "N" or user == "No" or user == "n" or user == "no":
            main()
        else:
            print("Please Enter Yes or No")

def selected_exit():
    """Exits the program"""
    print("\n******************Thank you for Playing BlackJack***********************")
    
def playGame():
    """Runs the blackjack game"""
    global keepPlaying
    global continueDraw
    global newDeal
    global playerBet
    newDeal = True
    continueDraw = True
    keepPlaying = True
    setWinLose = False
    while keepPlaying == True:
        placeBet()
        dealerStart()
        playerInitialDraw()
        while continueDraw == True:
            if deck.playerTotal > 21:
                print("\n|BUST|\n")
                bucket.getS3object("bust.jpeg")
                setWinLose = True
                bjdb.setPlayerLoss()
                revealWinLoseNoDealerDraw()
                calculateChips()
                continueDraw = False
            elif deck.playerTotal == 21:
                print("\n|BLACKJACK!|\n")
                bjdb.setPlayerWin()
                bucket.getS3object("blackjack.jpeg")
                setWinLose = True
                revealWinLoseNoDealerDraw()
                calculateChips()
                continueDraw = False
            else:
                setWinLose = False
                runPlayerChoice(getPlayerChoice())
        if setWinLose == False:
            calculateChips()
        getPlayAgainChoice()
        if newDeal == True:
            shuffleDelay()
        else:
            deck.reshuffle()
            keepPlaying = False
    selectMenu()
    
#****************************************
#1st level Functions/Methods for the code
#****************************************
def enterUser():
    """receives input for user name"""
    user = input("Enter your user name: ")
    bjdb.playerName = user
    return user
    
def checkForPlayer(playerName):
    """checks if player is in databse. Runs addUserText if not found"""
    global setPlayerChips
    if bjdb.searchForPlayer(playerName) == True:
        setPlayerChips = bjdb.getPlayerChips(playerName)
        print("Welcome {0}! You have {1} chips.".format(playerName, bjdb.getPlayerChips(playerName)))
    else:
        return addUserText(playerName)

def selectMenu():
    """runs the game menu"""
    global keepPlaying
    keepPlaying = True
    gameOn = True
    while gameOn == True:
        try:
            menuChoice = int(input("\nMain Menu:"
                                    "\n\t1. Play BlackJack"
                                    "\n\t2. Change Player"
                                    "\n\t3. See chip amount"
                                    "\n\t4. See Win/Loss Record"
                                    "\n\t5. Reset Record"
                                    "\n\t6. Exit the Program\n"))
            if menuChoice == 1:
                playGame()
            elif menuChoice == 2:
                main()
            elif menuChoice == 3:
                print("\n{0} has ${1} in chips".format(bjdb.playerName, bjdb.getPlayerChips(bjdb.playerName)))
            elif menuChoice == 4:
                print("{0} has a record of {1} wins and {2} losses".format(bjdb.playerName, bjdb.getPlayerWins(), bjdb.getPlayerLosses()))
            elif menuChoice == 5:
                bjdb.setDBPlayerWin(0)
                bjdb.setDBPlayerLoss(0)
                print("\n{0} has been set to 0 wins and 0 losses".format(bjdb.playerName))
            elif menuChoice == 6:
                selected_exit()
                break
        except:
            print("Please enter 1, 2, 3, 4 or 5")

#****************************************
#        Executes the code
#****************************************
def main():
    """Main of the program""
    while True:
        try:
            checkForPlayer(enterUser())
            selectMenu()
            break
        except:
            print("\nError Occured in Main!")
    
print("********Welcome to the BlackJack Game!********")
main()