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


'''specific waveform type to msx'''
class msxwaveform(object):
    def __init__(self, samplerate=22050, hex_freq=(0*256)+255, length=1, envelope = False, envelopetype='0b0000', env_period = (0*256)+11):
        self.samplerate = samplerate 
        self.hex_freq = hex_freq
        self.length = length
        self.envelope = envelope
        self.envelopetype = envelopetype
        self.env_period = env_period

        if env_period >= (256*256):
            self.env_period = 65535
        if hex_freq > 4095:
            self.hex_freq = 4095
        
        self.freq = (3580000/2) / (16*self.hex_freq)

        self.samples = self.length * self.samplerate

        self.volume = 255   # max value of simulated envelope

        self.env_freq = (3580000/2) / (256*self.env_period)

        self.x = np.arange(self.samples)

        self.y = sg.square(2*np.pi*self.freq*self.x/self.samplerate) # actual wave generation

        self.y = (self.volume/2) * self.y + (self.volume/2) # adjust amplitude for volume
####

# sine:
#y = envelope_level * np.sin(2 * np.pi * freq * x / sampling_rate)
# square wav: default duty = 0.5
#y = sg.square(2 * np.pi * freq_tp * x / sampling_rate)
# sqaure w duty cycle:
#wf 00xx and 1001
#y = envelope_level * sg.sawtooth(2 * np.pi * freq * x / sampling_rate, 0)
# triangle 1110: ??
#y = envelope_level * sg.sawtooth(2 * np.pi * freq*2 * x / sampling_rate, 0.5)
# adjust for volume/unsigned pcm

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
def writeheader(wavetest, file):
    file.write(bytes([0x52, 0x49, 0x46, 0x46])) # RIFF)
    file.write(bytes(ToByteArr(36+wavetest.samples, 4, endian=0)))# 36 + data size (lend) 22050 or $68 $ac for 44100
    file.write(bytes([0x57, 0x41, 0x56, 0x45])) # WAVE)

    file.write(bytes([0x66, 0x6d, 0x74, 0x20])) # 'fmt '
    file.write(bytes([0x10, 0x00, 0x00, 0x00])) # pcm (lend)
    file.write(bytes([0x01, 0x00])) # pcm (lend)
    file.write(bytes([0x01, 0x00])) # mono (lend)
    file.write(bytes(ToByteArr(wavetest.samplerate, 4, endian=0)))## 22050 (lend) = $22 56, or $44 ac for 44100
    file.write(bytes(ToByteArr(wavetest.samplerate, 4, endian=0))) # byterate (lend) <- bitrate / 8 = 22050. if 8bit simply size of samples again.de
    file.write(bytes([0x01, 0x00])) # block align - bytes for 1 sample (lend)
    file.write(bytes([0x08, 0x00])) # bits per sample (8)

    file.write(bytes([0x64, 0x61, 0x74, 0x61])) # 'data'
    file.write(bytes(ToByteArr(wavetest.samples, 4, endian=0))) # data block size (22050b)


'''actual app class'''
class msfx_window(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('MSFX2')

        self.wave_vals = []
        self.wave_freq_entries = []
        self.wave_freq_scroll = []
        self.enabled = []
        self.noise = []

        i = 0
        while i < 3:
            if i == 0:
                ltr = 'A'
            elif i == 1:
                ltr = 'B'
            else:
                ltr = 'C'
            l = tk.Label(self, text='Channel {} freq:'.format(ltr))
            l.grid(row=i*2, columnspan=3)
            
            self.wave_vals.append(tk.StringVar())
            wv = self.wave_vals[i]
            wv.trace('w', lambda name, index, mode, wv=wv: self.changefreq)

            self.wave_freq_entries.append(tk.Entry(self, width=4, textvariable=self.wave_vals[i]))
            self.wave_freq_entries[i].grid(row=i*2, column=4)
            
            self.wave_freq_scroll.append(tk.Scale(self, orient=tk.HORIZONTAL, to=4095, resolution=1)) #command=lambda a:self.changefreq(self.wave_freq_scroll[i].get(), self.wave_freq_scroll[i])))
            self.wave_freq_scroll[i].grid(row=(i*2)+1, column=1, columnspan=5, sticky='EW')
            
            tk.Label(self, text='Enabled?').grid(row=i*2, column=7)
            tk.Label(self, text='Music/Noise/Mix?').grid(row=i*2, column=8, columnspan=3)
            
            self.enabled.append(tk.BooleanVar())
            tk.Checkbutton(self, variable=self.enabled[i]).grid(row=(i*2)+1, column=7)
            
            self.noise.append(tk.IntVar())
            tk.Radiobutton(self, variable=self.noise[i], value = 0).grid(row=(i*2)+1, column=8)
            tk.Radiobutton(self, variable=self.noise[i], value=1).grid(row=(i*2)+1, column=9)
            tk.Radiobutton(self, variable=self.noise[i], value=2).grid(row=(i*2)+1, column=10)
            
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
        
        tk.Button(self, text='<', command=lambda:self.freq_inc(0, -1)).grid(row=1, column=0)
        tk.Button(self, text='>', command=lambda:self.freq_inc(0, 1)).grid(row=1, column=6)
        tk.Button(self, text='<', command=lambda:self.freq_inc(1, -1)).grid(row=3, column=0)
        tk.Button(self, text='>', command=lambda:self.freq_inc(1, 1)).grid(row=3, column=6)
        tk.Button(self, text='<', command=lambda:self.freq_inc(2, -1)).grid(row=5, column=0)
        tk.Button(self, text='>', command=lambda:self.freq_inc(2, 1)).grid(row=5, column=6)

        tk.Button(self, text='Save .WAV', command=self.makefile).grid(row=6, column=3, columnspan=6)


    def freq_inc(self, wav, delta):
        self.wave_freq_scroll[wav].set(self.wave_freq_scroll[wav].get()+delta)


    def changefreq(self, o, num, manual=False):
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

            self.wave_freq_entries[num].delete(0,tk.END)
            self.wave_freq_entries[num].insert(0,c)
            self.wave_freq_scroll[num].set(c)


    def makefile(self):
        fre = int(self.wave_freq_entries[0].get())
        w = msxwaveform(hex_freq = fre)

        try:
            f = open('test2.wav', 'wb')

            writeheader(w, f)

            for i in w.y:
                i = int(i)
                f.write(bytes([i]))

            print('.wav written successfully!')

        except:
            print('something went wrong.')

        finally:
            if(f):
                f.close()
#### end def for msfx_window


app = msfx_window()
app.mainloop()