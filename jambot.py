#CS 101 Group 30 
import random
import time
import sys
import os
import copy
from required import create
from required import music

class Patch():
	"""Patch objects contain settings that are relevant to the way the
		robot will behave musically. 
	"""
	def __init__(self, tempo, playStyle, pitches,
				rhythms, tempoSens = 0, pitchSens = 0):
		
		# Stores the original tempo in case tempo changes
		self.baseTempo = tempo 
		# Current tempo used to determine note durations. May change
		self.tempo = tempo
		# The amount the left sensor will change the tempo by when activated
		self.tempoSens = tempoSens
		#  The amount the right sensor will change the pitch by when activated
		self.pitchSens = pitchSens
		# Base notes that generateNotes() can choose from
		self.pitches = pitches
		# Random or predictable playing style
		self.playStyle = playStyle
		# Base rhythms that generateNotes() can choose from
		self.rhythms = rhythms
		self.songTime = 0
		self.displayPitches = ()
	def generateNotes(self, pitchShift, tempoShift):
		# Will return a list of notes generated for the robot to play 
		# based off of the current patch settings
		notes = [] 
		rhythm = [] 
		self.songTime = 0
		
		# Modifiers:
		# Pitch modifier:
		if self.pitchSens == 0:
			# Default modifier for pitch. Given pitches are split into 4 zones.
			# Depending on the value of the left sensor, a slice of the patch's
			# pitches will be used to generate notes 
			split = len(self.pitches)/4
			pitchSelection = self.pitches[(pitchShift-1)*split:pitchShift*split]
			self.displayPitches = pitchSelection # Preserved for printed in GUI()
			pitchSelection = tuple(map(music.note2midi,pitchSelection))
		else:
			# Linear modifier for pitch. Given pitches are all selected.
			# Depending on the value of the left sensor, all pitches
			# are transposed by a number of semitones 
			self.displayPitches = self.pitches 
			modifiedPitches = map(music.note2midi,self.pitches)
			for i in range(len(modifiedPitches)):
				modifiedPitches[i] += (self.pitchSens * (pitchShift-1))
			pitchSelection = tuple(modifiedPitches)
		# Tempo modifier:
		self.tempo = self.baseTempo + self.tempoSens * tempoShift

		# Set style: plays the current patch's pitches in the default given order. 
		# 	note durations are randomly determined from the given rhythms 
		if self.playStyle == 'set':
			for pitch in pitchSelection:
				if rhythm == []:
					rhythm = copy.copy(random.choice(self.rhythms))
				# Each note is a tuple that consists of a pitch and a duration.
				# -Pitch is converted into and int the robot can understand
				# 		by using music.note2midi().
				# -Duration is converted into an appropriate number for the robot
				# 	by using formatTime().
				duration = formatTime(self.tempo,rhythm.pop(0))
				notes.append(tuple((pitch, duration)))
				self.songTime += duration/float(64)
				
		# Random style: randomly plays pitches the current patch 
		# 	note durations are randomly determined from the given rhythms 
		elif self.playStyle == 'random':
			for i in range(len(pitchSelection)):
				if rhythm == []:
					rhythm = copy.copy(random.choice(self.rhythms))
				pitch = random.choice(pitchSelection)
				# Modify/assign pitch and duration to the note (see comments above)
				duration = formatTime(self.tempo,rhythm.pop(0))
				notes.append(tuple((pitch, duration)))
				#
				self.songTime += duration/float(64)
		return notes
		
	def __str__(self):
		
		return str((self.tempo,
					self.tempoSens,
					self.pitchSens,
					self.pitches,
					self.playStyle,
					self.rhythms))
					
def formatTime(BPM, duration):
	"""Takes in a desired BPM and duration and returns an appropriate
	amount of time for the robot to play the note. Minimum is 4."""
	return int(music.milliseconds(BPM,duration)*.064)
					
def importPatches(filename):
	try:
		patchFile = open(filename, 'r')
	except IOError:
		print "File: '"+filename+"' not found."
		exit()
	
	newPatches = []
	patchFile.readline() # First line should just be labels
	for line in patchFile:
		# Parse the file lines to obtain the desired arguments
		line = line.strip()
		patchArgs = line.replace(' ','').split('|')
		sensorArgs = patchArgs[2].split(',')
		pitchArgs = patchArgs[3].strip('()').split(',')
		rhythmArgs = patchArgs[4].split('/')
		for i in range(len(rhythmArgs)):
			rhythmArgs[i] = rhythmArgs[i].strip('()').split(',')
		# Create a new patch based of the extracted arguments
		newPatches += [Patch(int(patchArgs[0]),
							patchArgs[1],
							tuple(pitchArgs),
							tuple(rhythmArgs),
							int(sensorArgs[0]),
							int(sensorArgs[1]))]
	patchFile.close()
	return newPatches

def clearScreen():
	# Refreshes the terminal view
	if os.name == "posix":
		os.system("clear") 
	elif os.name == "nt":
		os.system("cls")

def GUI():
	clearScreen() 
	print "-" * 80 + "|"
	print "Patch: {:<3}".format(patchCount+1)+70*" "+"|"
	print "-" * 80 + "|"
	print "{:<80}".format("Sensors: ")+"|"
	print "Right ({}:{:<3}): {:<65}".format(pitchShift,leftRaw,(leftRaw/25)*"#")+"|"
	print "Left  ({}:{:<3}): {:<65}".format(tempoShift,rightRaw,(rightRaw/25)*"#")+"|"
	print "-" * 80 + "|"
	if not pause:
		print "{:<7}{:<73}".format("Tempo: ",currentPatch.tempo)+"|"
		print "{:<9}{:<71}".format("Pitches: ",currentPatch.displayPitches)+"|"
	else:
		print "{:<80}".format("Paused")+"|"
		print " " * 80 + "|"
	print "-" * 80 + "|"
	
# MAIN 

# Importing patches from a given file name
# either through command line args or input 
if len(sys.argv) > 1:
	patchList = importPatches(sys.argv[1])
else:
	patchList = importPatches(raw_input("Enter Patchfile Name: "))

robot = create.Create("/dev/tty.KeySerial1")
robot.toFullMode()
 
# Press play button to begin
while True:
	# Poll the play button until it's pressed
	sensors = robot.sensors([create.PLAY_BUTTON])
	if sensors[create.PLAY_BUTTON]:
		# When it's lifted up, break out off the waiting loop 
		# and go onto the main program
		while sensors[create.PLAY_BUTTON]:
			sensors = robot.sensors([create.PLAY_BUTTON])
			pass
		else:
			break
	time.sleep(.2) 

patchCount = 0
bumperReleased = True

while True:
	sensors = robot.sensors([
							create.PLAY_BUTTON,
							create.LEFT_BUMP, 
							create.RIGHT_BUMP,
							create.CENTER_WHEEL_DROP,
							create.CLIFF_LEFT_SIGNAL,
							create.CLIFF_RIGHT_SIGNAL,
							create.CLIFF_FRONT_LEFT_SIGNAL,
							create.CLIFF_FRONT_RIGHT_SIGNAL])
	#print "(" #DEBUG
	#for i in sensors:
	#	print sensors[i]
	#print ")"	s
	
	if sensors[create.PLAY_BUTTON]:
		# Finished when the play button is pressed again
		break
		
	# Combining/storing the sensor values in appropriate variables					
	bumperPressed	= sensors[create.LEFT_BUMP] or sensors[create.RIGHT_BUMP]
	leftRaw = sensors[create.CLIFF_FRONT_LEFT_SIGNAL] +\
					sensors[create.CLIFF_LEFT_SIGNAL]
	rightRaw =  sensors[create.CLIFF_RIGHT_SIGNAL] +\
					sensors[create.CLIFF_FRONT_RIGHT_SIGNAL]
	pause =  not sensors[create.CENTER_WHEEL_DROP]
	
	if leftRaw < 30:
		pitchShift = 1
	elif leftRaw < 250:
		pitchShift = 2
	elif leftRaw < 900:
		pitchShift = 3
	else:
		pitchShift = 4
	
	if rightRaw < 30:
		tempoShift = 1
	elif rightRaw < 250:
		tempoShift = 2
	elif rightRaw < 900:
		tempoShift = 3
	else:
		tempoShift = 4
	
	# These bools let us know if it's an appropriate time to change the patch 
	# if the bumper is pressed and it has been released since it was last changed:
	if bumperPressed and bumperReleased and patchCount < len(patchList)-1:	
		patchCount += 1
		bumperReleased = False
	if (not bumperPressed) and (not bumperReleased):
		bumperReleased = True 
	
	currentPatch = patchList[patchCount]
	
	if not pause:
		notes = currentPatch.generateNotes(pitchShift, tempoShift)
		robot.playSong(notes)
		GUI() #Display Params
		#Wait till the current notes is done bit before trying to get more
		time.sleep(currentPatch.songTime)
		currentPatch.songTime = 0
	else:
		GUI()
		time.sleep(.1)
	