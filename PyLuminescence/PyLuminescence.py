from __future__ import division
import math
import pyaudio as PyAudio # sudo apt-get install python-pyaudio
from time import sleep
import sys
import audioop
import struct
from array import array
import pygame
import Tkinter
from Tkinter import *
import tkMessageBox
import json
from pygame.locals import *
from pygame.mixer import Sound, get_init, pre_init
try:
    # global config
    # config = json.loads(open("./PyLuminescence.config",'r+').read())
    # print(config)
    print(open("./PyLuminescence.config",'r+').read())
except:
    config = open("./PyLuminescence.config",'w+')
    config.write("{}")
    config.close()
    config = json.loads(open("PyLuminescence.config",'r+').read())
set_frequency = 100
set_volume = 0.0
button = ""
initial_volume = 0.4
global frequency_range
global key
key = 0
frequency_range = [21000,25000]
class Note(Sound):

    def __init__(self, frequency, volume=.1):
        self.frequency = frequency
        Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        period = int(round(get_init()[0] / self.frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (abs(get_init()[1]) - 1) - 1
        for time in xrange(period):
            if time < period / 2:
                samples[time] = amplitude
            else:
                samples[time] = -amplitude
        return samples

p = PyAudio.PyAudio()
stream = p.open(format=PyAudio.paInt16, # 8bit
                    channels=1, # mono
                    rate=96000,
                    input=True,
                    output=False,
                    frames_per_buffer=2048)
pre_init(96000, -16, 1, 1024)
pygame.init()

top = Tkinter.Tk()
top.title("PyLuminescence")


def Tune():
    global initial_volume
    global set_frequency
    volume = initial_volume
    display_volume.configure(text="Volume: " + str(volume))
    temp_best_amplitude=0.0
    temp_best_frequency=0.0
    display_percentage = Label(top, text="")
    display_percentage.grid(row=1,column=4)
    display_percentage.configure(text="%")
    for frequency in range(21000,25000,10):
        Note(frequency,volume).play(-1)
        sleep(0.1)
        stream.start_stream()
        data=stream.read(2048)
        stream.stop_stream()
        amplitude = (audioop.maxpp(data,2)/65536)*1.41
        Note(frequency).stop()
        w.create_rectangle(int(((frequency-frequency_range[0])/float(frequency_range[1]-frequency_range[0]))*500.0), 50, int(((frequency-frequency_range[0])/float(frequency_range[1]-frequency_range[0]))*500.0)+1, 50-((amplitude/1.41)*50), fill="blue")
        w.update()
        top.title("PyLuminescence Auto-Tune Coarse")
        #w.delete("all")
        display_percentage.configure(text=str(int(((frequency-frequency_range[0])/float(frequency_range[1]-frequency_range[0]))*100.0))+"% Coarse")
        if(amplitude > temp_best_amplitude):
            temp_best_amplitude=amplitude
            temp_best_frequency=frequency
            display_amplitude.configure(text=("Best Amplitude: %.2f" % amplitude))
            display_frequency.configure(text=("Best Frequency: "+ str(frequency)))
    set_frequency = temp_best_frequency
    for frequency in range(set_frequency-50,set_frequency+50,1):
        Note(frequency,volume).play(-1)
        sleep(0.1)
        stream.start_stream()
        data=stream.read(2048)
        stream.stop_stream()
        amplitude = (audioop.maxpp(data,2)/65536)*1.41        
        Note(frequency).stop()
        w.create_rectangle(int(((frequency-frequency_range[0])/float(frequency_range[1]-frequency_range[0]))*500.0), 50, int(((frequency-frequency_range[0])/float(frequency_range[1]-frequency_range[0]))*500.0)+1, 50-((amplitude/1.41)*50), fill="red")
        w.update()
        top.title("PyLuminescence Auto-Tune Fine")
        display_percentage.configure(text=str(((frequency-(set_frequency-50))))+"% Fine")
        if(amplitude > temp_best_amplitude):
            temp_best_amplitude=amplitude
            temp_best_frequency=frequency
            display_amplitude.configure(text=("Best Amplitude: %.2f" % amplitude))
            display_frequency.configure(text=("Best Frequency: "+ str(frequency)))
    set_frequency = temp_best_frequency
    display_percentage.destroy()

def ButtonBack(what):
    global button
    print(what)
    button=what

def Key(event):
    global key
    print(event.keysym)
    key=str(event.keysym)
    print(key)
def Ignite():
    global button
    global key
    global set_frequency
    global initial_volume
    global set_volume
    if(set_frequency == 0):
        tkMessageBox.showwarning("Tune First","You must run the tuning setup first.")
    else:
        e = Tkinter.Button(top, text ="Cancel", command=lambda *args:  ButtonBack('exit'))
        e.grid(row=1, column=4)
        b = Tkinter.Button(top, text ="Fine-tune", command=lambda *args:  ButtonBack('R'))
        b.grid(row=2, column=4)
        set_volume=initial_volume
        Note(set_frequency,set_volume).play(-1)
        tkMessageBox.showinfo("Inject bubble","Inject a bubble now.")
        mode = False
        desired_amplitude = 0
        display_status = Label(top, text="")
        display_status.grid(row=0,column=1)
        display_status.configure(text="Status: Manual")    
        while(button != 'exit'):
            Note(set_frequency).stop()
            Note(set_frequency,set_volume).play(-1)
            stream.start_stream()
            data=stream.read(2048)
            stream.stop_stream()
            amplitude = (audioop.maxpp(data,2)/65536)*1.41
            display_volume.configure(text="Volume: " + str(set_volume))
            display_amplitude.configure(text=("Amplitude: %.2f" % amplitude))
            display_frequency.configure(text="Frequency: " + str(set_frequency))
            top.update()
            top.update_idletasks()

            if(amplitude < desired_amplitude and mode):
                max_amplitude_temp = 0
                display_status.configure(text="Status: Scanning")
                for i in range(set_frequency-5,set_frequency+15):
                    Note(i).stop()
                    Note(i,set_volume).play(-1)
                    stream.start_stream()
                    data=stream.read(2048)
                    stream.stop_stream()
                    amplitude = (audioop.maxpp(data,2)/65536)*1.41
                    if(amplitude > max_amplitude_temp):
                        max_amplitude_temp = amplitude
                        set_frequency = i
                    display_frequency.configure(text="Frequency: " + str(i))
                if(amplitude < desired_amplitude):
                    set_volume+=0.02
            elif(mode) :
                display_status.configure(text="Status: Ampl. Lock")    
            if(key == 'Up'):
                key = ''
                set_volume=set_volume+0.005
            if(key == 'Down'):
                key = ''
                set_volume=set_volume-0.005
            if(key == 'Left'):
                key = ''
                set_frequency=set_frequency-1
            if(key == 'Right'):
                key = ''
                set_frequency=set_frequency+1
            if(key == 'space'):
                mode = not mode
                desired_amplitude = amplitude
                if(mode):
                    display_status.configure(text="Status: Ampl. Lock")    
                # key = ''
                # for frequency in range(set_frequency-20,set_frequency+20,1):
                #     Note(set_frequency).stop()
                #     Note(frequency,set_volume).play(-1)
                #     sleep(0.1)
                #     stream.start_stream()
                #     data=stream.read(2048)  
                #     stream.stop_stream()
                #     amplitude = (audioop.maxpp(data,2)/65536)*1.41        
                #     w.create_rectangle(int(((frequency-frequency_range[0])/float(frequency_range[1]-frequency_range[0]))*500.0), 50, int(((frequency-frequency_range[0])/float(frequency_range[1]-frequency_range[0]))*500.0)+1, 50-((amplitude/1.41)*50), fill="red")
                #     w.update()
                #     top.title("PyLuminescence Auto-Tun e Fine")
                #     display_percentage.configure(text=str(((frequency-(set_frequency-50))))+"% Fine")
                #     if(amplitude > temp_best_amplitude):
                #         temp_best_amplitude=amplitude
                #         temp_best_frequency=frequency
                #         display_amplitude.configure(text=("Best Amplitude: %.2f" % amplitude))
                #         display_frequency.configure(text=("Best Frequency: "+ str(frequency)))
                # set_frequency = temp_best_frequency
        b.destroy()
        e.destroy()

top.bind('<Left>', Key)
top.bind('<R>', Key)
top.bind('<Right>', Key)
top.bind('<Up>', Key)
top.bind('<Down>', Key)
top.bind('<space>', Key)

Tuner = Tkinter.Button(top, text ="Tune", command = Tune).grid(row=0, sticky=W)
Igniter = Tkinter.Button(top, text ="Ignite", command = Ignite).grid(row=0,column=1, sticky=W)

display_amplitude = Label(top, text="")
display_amplitude.grid(row=0,column=2)
display_amplitude.configure(text="Amplitude: 0")

display_volume = Label(top, text="") 
display_volume.grid(row=0,column=3)
display_volume.configure(text="Volume: 0")

display_frequency = Label(top, text="")
display_frequency.grid(row=0,column=4)
display_frequency.configure(text="Frequency: 0")

w = Canvas(top, width=500, height=50)
w.grid(row=4, column=1,sticky=W)

top.mainloop()
