noteNames = ('C','C#','D','D#','E','F','F#','G','G#','A','A#','B')

intervals = {'P1':0,'m2':1,'M2':2,'m3':3,'M3':4,'P4':5,'TT':6,
			 'P5':7,'m6':8,'M6':9,'m7':10,'M7':11,'P8':12}
			 
noteLengths = {'w':4.0,'h':2.0,'q':1.0,'e':0.5,'s':0.25,'ts':0.125,'sf':0.625}
	
major = ['P1','M2','M3','P4','P5','M6','M7','P8']	
minor = ['P1','M2','m3','P4','P5','m6','m7','P8']			 
			 
class note():
	
	def __init__(self, midiNum, duration = None): ##Annotation->int
	
		self.midi = midiNum
		self.note = noteNames[midiNum%12]
		self.octave = (midiNum/12) - 1 ##IntDivision
		self.duration = duration

	def frequency(self, ref = 440):
		"""Return a note's frequency
		
		Keyword Arguments:
		ref -- the reference frequency for A4 (default = 440)
		
		"""	
		#f = ref * (a)^n
		root = 2**(1/float(12)) #a ##FloatDivision
		dist = self.midi - 69 #n 
		return ref * (root**dist)
		
	def modulated(self, interval):
		"""Return a note shifted by the given interval
		
		Keyword Arguments:
		interval -- string representing the interval that should be shifted by
		
		"""
		negative = False
		if interval[0] == '-':
			negative = True
			interval.replace('-','',1)

		semitones = intervals[interval]
		
		if negative:
			#For transposing downwards
			semitones *= -1
				
		newNote = note(self.midi+semitones)
		
		return newNote
		
	def __str__(self):
		
		return (self.note + str(self.octave))

class melody():

	def __init__(self, *notes):
	
		self.notes = notes		

def milliseconds(BPM, duration):
	"""Return the length of a note in milliseconds
		
		Keyword Arguments:
		BPM -- tempo of the song in beats per minute
		duration -- shorthand string representation of the note length 
		
	"""	
	if duration == None: 
		duration = 1
	#Divide BPM by 60s to get beats per second
	#Divide by 1000ms to get milliseconds per beat
	#Multiply by fractional duration to get total milliseconds 
	return noteLengths[duration] * (1000/(BPM/60))
	
def note2midi(note):
	"""Return the midi number of a given string representation of a note
		
		Keyword Arguments:
		note -- a shorthand representation of a note (ex. 'C4')
		
	"""	
	try:
		letterVal = noteNames.index(note[0:-1])
	except ValueError, e:
		print "Unidentified note: " + str(note)
		print e
		exit()
	octave = ((int(note[-1])*12)+12)
	return octave+letterVal
	