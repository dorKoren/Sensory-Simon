#Simon by Dor Koren 23021803, Gal Ron 308344548 and Dolev Binness 312526031
#Video Link - https://youtu.be/FK7ntbduK5w

import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import RPi.GPIO as GPIO
from time import sleep
import time
import wiringpi
import random

GPIO.setwarnings(False)


#Adafruit pins
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25

mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

#Speaker Pin
speaker = 22


#Light Pins
redLight    = 6
yellowLight = 13
greenLight  = 19
blueLight   = 26

#sensors
redSensor    = 0
yellowSensor = 0
greenSensor  = 0
blueSensor   = 0

#Sound frequencies
redFreq    = 440
yellowFreq = 523
greenFreq  = 659
blueFreq   = 784
loseFreq   = 880


#Speed frequenies
speedFreq    = 1
maxSpeedFreq = 0.4

#Speed lights
speedLight    = 1
maxSpeedLight = 0.4

#Arrays
lights      = [redLight, yellowLight, greenLight, blueLight]
sensors     = [redSensor, yellowSensor, greenSensor, blueSensor]
frequencies = [redFreq, yellowFreq, greenFreq, blueFreq]


#initiate wiringpi
wiringpi.wiringPiSetupGpio()
wiringpi.softToneCreate(speaker)

#flags used to signal game status
isDisplayingPattern = False
isWonCurrentLevel   = False
isGameOver          = False

#game state
currentLevel       = 1
currentStepOfLevel = 0
pattern            = []


#functions

def initialGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(lights, GPIO.OUT, initial=GPIO.LOW)



def playFreq(freq, light):
    print("play {0} frequency\n".format(freq))
    wiringpi.softToneWrite(speaker, freq)
    GPIO.output(light, GPIO.HIGH)
    sleep(speedFreq)
    GPIO.output(light, GPIO.LOW)
    wiringpi.softToneWrite(speaker, 0)
    sleep(0.3)


def addNewColorToPattern():
    global isWonCurrentLevel, currentStepOfLevel
    isWonCurrentLevel = False
    currentStepOfLevel = 0
    nextColor = random.randint(0, 3)
    pattern.append(nextColor)
    print("color {0} was append".format(lights[nextColor]))
    
def printLightToScreen(light):
    if light == 6:
        print("Red\n")
    if light == 13:
        print("Yellow\n")
    if light == 19:
        print("Green\n")
    if light == 26:
        print("Blue\n")


def checkLevelOfDifficulty():
    global speedFreq, speedLight, maxSpeedFreq, maxSpeedLight, currentLevel

    if currentLevel % 4 == 0 and speedFreq >= maxSpeedFreq and speedLight >= maxSpeedLight:
        speedLight -= 0.1
        speedFreq -= 0.1
        print("Level of difficulty was updated!")
        
def displayPatternToPlayer():
    global isDisplayingPattern

    isDisplayingPattern = True
    GPIO.output(lights, GPIO.LOW)

    for i in range(currentLevel): 
        printLightToScreen(lights[pattern[i]])

        checkLevelOfDifficulty()       
        
        playFreq(frequencies[pattern[i]], lights[pattern[i]])
              
    isDisplayingPattern = False
    
def siren():
    for freq in range(440, 880, 20):
        wiringpi.softToneWrite(speaker, freq)
        sleep(0.05)

    for freq in range(880, 440, -20):
        wiringpi.softToneWrite(speaker, freq)
        sleep(0.05)


def waitForPlayerResponse():
    global currentStepOfLevel, currentLevel, isWonCurrentLevel, isGameOver

    while not isWonCurrentLevel and not isGameOver:
        if not isDisplayingPattern and not isWonCurrentLevel and not isGameOver:

            currentSensor = -1

            #set the values of the sensors
            for i in range(4):
                sensors[i] = mcp.read_adc(i)
                
             #check if one of the sensors reach to the expected value
            if sensors[0] > 1000:
                playFreq(frequencies[0], lights[0])
                currentSensor = sensors[0]

            if sensors[1] < 200:
                playFreq(frequencies[1], lights[1])
                currentSensor = sensors[1]

            if sensors[2] > 900:
                playFreq(frequencies[2], lights[2])
                currentSensor = sensors[2]

            if sensors[3] > 800:
                playFreq(frequencies[3], lights[3])
                currentSensor = sensors[3]


            if currentSensor != -1:
                if currentSensor == sensors[pattern[currentStepOfLevel]]:
                    currentStepOfLevel += 1

                    if currentStepOfLevel >= currentLevel:
                        currentLevel += 1
                        isWonCurrentLevel = True
                        print("you won current level\n")

                else:
                    isGameOver = True
                    siren()
            sleep(0.1)

def resetGame():
    global isDisplayingPattern, isWonCurrentLevel, isGameOver
    global currentLevel, currentStepOfLevel, pattern
    global speedFreq, speedLigh
    isDisplayingPattern = False
    isWonCurrentLevel   = False
    isGameOver          = False
    currentLevel        = 1
    currentStepOfLevel  = 0
    speedFreq           = 1
    speedLigh           = 1
    pattern             = []
    GPIO.output(lights, GPIO.LOW)

    print("Game was reset!")


def startGame():
    while True:
        addNewColorToPattern()
        displayPatternToPlayer()
        waitForPlayerResponse()

        if isGameOver:
            print("You Loosed!\n".format(currentLevel-1))
            resetGame()
            print("New Round Has Start!")

        sleep(0.5)

# Main
print("Let S-Y-M-O-N begin!")
initialGPIO()
startGame() 