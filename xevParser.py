#!/usr/bin/env python3
 
import subprocess

import sys
import subprocess
import time
from numpy import interp
import rtmidi
 
# This program parses xev input from stdin for the purpose of midi instrument

class RtMidi:
  midiout = None
  def __init__(self):
    self.midiout = rtmidi.MidiOut()
    #self.available_ports = midiout.get_ports()
    self.midiout.open_virtual_port("My virtual output")
  def send(self, message):
    self.midiout.send_message(message)

class Key:
  keycode = 0
  mod = 0
  state = 0
  def __init__(self, keycode):
    self.keycode = keycode
    #self.mod = mod
  def getKeycode(self):
    return(self.keycode)
  def getMod(self):
    return(self.mod)
  def setState(self, state):
    if state != self.state:
      self.state = state
      print(self.keycode, self.state)
      return(True)
    return(False)
  def getState(self):
    return(self.state)

class Axis:
  x = 0
  y = 0
  def setX(self, x):
    if x != self.x:
      self.x = x
      return(True)
    return(False)
  def setY(self, y):
    if y != self.y:
      self.y = y
      return(True)
    return(False)
  def getX(self):
    return(self.x)
  def getY(self):
    return(self.y)

class VirtualInstrument:
    octave = 4
    gString = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    dString = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]
    aString = ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";"]
    eString = ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"]
    strings = [eString, aString, dString, gString]
    eStringStart = 36
    aStringStart = eStringStart + 5
    dStringStart = aStringStart + 5
    gStringStart = dStringStart + 5
    keys = []
    axis = Axis()
    def __init__(self):
      for string in self.strings:
        for tone in string:
          self.keys.append(Key(ord(tone)))
    def parseKeyEvent(self, keycode, mod, state):
      if(chr(keycode) == "-"):
        print("getSize")
        xW.getSize()
      elif(keycode == 65365 and state):
        self.octave += 1
        print("octave", self.octave)
      elif(keycode == 65366 and state):
        self.octave -= 1
        print("octave", self.octave)
      for key in self.keys:
        if str(key.getKeycode()) == str(keycode):
          if (key.getState != state):
            #key.setState(state)
            if(chr(keycode) in self.eString):
              note = self.eString.index(chr(keycode))+ self.eStringStart + (self.octave * 5)
            elif(chr(keycode) in self.aString):
              note = self.aString.index(chr(keycode))+ self.aStringStart + (self.octave * 5)
            elif(chr(keycode) in self.dString):
              note = self.dString.index(chr(keycode))+ self.dStringStart + (self.octave * 5)
            elif(chr(keycode) in self.gString):
              note = self.gString.index(chr(keycode))+ self.gStringStart + (self.octave * 5)
            rm.send([0x90, note, state*100])
            print(note, state)
    def parseMouseEvent(self, x, y):
      if self.axis.setX(x): self.sendMouseEventX()
      if self.axis.setY(y): self.sendMouseEventY()
    def sendMouseEventX(self):
      print("CC11: ", self.axis.getX())
      rm.send([0xb0, 0x0b, self.axis.getX()])
    def sendMouseEventY(self):
      print("CC5: ", self.axis.getY())

class x11Window:
  xMax = 0
  yMax = 0
  xPerMax = 127
  yPerMax = 127
  def getSize(self):
    id = subprocess.check_output(["xdotool", "search", "--name",  "Event Tester"]).decode('utf-8').strip()
    xwininfo = subprocess.check_output(["xwininfo", "-id", id]).decode('utf-8').split()
    self.xMax = int(xwininfo[23])
    self.yMax = int(xwininfo[25])
  def getPercent(self, x, y):
   #print(self.xMax, self.yMax)
   x = int(x)
   y = int(y)
   if(x > self.xMax): x = self.xMax 
   if(x < 0): x = 0 
   if(y > self.yMax): y = self.yMax
   if(y < 0): y = 0 
   xPer = int(interp(x ,[0, self.xMax], [0, self.xPerMax]))
   yPer = int(interp(y ,[0, self.yMax], [self.yPerMax, 0]))
   #print(xPer, yPer)
   return((xPer, yPer))
 
class xevReader:
  keyPress = False
  keyPressLines = 5
  keyRelease = False
  keyReleaseLines = 4
  motionNotify = False
  motionNotifyLines = 2
  linesCounter = 0
  lineset = []
  lineSetCopy = []
  isReadyBool = False
  def isReady(self):
    return(self.isReadyBool)
  def read(self, line):
    if(len(line) > 2):
      # trigger action
      if(line.split()[0] == "KeyPress"):
        self.keyPress = True
      elif(line.split()[0] == "KeyRelease"):
        self.keyRelease = True
      elif(line.split()[0] == "MotionNotify"):
        self.motionNotify = True
      # react to trigger
      if(self.keyPress):
        if(self.linesCounter < self.keyPressLines):
            self.lineset.append(line)
            self.linesCounter += 1
        else:
            #print(self.lineset)
            self.isReadyBool = True
            self.lineSetCopy = list(self.lineset)
            self.lineset = []
            self.linesCounter = 0
            self.keyPress = False
      elif(self.keyRelease):
        if(self.linesCounter < self.keyReleaseLines):
            self.lineset.append(line)
            self.linesCounter += 1
        else:
            #print(self.lineset)
            self.isReadyBool = True
            self.lineSetCopy = list(self.lineset)
            self.lineset = []
            self.linesCounter = 0
            self.keyRelease = False
      elif(self.motionNotify):
        if(self.linesCounter < self.motionNotifyLines):
            self.lineset.append(line)
            self.linesCounter += 1
        else:
            #print(self.lineset)
            self.isReadyBool = True
            self.lineSetCopy = list(self.lineset)
            self.lineset = []
            self.linesCounter = 0
            self.motionNotify = False
  def getEvent(self):
    self.isReadyBool = False
    return(self.lineSetCopy)

class xevParser:
  def parse(self, event):
    if(event[0].split()[0] == "KeyPress"):
      mod = (event[2].split()[1][2:-1])
      keycode = (int(event[2].split()[5][2:-1], 16))
      state = 1
      print("DEBUG:", keycode, mod, state)
      vI.parseKeyEvent(keycode, mod, state)
    elif(event[0].split()[0] == "KeyRelease"):
      mod = (event[2].split()[1][2:-1])
      keycode = (int(event[2].split()[5][2:-1], 16))
      state = 0
      print("DEBUG:", keycode, mod, state)
      vI.parseKeyEvent(keycode, mod, state)
    elif(event[0].split()[0] == "MotionNotify"):
      pair = event[1].split()[6][1:-2].split(",")
      x = pair[0]
      y = pair[1]
      xPer, yPer = xW.getPercent(x, y)
      #print(xPer, yPer)
      vI.parseMouseEvent(xPer, yPer)
          
def main():
  for line in sys.stdin:
    xR.read(line)
    if(xR.isReady()):
      xP.parse(xR.getEvent())

if __name__ == "__main__":
    # execute only if run as a script
    try:
        process = subprocess.Popen("xset r off".split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        xW = x11Window()
        xW.getSize()
        vI = VirtualInstrument()
        xR = xevReader()
        xP = xevParser()
        rm = RtMidi()
        main()
    except KeyboardInterrupt:
        process = subprocess.Popen("xset r on".split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
