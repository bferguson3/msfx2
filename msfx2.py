##########################################
# MSFX2 - waveform to asm editor for MSX/2
#
# (c) 2019 Ben Ferguson
#  Credits to github user 153armstrong
# for the base waveform generation
##########################################

import numpy as np 
import math 
from scipy import signal as sg 
import tkinter as tk 
import wave
import time
import random
import pyaudio  # sudo apt-get install python3-pyaudio
from threading import Thread
from tkinter import messagebox
import lfsr 
import sys 

class icon_datas(object):
    def __init__(self):
    ## button bitmaps
        self.decline_off_data = """
        #define im_width 16
        #define im_height 16
        static char im_bits[] = {
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x00, 0x06, 0x00, 0x0c, 0x00, 0x18, 0x00, 0xf0, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        };
        """
        self.incline_off_data = """
        #define im_width 16
        #define im_height 16
        static char im_bits[] = {
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0x00, 0xe0, 0x00, 0xb0, 0x00, 0x98, 0x00, 0x8c, 0x00, 0x86, 0x00, 0x83, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        };
        """
        self.inv_sawtooth_data = """
        #define im_width 16
        #define im_height 16
        static char im_bits[] = {
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x63, 0x0c, 0xe6, 0x1c, 0xac, 0x35, 0x38, 0x67, 0x30, 0xc6, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        };
        """
        self.inv_triangle_data = """
        #define im_width 16
        #define im_height 16
        static char im_bits[] = {
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x80, 0x06, 0x60, 0x18, 0x18, 0x60, 0x06, 0x80, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        };
        """
        self.sawtooth_data = """
        #define im_width 16
        #define im_height 16
        static char im_bits[] = {
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x30, 0xc6, 0x38, 0x67, 0xac, 0x35, 0xe6, 0x1c, 0x63, 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        };
        """
        self.incline_on_data = """
        #define im_width 16
        #define im_height 16
        static char im_bits[] = {
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf0, 0xff, 0x18, 0x00, 0x0c, 0x00, 0x06, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        };
        """
        self.triangle_data = """
        #define im_width 16
        #define im_height 16
        static char im_bits[] = {
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x01, 0x60, 0x06, 0x18, 0x18, 0x06, 0x60, 0x01, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        };
        """
        self.decline_on_data = """
        #define im_width 16
        #define im_height 16
        static char im_bits[] = {
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x83, 0xff, 0x86, 0x00, 0x8c, 0x00, 0x98, 0x00, 0xb0, 0x00, 0xe0, 0x00, 0xc0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        };
        """
envelope_types = {
    #('decline', '0b0000', max(0,-x)),
    #('incline_off', '0b0100', min(1,x)), #then set to 0 after 1 loop
    'inv_sawtooth': '0b1000',#, sg.sawtooth(2 * np.pi * freq * x / sampling_rate, 0)),
    'decline': '0b1001',#, max(0,-x)),
    'inv_triangle': '0b1010',#, sg.sawtooth(1 * np.pi * freq * x / sampling_rate, 0.5)), #offset by half a second?
    'decline_on': '0b1011',#, max(0,-x)), #then set to 1
    'sawtooth': '0b1100',#, sg.sawtooth(2 * np.pi * freq * x / sampling_rate, 1)),
    'incline': '0b1101',#, min(1,x)),
    'triangle': '0b1110',# sg.sawtooth(1 * np.pi * freq * x / sampling_rate, 0.5)),
    'incline_off': '0b1111'#, min(1,x)), #then set to 0
}

tone_frequencies = {
    'C  (0)': 16,
    'C# (0)': 17,
    'D  (0)': 18,
    'D# (0)': 19,
    'E  (0)': 21,
    'F  (0)': 22,
    'F# (0)': 23,
    'G  (0)': 25,
    'G# (0)': 26,
    # above are unused, too low.
    'A  (0)': 28,
    'A# (0)': 29,
    'B  (0)': 31,
    
    'C  (1)': 33,
    'C# (1)': 35,
    'D  (1)': 37,
    'D# (1)': 39,
    'E  (1)': 41,
    'F  (1)': 44,
    'F# (1)': 46,
    'G  (1)': 49,
    'G# (1)': 52,
    'A  (1)': 55,
    'A# (1)': 58,
    'B  (1)': 62,

    'C  (2)': 65,
    'C# (2)': 69,
    'D  (2)': 73,
    'D# (2)': 78,
    'E  (2)': 82,
    'F  (2)': 87,
    'F# (2)': 93,
    'G  (2)': 98,
    'G# (2)': 104,
    'A  (2)': 110,
    'A# (2)': 117,
    'B  (2)': 123,

    'C  (3)': 131,
    'C# (3)': 139,
    'D  (3)': 147,
    'D# (3)': 156,
    'E  (3)': 165,
    'F  (3)': 175,
    'F# (3)': 185,
    'G  (3)': 196,
    'G# (3)': 208,
    'A  (3)': 220,
    'A# (3)': 233,
    'B  (3)': 247,

    'C  (4)': 262,
    'C# (4)': 277,
    'D  (4)': 294,
    'D# (4)': 311,
    'E  (4)': 330,
    'F  (4)': 349,
    'F# (4)': 370,
    'G  (4)': 392,
    'G# (4)': 415,
    'A  (4)': 440,
    'A# (4)': 466,
    'B  (4)': 494,
    
    'C  (5)': 523,
    'C# (5)': 554,
    'D  (5)': 587,
    'D# (5)': 622,
    'E  (5)': 659,
    'F  (5)': 698,
    'F# (5)': 740,
    'G  (5)': 784,
    'G# (5)': 831,
    'A  (5)': 880,
    'A# (5)': 932,
    'B  (5)': 988,

    'C  (6)': 1047,
    'C# (6)': 1109,
    'D  (6)': 1175,
    'D# (6)': 1245,
    'E  (6)': 1319,
    'F  (6)': 1397,
    'F# (6)': 1480,
    'G  (6)': 1568,
    'G# (6)': 1661,
    'A  (6)': 1760,
    'A# (6)': 1865,
    'B  (6)': 1976,

    'C  (7)': 2093,
    'C# (7)': 2217,
    'D  (7)': 2349,
    'D# (7)': 2489,
    'E  (7)': 2637,
    'F  (7)': 2794,
    'F# (7)': 2960,
    'G  (7)': 3136,
    'G# (7)': 3322,
    'A  (7)': 3520,
    'A# (7)': 3729,
    'B  (7)': 3951,

    'C  (8)': 4186,
    'C# (8)': 4435,
    'D  (8)': 4699,
    'D# (8)': 4978,
    'E  (8)': 5274,
    'F  (8)': 5587,
    'F# (8)': 5920,
    'G  (8)': 6272,
    'G# (8)': 6645,
    'A  (8)': 7040,
    'A# (8)': 7459,
    'B  (8)': 7902
}

'''specific waveform type to msx'''
class msxwaveform(object):
    def __init__(self, samplerate=22000, hex_freq=254, noise_fr = 0, length=3, wf='tone', envelope = False, envelopetype=envelope_types['decline'], env_period = 6992):
        self.samplerate = samplerate 
        self.hex_freq = hex_freq #254 ~= 440 A(4)
        self.length = (3580000/2)/(env_period*256)*3
        self.envelope = envelope
        self.envelopetype = envelopetype
        self.env_period = env_period    # 6992 or 1b50h is ~1s
        self.env_bin = ''
        self.wf = wf # 'noise', 'mixed'
        self.noise_fr = noise_fr
        self.noise = -1

        if env_period >= (256*256):
            self.env_period = 65535
        if hex_freq > 4095:
            self.hex_freq = 4095
        
        self.freq = (3580000/2) / (16*self.hex_freq)

        self.samples = self.length * self.samplerate

        self.volume = 60   # max value of simulated envelope

        self.env_freq = (3580000/2) / (256*self.env_period) 

        self.x = np.arange(self.samples)

        if self.wf == 'noise':
            self.noise_freq = (3580000) / (16*self.noise_fr)
            i = 0
            j = math.ceil((self.samples / self.noise_freq)/2)
            a = []
            r = random.randrange(0,32)/32
            while i < self.samples:
                a.append(r)
                if i % j == 0:
                    r = (random.randrange(0,32)/32) * 0.75
                i += 1
            self.y = np.asarray(a)
        elif self.wf == 'tone':
            self.y = sg.square(2*np.pi*self.freq*self.x/self.samplerate) # actual wave generation
        else:
            self.noise_freq = (3580000) / (16*self.noise_fr)
            i = 0
            j = math.ceil((self.samples / self.noise_freq)/2)
            a = []
            r = random.randrange(0,32)/32
            while i < self.samples:
                a.append(r)
                if i % j == 0:
                    r = random.randrange(0,32)/32
                i += 1
            self.noise = np.asarray(a)
            self.noise = self.noise * (self.volume) * 0.75
            #print(self.noise)
            self.y = sg.square(2*np.pi*self.freq*self.x/self.samplerate) # actual wave generation
            self.volume = self.volume * 2

        self.y = self.volume * self.y 

        if self.envelope == True:
            apply_envelope(self)
####


'''converts any integer up to 4 bytes long to byte form of either endian type'''
def ToByteArr(num, len, endian=1):
    # num is number to convert
    # len is how many bytes to return in the array
    # endian = 1 big endian, =0 little endian
    b1 = 0
    b2 = 0
    b3 = 0
    b4 = 0
    ret_arr = []

    if num < 256:
        b1 = num 
        b2 = 0
        b3 = 0
        b4 = 0
    elif num > 255 and num < 65536:
        b2 = math.floor(num/256)
        b1 = num - (b2*256)
        b3 = 0
        b4 = 0
    elif num > 65535 and num < 16777216:
        b3 = math.floor( (num/256) / 256)
        b2 = math.floor( (num - (b3*256*256))/256)
        b1 = num - (b3*256*256) - (b2*256)
        b4 = 0
    else: # up to 4.2 billion
        b4 = math.floor( ((num/256)/256)/256 ) # 1
        b3 = math.floor( ((num - ( b4*256*256*256 )) / 256) / 256) # 49
        b2 = math.floor( ((num - (b4*256*256*256) - (b3*256*256)) / 256 ))
        b1 = num - (b4*256*256*256) - (b3*256*256) - (b2*256)

    if endian == 0:
        ret_arr.append(b1)
        ret_arr.append(b2)
        ret_arr.append(b3)
        ret_arr.append(b4)
    else:
        ret_arr.append(b4)
        ret_arr.append(b3)
        ret_arr.append(b2)
        ret_arr.append(b1)

    return ret_arr
####

'''writes header to passed msxwaveform and file'''
def writeheader(wavetest, file, segment):
    global app 
    s = 0
    i = 0
    channels = 1
    while i < 3:
        if app.enabled[i].get() == True:
            s += 1
            if app.noise[i].get() == 2:
                channels = 2
        i += 1

    file.write(bytes([0x52, 0x49, 0x46, 0x46])) # RIFF)
    t = 0
    if segment == 'a':
        t = math.floor(wavetest.samples/3)
    else:
        t = math.floor(wavetest.samples/3)*2
    file.write(bytes(ToByteArr(36+(t*s*channels), 4, endian=0)))# 36 + data size (lend) 22050 or $68 $ac for 44100
    file.write(bytes([0x57, 0x41, 0x56, 0x45])) # WAVE)

    file.write(bytes([0x66, 0x6d, 0x74, 0x20])) # 'fmt '
    file.write(bytes([0x10, 0x00, 0x00, 0x00])) # pcm (lend)
    file.write(bytes([0x01, 0x00])) # pcm (lend)
    if channels == 2:
        c = 0x02 
    else:
        c = 0x01
    file.write(bytes([c, 0x00])) # mono (lend)
    file.write(bytes(ToByteArr(wavetest.samplerate*s, 4, endian=0)))## 22050 (lend) = $22 56, or $44 ac for 44100
    file.write(bytes(ToByteArr(wavetest.samplerate*2*channels, 4, endian=0))) # byterate (lend) <- bitrate / 8 = 22050. if 8bit simply size of samples again.de
    file.write(bytes([c, 0x00])) # block align - bytes for 1 sample (lend)
    file.write(bytes([0x08, 0x00])) # bits per sample (8)

    file.write(bytes([0x64, 0x61, 0x74, 0x61])) # 'data'
    file.write(bytes(ToByteArr(t*s*channels, 4, endian=0))) # data block size (22050b)
#

def apply_envelope(msxwav):
    env_len = msxwav.env_freq # 6992
    #print(env_len)
    x = np.arange(32*msxwav.length) #length = env period * 3

    global envelope_types
    # denominator is num of samples, therefore resolution of envelope
    if msxwav.envelopetype == envelope_types['inv_sawtooth']:
        y = (sg.sawtooth(2 * np.pi * (1/env_len) * x / (32), 0)+1)/2
        
    elif msxwav.envelopetype == envelope_types['decline']:
        y = (sg.sawtooth(2 * np.pi * (1/env_len) * x / (32), 0)+1)/2
        if len(y) > 32*(msxwav.length/3):
            i = math.floor(32*(msxwav.length/3))
            while i < len(y):
                y[i] = 0
                i += 1
        
    elif msxwav.envelopetype == envelope_types['inv_triangle']:
        y = (sg.sawtooth( ((1 * np.pi * (1/env_len) * x) / 32) + np.pi, 0.5) + 1)/2 #offset by half a second?

    elif msxwav.envelopetype == envelope_types['decline_on']:
        y = (sg.sawtooth(2 * np.pi * (1/env_len) * x / 32, 0) + 1)/2
        if len(y) > 32*(msxwav.length/3):
            i = math.floor(32*(msxwav.length/3))
            while i < len(y):
                y[i] = 1
                i += 1

    elif msxwav.envelopetype == envelope_types['sawtooth']:
        y = (sg.sawtooth(2 * np.pi * (1/env_len) * x / 32, 1) + 1)/2

    elif msxwav.envelopetype == envelope_types['incline']:
        y = (sg.sawtooth(2 * np.pi * (1/env_len) * x / 32, 1) + 1)/2
        if len(y) > 32*(msxwav.length/3):
            i = math.floor(32*(msxwav.length/3))
            while i < len(y):
                y[i] = 1
                i += 1

    elif msxwav.envelopetype == envelope_types['triangle']:
        y = (sg.sawtooth( ((1 * np.pi * (1/env_len) * x) / 32), 0.5) + 1)/2

    elif msxwav.envelopetype == envelope_types['incline_off']:
        y = (sg.sawtooth(2 * np.pi * (1/env_len) * x / 32, 1) + 1)/2
        if len(y) > 32*(msxwav.length/3):
            i = math.floor(32*(msxwav.length/3))
            while i < len(y):
                y[i] = 0
                i += 1
    # end envelope pattern definitions
    
    # TODO: fix this manual amplitude adjustment for proper hardware levels.
    i = 0
    while i < len(y):
        #if msxwav.wf != 'noise':
        #    y[i] -= 0.1
        #else:
        y[i] -= 0.25
        if y[i] < 0:
            y[i] = 0
        i += 1

    i = 0
    j = 0
    perstep = math.ceil(msxwav.samplerate / (32))
    for c in msxwav.y:
        c = c * y[j]
        if msxwav.wf == 'mixed':
            #print(msxwav.noise[i])
            n = msxwav.noise[i] * y[j]
        msxwav.y[i] = int(c)
        if msxwav.wf == 'mixed':
            msxwav.noise[i] = int(n)
        i += 1
        if i % perstep == 0:
            j += 1
            if j >= len(y):
                j = 0
            

class asm_window(tk.Tk):
    def __init__(self, wf):
        super().__init__()

        self.title('z80 listing')

        self.parent = wf

        self.dos = tk.BooleanVar()
        self.init = tk.BooleanVar()
        self.vol = tk.BooleanVar()
        self.defs = tk.BooleanVar()

        self.bframe = tk.Frame(self)
        self.bframe.pack(side=tk.TOP)
        self.cb_lbls = tk.Checkbutton(self.bframe, text='Add defs', command=lambda:self.cb(self.defs))
        self.cb_lbls.pack(side=tk.LEFT)
        self.cb_dos = tk.Checkbutton(self.bframe, text='Interslot', command=lambda:self.cb(self.dos))
        self.cb_dos.pack(side=tk.LEFT) # interslot call?
        self.cb_init = tk.Checkbutton(self.bframe, text='PSG Init', command=lambda:self.cb(self.init))
        self.cb_init.pack(side=tk.LEFT) # include psg init?
        self.cb_vol = tk.Checkbutton(self.bframe, text='Volume', command=lambda:self.cb(self.vol))
        self.cb_vol.pack(side=tk.LEFT)# this is only enabled if envelope is false
        
        
        self.textbox = tk.Text(self, width=80, height=40)
        self.textbox.pack(side=tk.BOTTOM)

        self.protocol("WM_DELETE_WINDOW", self._iconme)
        
        self.refresh(self.parent)

    def _iconme(self):
        self.withdraw()

    def cb(self, var):
        global app
        if var.get() == False:
            var.set(True)
        else:
            var.set(False)
        self.refresh(app)

    def refresh(self, wf):
        self.textbox.delete(1.0, tk.END)

        self.textbox.insert(tk.END, ' ; Made with MSFX2!\n')
        self.textbox.insert(tk.END, ' ;  (Remember to reset channels after the desired\n ;   number of frames have passed.)\n\n')
        
        if self.defs.get():
            self.add_asm_text(self.dos.get(), -2, None, self.defs.get())
        
        # INIT - optional
        if self.init.get():
            self.textbox.insert(tk.END, ' ; Init PSG\n')
            self.add_asm_text(self.dos.get(), -1, None, self.defs.get()) # r#, value
            self.textbox.insert(tk.END, '\n')
        
        # TONE/NOISE IO (r7)
        b = '0b10000000'
        c = '0b00000000'
        if wf.enabled[0].get():
            e = wf.noise[0].get()
            if e == 0: #tone A
                c = '0b00000001'
            elif e == 1: # noise A
                c = '0b00001000'
            elif e == 2:
                c = '0b00001001'
        o = int(b,2) | int(c,2)
        if wf.enabled[1].get():
            e = wf.noise[1].get()
            if e == 0: # tone B
                c = '0b00000010'
            elif e == 1:
                c = '0b00010000'
            elif e == 2:
                c = '0b00010010'
        o = o | int(c,2)
        if wf.enabled[2].get():
            e = wf.noise[2].get()
            if e == 0:
                c = '0b00000100'
            elif e == 1:
                c = '0b00100000'
            elif e == 2:
                c = '0b00100100'
        o = o | int(c,2)
        #print(format(o,'08b'))
        self.textbox.insert(tk.END, ' ; Tone/Noise IO\n')
        self.add_asm_text(self.dos.get(), 7, o, self.defs.get())
        self.textbox.insert(tk.END, '\n')
        # VOL / ENVELOPE - optional if envelope = False (r8, r9, ra)
        if (wf.envyesno == False and self.vol.get()) or wf.envyesno == True:
            # 8 = A, 9 = B, A = C. 
            # if no envelope, 0000+4bit vol level
            # if yes envelope, 0001+xxxx
            print('todo')

        # TONE FREQ (r0-5) (if wf 0 or 2)
        i = 0
        while i < 3:
            if wf.enabled[i].get():
                if wf.noise[i].get() == 0 or wf.noise[i].get() == 2:
                    self.textbox.insert(tk.END, ' ; Channel ' + str(i+1) + ' tone\n')
                    self.add_asm_text(self.dos.get(), (i*2), wf.wave_freq_scroll[i].get(), self.defs.get())
                    self.textbox.insert(tk.END, '\n')
            i += 1
        # NOISE FREQ (r6) (if wf 1 or 2)
        i = 0
        nz = False
        while i < 3:
            if wf.noise[i].get() == 1 or wf.noise[i].get() == 2:
                nz = True
            i += 1
        if nz:
            self.textbox.insert(tk.END, ' ; Noise frequency\n')
            self.add_asm_text(self.dos.get(), 6, wf.wave_freq_scroll[3].get(), self.defs.get())
            self.textbox.insert(tk.END, '\n')
        # ENVELOPE FREQ (if env=true) (rb, rc)
        if wf.envyesno == True:
            print('env freq')
        # ENVELOPE SHAPE (if env=true) (rd)
        if wf.envyesno == True:
            print('env shape')
        
        self.textbox.insert(tk.END,'')
        return
    
    def add_asm_text(self, dos, reg, val, defs):
        if type(reg) == str:
            reg = int(reg,16)
        GICINI = '$0090'
        EXPTBL = '$fcc1'
        CALSLT = '$1c'
        WRTPSG = '$0093'#:     equ $0093
        out = ''
        if defs:
            GICINI = 'GICINI'
            EXPTBL = 'EXPTBL'
            CALSLT = 'CALSLT'
            WRTPSG = 'WRTPSG'
        if reg == -2:
            if self.init.get():
                out = out + 'GICINI: equ $0090\n'
            if dos:
                out = out + 'EXPTBL: equ $fcc1\n'
                out = out + 'CALSLT: equ $1c\n'
            out = out + 'WRTPSG: equ $0093\n'
            out = out + '\n'

        # if more than one byte...
        if reg == 0 or reg == 2 or reg == 4:
            v2 = str(math.floor(val/256))
            v1 = str(val % 256)
        elif reg == 7:
            v1 = '%' + format(val, '08b')
        else:
            v1 = str(val)

        if dos == False:
            if reg > -1:
                out = out + '   ld a, ' + str(reg) + '\n'
                out = out + '   ld e, ' + v1 + '\n'
                out = out + '   call ' + WRTPSG + '\n'
                if reg == 0 or reg == 2 or reg == 4:
                    out = out + '   ld a, ' + str(reg+1) + '\n'
                    out = out + '   ld e, ' + v2 + '\n'
                    out = out + '   call ' + WRTPSG + '\n'
            elif reg == -1:
                out = out + '   call ' + GICINI + '\n'
        else:
            if reg == -1:
                out = out + '   ld ix, ' +GICINI + '\n'
                out = out + '   ld iy, [' + EXPTBL + '-1]\n'
                out = out + '   call ' + CALSLT + '\n'
            if reg > -1:
                out = out + '   ld a, ' + str(reg) + '\n'
                out = out + '   ld e, ' + v1 + '\n'
                out = out + '   ld ix, ' + WRTPSG + '\n'
                out = out + '   ld iy, [' + EXPTBL + '-1]\n'
                out = out + '   call ' + CALSLT + '\n'
                if reg == 0 or reg == 2 or reg == 4:
                    out = out + '   ld a, ' + str(reg+1) + '\n'
                    out = out + '   ld e, ' + v2 + '\n'
                    out = out + '   ld ix, ' + WRTPSG + '\n'
                    out = out + '   ld iy, [' + EXPTBL + '-1]\n'
                    out = out + '   call ' + CALSLT + '\n'
        self.textbox.insert(tk.END, out)
        return

numeric = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']

'''actual app class'''
class msfx_window(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('MSFX2')

        self.wf = None
        self.t = None
        self.loop = True
        self.envelope = envelope_types['decline']
        self.modified = False 
        self.tw = None
        self.envyesno = True

        self.wave_vals = []
        self.freq_vals_hex = []
        self.wave_freq_entries = []
        self.wave_freq_scroll = []
        self.enabled = []
        self.noise = []
        self.tones_txt = []

        i = 0
        while i < 3:
            if i == 0:
                ltr = 'A'
            elif i == 1:
                ltr = 'B'
            else:
                ltr = 'C'
            l = tk.Label(self, text='Channel {} freq:'.format(ltr))
            l.grid(row=i*3, columnspan=3)
            self.freq_vals_hex.append(tk.Label(self, text='Value: $0000'))
            self.freq_vals_hex[i].grid(row=(i*3)+1, column=4, columnspan=3)
            
            self.tones_txt.append(tk.Label(self, text='Tone: <>'))
            self.tones_txt[i].grid(row=(i*3)+1, column=0, columnspan=3)
            
            self.wave_vals.append(tk.StringVar())
            #wv = self.wave_vals[i]
            #wv.trace('w', lambda name, index, mode, wv=wv: self.changefreq)

            self.wave_freq_entries.append(tk.Entry(self, width=4, textvariable=self.wave_vals[i]))
            self.wave_freq_entries[i].grid(row=i*3, column=4)
            
            self.wave_freq_scroll.append(tk.Scale(self, orient=tk.HORIZONTAL, to=4095, resolution=1)) #command=lambda a:self.changefreq(self.wave_freq_scroll[i].get(), self.wave_freq_scroll[i])))
            self.wave_freq_scroll[i].grid(row=(i*3)+2, column=1, columnspan=5, sticky='EW')
            
            tk.Label(self, text='On/Off').grid(row=i*3, column=6, columnspan=2, sticky='e')
            tk.Label(self, text='Music/Noise/Mix?').grid(row=i*3, column=8, columnspan=3)
            
            self.enabled.append(tk.BooleanVar())
            tk.Checkbutton(self, variable=self.enabled[i], command=self.enabled_cb).grid(row=(i*3)+2, column=7)
            
            self.noise.append(tk.IntVar())
            tk.Radiobutton(self, variable=self.noise[i], value = 0, command=self.enabled_cb).grid(row=(i*3)+2, column=8)
            tk.Radiobutton(self, variable=self.noise[i], value=1, command=self.enabled_cb).grid(row=(i*3)+2, column=9)
            tk.Radiobutton(self, variable=self.noise[i], value=2, command=self.enabled_cb).grid(row=(i*3)+2, column=10)

            i += 1
        
        self.wave_freq_scroll[0].configure(command=lambda a: self.changefreq(self.wave_freq_scroll[0].get(), 0))
        self.wave_freq_scroll[1].configure(command=lambda a: self.changefreq(self.wave_freq_scroll[1].get(), 1))
        self.wave_freq_scroll[2].configure(command=lambda a: self.changefreq(self.wave_freq_scroll[2].get(), 2))
        
        w = self.wave_vals[0]
        self.wave_vals[0].trace("w", lambda name, index, mode, w=w: self.changefreq(w.get(), 0, True))
        w = self.wave_vals[1]
        self.wave_vals[1].trace("w", lambda name, index, mode, w=w: self.changefreq(w.get(), 1, True))
        w = self.wave_vals[2]
        self.wave_vals[2].trace("w", lambda name, index, mode, w=w: self.changefreq(w.get(), 2, True))
        
        tk.Button(self, text='<', command=lambda:self.freq_inc(0, -1)).grid(row=2, column=0, sticky='e')
        tk.Button(self, text='>', command=lambda:self.freq_inc(0, 1)).grid(row=2, column=6, sticky='w')
        tk.Button(self, text='<', command=lambda:self.freq_inc(1, -1)).grid(row=5, column=0, sticky='e')
        tk.Button(self, text='>', command=lambda:self.freq_inc(1, 1)).grid(row=5, column=6, sticky='w')
        tk.Button(self, text='<', command=lambda:self.freq_inc(2, -1)).grid(row=8, column=0, sticky='e')
        tk.Button(self, text='>', command=lambda:self.freq_inc(2, 1)).grid(row=8, column=6, sticky='w')

        tk.Label(self, text='Noise freq:').grid(row=12,column=0)
        self.wave_freq_scroll.append(tk.Scale(self, orient=tk.HORIZONTAL, to=31, resolution=1)) #command=lambda a:self.changefreq(self.wave_freq_scroll[i].get(), self.wave_freq_scroll[i])))
        self.wave_freq_scroll[3].grid(row=12, column=1, columnspan=8, sticky='EW')
        self.wave_freq_scroll[3].configure(command=lambda a: self.changefreq(self.wave_freq_scroll[3].get(), 3))
        self.noiselbl = tk.Label(self, text='0 Hz')
        self.noiselbl.grid(row=12,column=9, columnspan=2)

        tk.Label(self, text='Env. Freq:').grid(row=14)
        self.env_freq = tk.Scale(self, orient=tk.HORIZONTAL, to=65535, resolution=1, command=self.change_env_freq)
        self.env_freq.set(6992)
        self.env_freq.grid(row=14,column=1,columnspan=8, sticky='ew')
        self.env_freq_var = tk.StringVar()
        ev = self.env_freq_var
        self.env_freq_txt = tk.Entry(self, width=4, textvariable=self.env_freq_var)
        ev.trace('w', lambda name, index, mode, ev=ev: self.change_env_time())
        self.env_freq_txt.insert(0,'1.00')
        tk.Label(self,text='sec').grid(row=14,column=10)
        self.env_freq_txt.grid(row=14,column=9)
        
        self.exp_asm = tk.Button(self,text='Export ASM', command=self.export_asm)
        self.exp_asm.grid(row=18,column=1,columnspan=3)

        self.gen_wv = tk.Button(self, text='Generate wave', command=self.makefile)
        #self.mft = False
        #self.gen_wv = tk.Label(self, text='')
        self.gen_wv.grid(row=18, column=4, columnspan=6)
        self.playbutton = tk.Button(self, text='Play', command=self.playthread)
        self.playbutton.grid(row=18, column=8, columnspan=2)

        self.stopbutton = tk.Button(self, text='Stop', command=self.stopplay)
        self.stopbutton.grid(row=18,column=10,columnspan=2)

        self.audio = pyaudio.PyAudio()
        self.stream = None

        self.protocol("WM_DELETE_WINDOW", self.quit)
    
    def quit(self):
        print('quitting')
        sys.exit()

    def change_env_time(self):
        c = self.env_freq_var.get()
        global numeric 
        ok = False
        i = 0
        while i < len(c):
            ok = False
            for n in numeric:
                if c[i] == n:
                    ok = True
            if ok == False:
                break 
            i += 1
        if not ok or len(c) > 4:
            c = c[:-1]
            self.env_freq_txt.delete(0,tk.END)
            self.env_freq_txt.insert(0,c)

        if self.env_freq_var.get() == '':
            return
        try:
            if float(self.env_freq_var.get()) == 0:
                return
        except:
            return

        pd = float(self.env_freq_var.get())
        v = math.floor((3580000/2)/pd/256)
        if v < 1:
            v = 1
        if v > 65535:
            v = 65535
        
        self.env_freq.set(v)

    def change_env_freq(self, o):
        if int(o) == 0:
            self.env_freq.set(1)
            o = '1'
        pd = round((3580000/2)/(256*int(o)),2)
        #print(pd)
        self.env_freq_txt.delete(0,tk.END)
        self.env_freq_txt.insert(0,pd)


    def export_asm(self):
        if self.tw == None:
            self.tw = asm_window(self)
        else:
            self.tw.deiconify()
            self.tw.refresh(self)
            self.tw.lift()
        return

    def enabled_cb(self):
        self.set_modified(True)
        self.loop = False

    def set_modified(self,tf):
        self.modified = tf
        if tf == True:
            self.gen_wv.config(text='*Generate wave')
    #        self.gen_wv.config(text='Generating...')
    #        self.makefile_thread()
        else:
            self.gen_wv.config(text='Generate wave')
            #self.gen_wv.config(text='')

    def stopplay(self):
        self.loop = False

    def freq_inc(self, wav, delta):
        #self.modified = True
        self.wave_freq_scroll[wav].set(self.wave_freq_scroll[wav].get()+delta)
        self.set_modified(True)


    def changefreq(self, o, num, manual=False):
        if num < 3:
            c = self.wave_freq_entries[num].get()
            try:
                d = int(c[len(c)-1])
            except:
                c = c[:-1]
                self.wave_freq_entries[num].delete(0,tk.END)
                self.wave_freq_entries[num].insert(0,c)
            
        if num == 3:
            if self.wave_freq_scroll[3].get() == 0:
                return
            f = math.floor((3580000/2)/(self.wave_freq_scroll[3].get()*16))
            self.noiselbl.configure(text=str(f)+' Hz')
            self.set_modified(True)
            return

        if manual == False:
            self.wave_freq_entries[num].delete(0,tk.END)
            c = self.wave_freq_scroll[num].get()
            self.wave_freq_entries[num].insert(0,c)

        else:
            c = self.wave_freq_entries[num].get()

            if c == '':
                return
            if type(c) == str:
                if len(c) > 4:
                    c = c[:4]
                c = int(c)
            if c > 4095:
                c = 4095
        #    self.set_modified(True)
            self.wave_freq_entries[num].delete(0,tk.END)
            self.wave_freq_entries[num].insert(0,c)
            self.wave_freq_scroll[num].set(c)

        self.freq_vals_hex[num].config(text='Value: $' + format(self.wave_freq_scroll[num].get(), '04x'))
        
        self.set_modified(True)
        
        if self.wave_freq_scroll[num].get() == 0:
            self.tones_txt[num].config(text='Tone: <>')
            return
        
        global tone_frequencies
        for b in tone_frequencies:
            t = int((3580000/2) / (16*self.wave_freq_scroll[num].get()))
            if tone_frequencies[b] == t:
                self.tones_txt[num].config(text='Tone: {}'.format(b))
                break
            if tone_frequencies[b]*0.99 < t and tone_frequencies[b]*1.01 > t:
                self.tones_txt[num].config(text='Tone: {}'.format(b))
                break
            else:
                self.tones_txt[num].config(text='Tone: <>')

    def change_envelope(self, env, btn):
        global b_do
        global b_io 
        global b_is 
        global b_it 
        global b_s 
        global b_i 
        global b_t 
        global b_d
        global b_off
        b_do.config(relief=tk.RAISED)
        b_io.config(relief=tk.RAISED)
        b_is.config(relief=tk.RAISED)
        b_it.config(relief=tk.RAISED)
        b_s.config(relief=tk.RAISED)
        b_i.config(relief=tk.RAISED)
        b_t.config(relief=tk.RAISED)
        b_d.config(relief=tk.RAISED)
        b_off.config(relief=tk.RAISED)
        if env != None:
            self.envelope = env
            self.envyesno = True
        else:
            self.envyesno = False
        btn.config(relief=tk.SUNKEN)
        self.set_modified(True)
    

    #def makefile_thread(self):
        #self.playbutton.config(state=tk.DISABLED)
        #self.loop = True
    #    if self.mft == False:
    #        t = Thread(target=self.makefile, daemon=True)
    #        t.start()
    #        self.mft = True

    def makefile(self):
        w = []
        s = 0
        i = 0
        stereonoise = False
        noisechan = 0
        while i < len(self.enabled):
            w.append(0)
            if self.enabled[i].get() == True:
                fre = self.wave_freq_entries[i].get()
                if fre == '' or fre == 0:
                    self.freq_inc(i, 1)
                    fre = '1' 
                fre = int(fre)
                nf = self.wave_freq_scroll[3].get()
                if nf == '' or nf == 0:
                    nf = 1
                    self.wave_freq_scroll[3].set(1)
                if self.noise[i].get() == 0:
                    wf = 'tone'
                elif self.noise[i].get() == 1:
                    wf = 'noise'
                elif self.noise[i].get() == 2:
                    wf = 'mixed' 
                    stereonoise = True
                    noisechan = i
                w[i] = msxwaveform(hex_freq = fre, envelope=self.envyesno, envelopetype=self.envelope, env_period=self.env_freq.get(), wf=wf, noise_fr=nf)#, envelopetype=envelope_types['inv_sawtooth'])
                s += 1
            i += 1
        if s == 0:
            print('enable at least one channel!')
            return
        try:
            f = open('a.wav', 'wb')
            l = 0 
            if w[0] != 0:
                writeheader(w[0], f, 'a')
                l = len(w[0].y)
            elif w[1] != 0:
                writeheader(w[1], f, 'a')
                l = len(w[1].y)
            elif w[2] != 0:
                writeheader(w[2], f, 'a')
                l = len(w[2].y)
            i = 0
            while i < math.ceil(l/3)+720:
                if self.enabled[0].get() == True:
                    b = int(w[0].y[i])
                    b += 127          
                    f.write(bytes([b]))
                    if stereonoise:
                        b = int(w[noisechan].noise[i])
                        b += 127
                        f.write(bytes([b]))
                if self.enabled[1].get() == True:
                    c = int(w[1].y[i])
                    c += 127
                    f.write(bytes([c]))
                    if stereonoise:
                        b = int(w[noisechan].noise[i])
                        b += 127
                        f.write(bytes([b]))
                if self.enabled[2].get() == True:
                    d = int(w[2].y[i])
                    d += 127
                    f.write(bytes([d]))
                    if stereonoise:
                        b = int(w[noisechan].noise[i])
                        b += 127
                        f.write(bytes([b]))
                i += 1
            f.write(bytes([0x80]))
            if (f):
                f.close()
            f = open('b.wav','wb')
            if w[0] != 0:
                writeheader(w[0], f, 'b')
            elif w[1] != 0:
                writeheader(w[1], f, 'b')
            elif w[2] != 0:
                writeheader(w[2], f, 'b')
            while i < l-1:
                if self.enabled[0].get() == True:
                    b = int(w[0].y[i])
                    b += 127
                    f.write(bytes([b]))
                    if stereonoise:
                        b = int(w[noisechan].noise[i])
                        b += 127
                        f.write(bytes([b]))
                if self.enabled[1].get() == True:
                    c = int(w[1].y[i])
                    c += 127
                    f.write(bytes([c]))
                    if stereonoise:
                        b = int(w[noisechan].noise[i])
                        b += 127
                        f.write(bytes([b]))
                if self.enabled[2].get() == True:
                    d = int(w[2].y[i])
                    d += 127
                    f.write(bytes([d]))
                    if stereonoise:
                        b = int(w[noisechan].noise[i])
                        b += 127
                        f.write(bytes([b]))
                i += 1
            f.write(bytes([0x80]))
            if(f):
                f.close()
            print('.wav written successfully!')
        #except:
        #    print('something went wrong.')
        except PermissionError:
            print("still open!")

        self.mft = False
        self.set_modified(False)

    def playthread(self):
        self.playbutton.config(state=tk.DISABLED)
        self.loop = True
        self.t = Thread(target=self.playfile, daemon=True)
        self.t.start()

    def playfile(self):
        self.wf = wave.open('a.wav','rb')
        self.stream = self.audio.open(format=self.audio.get_format_from_width(self.wf.getsampwidth()),
                            channels=self.wf.getnchannels(),
                            rate=self.wf.getframerate(),
                            output=True,
                            stream_callback=self.play_cb)
        self.stream.start_stream() 
        while self.stream.is_active():
                time.sleep(0.01)
        self.stream.stop_stream()
        self.stream.close()
        
        self.wf = wave.open('b.wav','rb')
        self.stream = self.audio.open(format=self.audio.get_format_from_width(self.wf.getsampwidth()),
                            channels=self.wf.getnchannels(),
                            rate=self.wf.getframerate(),
                            output=True)
        data = self.wf.readframes(64)
        while len(data) > 0 and self.loop==True:
            self.stream.write(data)
            data = self.wf.readframes(64)
            if data == b'':
                self.wf.rewind()
                data = self.wf.readframes(64)
            
        self.stream.stop_stream()
        self.stream.close()
        
        self.playbutton.config(state=tk.NORMAL)
        

    def play_cb(self, in_data, frame_count, time_info, status):
        #print(in_data, frame_count, time_info)
        data = self.wf.readframes(frame_count)
        return (data, pyaudio.paContinue)
 
            
#### end def for msfx_window

app = msfx_window() 

icons = icon_datas()
inv_sawtooth_icon = tk.BitmapImage(data=icons.inv_sawtooth_data)
decline_off_icon = tk.BitmapImage(data=icons.decline_off_data)
incline_off_icon = tk.BitmapImage(data=icons.incline_off_data)
inv_triangle_icon = tk.BitmapImage(data=icons.inv_triangle_data)
sawtooth_icon = tk.BitmapImage(data=icons.sawtooth_data)
incline_on_icon = tk.BitmapImage(data=icons.incline_on_data)
triangle_icon = tk.BitmapImage(data=icons.triangle_data)
decline_on_icon = tk.BitmapImage(data=icons.decline_on_data)
tk.Label(app, text='Vol envelope:').grid(row=13, column=0)

b_do = tk.Button(app, image=decline_off_icon, width=30, height=20, command=lambda:app.change_envelope(envelope_types['decline'], b_do))
b_do.grid(row=13, column=3)
b_do.config(relief=tk.SUNKEN)
b_io = tk.Button(app, image=incline_off_icon, width=30, height=20, command=lambda:app.change_envelope(envelope_types['incline_off'], b_io))
b_io.grid(row=13, column=4)
b_is = tk.Button(app, image=inv_sawtooth_icon, width=30, height=20, command=lambda:app.change_envelope(envelope_types['inv_sawtooth'], b_is))
b_is.grid(row=13, column=5)
b_it = tk.Button(app, image=inv_triangle_icon, width=30, height=20, command=lambda:app.change_envelope(envelope_types['inv_triangle'], b_it))
b_it.grid(row=13, column=6)
b_s = tk.Button(app, image=sawtooth_icon, width=30, height=20, command=lambda:app.change_envelope(envelope_types['sawtooth'], b_s))
b_s.grid(row=13, column=7, sticky='w')
b_i = tk.Button(app, image=incline_on_icon, width=30, height=20, command=lambda:app.change_envelope(envelope_types['incline'], b_i))
b_i.grid(row=13, column=8, sticky='e')
b_t = tk.Button(app, image=triangle_icon, width=30, height=20, command=lambda:app.change_envelope(envelope_types['triangle'], b_t))
b_t.grid(row=13, column=9, sticky='w')
b_d = tk.Button(app, image=decline_on_icon, width=30, height=20, command=lambda:app.change_envelope(envelope_types['decline_on'], b_d))
b_d.grid(row=13, column=10, sticky='w')
b_off = tk.Button(app, text='OFF', width=3, height=1, command=lambda:app.change_envelope(None, b_off))
b_off.grid(row=13, column=11, sticky='w')


app.mainloop() 