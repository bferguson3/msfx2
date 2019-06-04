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
        self.volume = 255
        self.env_freq = (3580000/2) / (256*self.env_period)
        self.x = np.arange(self.samples)
        self.y = sg.square(2*np.pi*self.freq*self.x/self.samplerate)
        self.y = (self.volume/2) * self.y + (self.volume/2)

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
    else: #(20 million)
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


# now write wav header
def writeheader(file):
    file.write(bytes([0x52, 0x49, 0x46, 0x46])) # RIFF)
    file.write(bytes(ToByteArr(36+wavetest.samples, 4, endian=0)))# [0x68, 0xac, 0x00, 0x00])) # 36 + data size (lend) 22050 or $68 $ac for 44100
    file.write(bytes([0x57, 0x41, 0x56, 0x45])) # WAVE)
    file.write(bytes([0x66, 0x6d, 0x74, 0x20])) # 'fmt '
    file.write(bytes([0x10, 0x00, 0x00, 0x00])) # pcm (lend)
    file.write(bytes([0x01, 0x00])) # pcm (lend)
    file.write(bytes([0x01, 0x00])) # mono (lend)
    file.write(bytes(ToByteArr(wavetest.samplerate, 4, endian=0)))#[0x44, 0xac, 0x00, 0x00])) # 22050 (lend) = $22 56, or $44 ac for 44100
    file.write(bytes(ToByteArr(wavetest.samplerate, 4, endian=0))) # byterate (lend) <- bitrate / 8 = 22050. if 8bit simply size of samples again.de
    file.write(bytes([0x01, 0x00])) # block align - bytes for 1 sample (lend)
    file.write(bytes([0x08, 0x00])) # bits per sample (8)
    file.write(bytes([0x64, 0x61, 0x74, 0x61])) # 'data'
    file.write(bytes(ToByteArr(wavetest.samples, 4, endian=0))) # data block size (22050b)


class msfx_window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('MSFX2')

        self.wave_vals = []
        self.wave_freq_entries = []
        self.wave_freq_scroll = []
        i = 0
        while i < 3:
            

        self.wave_one_freq_txt = tk.Label(self, text='Channel A freq:')
        self.wave_one_freq_txt.grid(row=0, columnspan=3)
        waveoneval = tk.StringVar()
        self.wave_one_freq_entry = tk.Entry(self, width=4, textvariable=waveoneval)
        waveoneval.trace("w", lambda name, index, mode, waveoneval=waveoneval: self.changefreq(waveoneval))
        self.wave_one_freq_entry.grid(row=0, column=4)
        self.wave_one_down = tk.Button(self, text='<', command=lambda:self.freq_inc(1,-1))
        self.wave_one_down.grid(row=1, column=0)
        self.wave_one_up = tk.Button(self, text='>', command=lambda:self.freq_inc(1, 1))
        self.wave_one_up.grid(row=1, column=6)
        self.wave_one_freq_sb = tk.Scale(self, orient=tk.HORIZONTAL, to=4095, resolution=1, command=self.changefreq)
        self.wave_one_freq_sb.grid(row=1, column=1, columnspan=5, sticky='EW')


    def freq_inc(self, wavenum, delta):
        if wavenum == 1:
            self.wave_one_freq_sb.set(self.wave_one_freq_sb.get()+delta)

    def changefreq(self, o):
        if type(o) == tk.StringVar:
            if o.get() == '':
                return
            if len(o.get()) > 4:
                o.set(o.get()[:4])
            c = int(o.get())
            if c > 4095:
                c = 4095
                self.wave_one_freq_entry.delete(0,tk.END)
                self.wave_one_freq_entry.insert(0,c)
            self.wave_one_freq_sb.set(c)
        else:
            self.wave_one_freq_entry.delete(0,tk.END)
            c = self.wave_one_freq_sb.get()
            self.wave_one_freq_entry.insert(0,c)
            


wavetest = msxwaveform(hex_freq=(1*256)+255, length=2)

f = open('test2.wav', 'wb')
writeheader(f)
for i in wavetest.y:
    i = int(i)
    f.write(bytes([i]))
f.close()

app = msfx_window()
app.mainloop()