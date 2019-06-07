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
#import playsound # sudo apt-get install python3-pyaudio
import time 
import pyaudio
from threading import Thread
from tkinter import messagebox

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
    def __init__(self, samplerate=22000, hex_freq=254, length=1, envelope = False, envelopetype=envelope_types['decline'], env_period = 6992):
        self.samplerate = samplerate 
        self.hex_freq = hex_freq #254 ~= 440 A(4)
        self.length = length
        self.envelope = envelope
        self.envelopetype = envelopetype
        self.env_period = env_period    # 6992 or 1b50h is ~1s
        self.env_bin = ''

        if env_period >= (256*256):
            self.env_period = 65535
        if hex_freq > 4095:
            self.hex_freq = 4095
        
        self.freq = (3580000/2) / (16*self.hex_freq)

        self.samples = self.length * self.samplerate

        self.volume = 127   # max value of simulated envelope

        self.env_freq = (3580000/2) / (256*self.env_period) 

        self.x = np.arange(self.samples)

        self.y = sg.square(2*np.pi*self.freq*self.x/self.samplerate) # actual wave generation
        #self.y = (self.volume/2) * self.y + (self.volume/2) # adjust amplitude for volume
        self.y = self.volume * self.y 

        #if self.envelope == True:
        #    apply_envelope(self)
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
def writeheader(wavetest, file):
    global app 
    s = 0
    for b in app.enabled:
        if b.get() == True:
            s += 1
            print(s)
    #print(len(wavetest.y))
    # Q R S T U V W X
    #  52535455565758
    file.write(bytes([0x52, 0x49, 0x46, 0x46])) # RIFF)
    file.write(bytes(ToByteArr(36+(wavetest.samples*s), 4, endian=0)))# 36 + data size (lend) 22050 or $68 $ac for 44100
    file.write(bytes([0x57, 0x41, 0x56, 0x45])) # WAVE)

    file.write(bytes([0x66, 0x6d, 0x74, 0x20])) # 'fmt '
    file.write(bytes([0x10, 0x00, 0x00, 0x00])) # pcm (lend)
    file.write(bytes([0x01, 0x00])) # pcm (lend)
    file.write(bytes([0x01, 0x00])) # mono (lend)
    file.write(bytes(ToByteArr(wavetest.samplerate*s, 4, endian=0)))## 22050 (lend) = $22 56, or $44 ac for 44100
    file.write(bytes(ToByteArr(wavetest.samplerate*s, 4, endian=0))) # byterate (lend) <- bitrate / 8 = 22050. if 8bit simply size of samples again.de
    file.write(bytes([0x02, 0x00])) # block align - bytes for 1 sample (lend)
    file.write(bytes([0x10, 0x00])) # bits per sample (8)

    file.write(bytes([0x64, 0x61, 0x74, 0x61])) # 'data'
    file.write(bytes(ToByteArr(wavetest.samples*s, 4, endian=0))) # data block size (22050b)
#

def apply_envelope(msxwav):
    env_len = msxwav.env_freq # 6992
    #print(env_len)
    x = np.arange(32*msxwav.length) #32 per second

    global envelope_types
    # denominator is num of samples, therefore resolution of envelope
    if msxwav.envelopetype == envelope_types['inv_sawtooth']:
        y = (sg.sawtooth(2 * np.pi * (1/env_len) * x / (32), 0) + 1)/2

    elif msxwav.envelopetype == envelope_types['decline']:
        y = (sg.sawtooth(2 * np.pi * (1/env_len) * x / (32), 0) + 1)/2
        if len(y) > 32:
            i = 32
            while i < len(y):
                y[i] = 0
                i += 1

    elif msxwav.envelopetype == envelope_types['inv_triangle']:
        y = (sg.sawtooth( ((1 * np.pi * (1/env_len) * x) / 32) + np.pi, 0.5) + 1)/2 #offset by half a second?

    elif msxwav.envelopetype == envelope_types['decline_on']:
        y = (sg.sawtooth(2 * np.pi * (1/env_len) * x / 32, 0) + 1)/2
        if len(y) > 32:
            i = 32
            while i < len(y):
                y[i] = 1
                i += 1

    elif msxwav.envelopetype == envelope_types['sawtooth']:
        y = (sg.sawtooth(2 * np.pi * (1/env_len) * x / 32, 1) + 1)/2

    elif msxwav.envelopetype == envelope_types['incline']:
        y = (sg.sawtooth(2 * np.pi * (1/env_len) * x / 32, 1) + 1)/2
        if len(y) > 32:
            i = 32
            while i < len(y):
                y[i] = 1
                i += 1

    elif msxwav.envelopetype == envelope_types['triangle']:
        y = (sg.sawtooth( ((1 * np.pi * (1/env_len) * x) / 32), 0.5) + 1)/2

    elif msxwav.envelopetype == envelope_types['incline_off']:
        y = (sg.sawtooth(2 * np.pi * (1/env_len) * x / 32, 1) + 1)/2
        if len(y) > 32:
            i = 32
            while i < len(y):
                y[i] = 0
                i += 1
    # end envelope pattern definitions
    
    # TODO: fix this manual amplitude adjustment for proper hardware levels.
    i = 0
    while i < len(y):
        y[i] -= 0.4
        if y[i] < 0:
            y[i] = 0
        i += 1

    i = 0
    j = 0
    perstep = math.ceil(msxwav.samplerate / (32)) 
    for c in msxwav.y:
        c = c * y[j]
        #print(j)
        msxwav.y[i] = int(c)
        i += 1
        if i % perstep == 0:
            j += 1
            if j >= len(y):
                j = 0
            

'''actual app class'''
class msfx_window(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('MSFX2')

        self.wf = None

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
            self.freq_vals_hex[i].grid(row=(i*3)+1, column=5)
            
            self.tones_txt.append(tk.Label(self, text='Tone: <>'))
            self.tones_txt[i].grid(row=(i*3)+1, column=0, columnspan=3)
            
            self.wave_vals.append(tk.StringVar())
            wv = self.wave_vals[i]
            wv.trace('w', lambda name, index, mode, wv=wv: self.changefreq)

            self.wave_freq_entries.append(tk.Entry(self, width=4, textvariable=self.wave_vals[i]))
            self.wave_freq_entries[i].grid(row=i*3, column=4)
            
            self.wave_freq_scroll.append(tk.Scale(self, orient=tk.HORIZONTAL, to=4095, resolution=1)) #command=lambda a:self.changefreq(self.wave_freq_scroll[i].get(), self.wave_freq_scroll[i])))
            self.wave_freq_scroll[i].grid(row=(i*3)+2, column=1, columnspan=5, sticky='EW')
            
            tk.Label(self, text='Enabled?').grid(row=i*3, column=7)
            tk.Label(self, text='Music/Noise/Mix?').grid(row=i*3, column=8, columnspan=3)
            
            self.enabled.append(tk.BooleanVar())
            tk.Checkbutton(self, variable=self.enabled[i]).grid(row=(i*3)+2, column=7)
            
            self.noise.append(tk.IntVar())
            tk.Radiobutton(self, variable=self.noise[i], value = 0).grid(row=(i*3)+2, column=8)
            tk.Radiobutton(self, variable=self.noise[i], value=1).grid(row=(i*3)+2, column=9)
            tk.Radiobutton(self, variable=self.noise[i], value=2).grid(row=(i*3)+2, column=10)
            
            #env_buttons_a=[]
            #env_buttons_b=[]
            #env_buttons_c=[]
            #k = 0
            #while k < 1:
            #    env_buttons_a.append(tk.Button(self, image=decline_off_icon, width=20, height=15))
            #    env_buttons_a[k].grid(row=12)
            #    k += 1

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
        
        tk.Button(self, text='<', command=lambda:self.freq_inc(0, -1)).grid(row=2, column=0)
        tk.Button(self, text='>', command=lambda:self.freq_inc(0, 1)).grid(row=2, column=6)
        tk.Button(self, text='<', command=lambda:self.freq_inc(1, -1)).grid(row=5, column=0)
        tk.Button(self, text='>', command=lambda:self.freq_inc(1, 1)).grid(row=5, column=6)
        tk.Button(self, text='<', command=lambda:self.freq_inc(2, -1)).grid(row=8, column=0)
        tk.Button(self, text='>', command=lambda:self.freq_inc(2, 1)).grid(row=8, column=6)

        tk.Button(self, text='Save .WAV', command=self.makefile).grid(row=9, column=3, columnspan=6)
        tk.Button(self, text='Play last', command=self.playthread).grid(row=9, column=9, columnspan=6)

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

        self.freq_vals_hex[num].config(text='Value: $' + format(self.wave_freq_scroll[num].get(), '04x'))

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
            


    def makefile(self):
        w = []

        s = 0
        i = 0
        while i < len(self.enabled):
            w.append(0)
            if self.enabled[i].get() == True:
                print(i, 'true')
                fre = int(self.wave_freq_entries[i].get())
                w[i] = msxwaveform(hex_freq = fre, envelope=True, length=1, envelopetype=envelope_types['inv_sawtooth'])
                s += 1
            i += 1
        if s == 0:
            print('enable at least one channel!')
            return

        try:
            f = open('test2.wav', 'wb')
            l = 0 
            if w[0] != 0:
                writeheader(w[0], f)
                l = len(w[0].y)
            elif w[1] != 0:
                #print('2')
                writeheader(w[1], f)
                l = len(w[1].y)
            elif w[2] != 0:
                writeheader(w[2], f)
                l = len(w[2].y)

            i = 0
            while i < l:
                # to convert to signed bytes:
                
                if self.enabled[0].get() == True:
                    b = int(w[0].y[i])
                    b += 127
                    print(b)
                    f.write(bytes([b]))
                if self.enabled[1].get() == True:
                    c = int(w[1].y[i])
                    f.write(bytes([c]))
                if self.enabled[2].get() == True:
                    d = int(w[2].y[i])
                    f.write(bytes([d]))
                i += 1
            if (f):
                f.close()
            print('.wav written successfully!')
        #except:
        #    print('something went wrong.')
        except PermissionError:
            print("still open!")
        

    #def makefile(self):
        #t = Thread(target=self.makefile_thread, daemon=True)
        #t.start()

    def playthread(self):
        t = Thread(target=self.playfile, daemon=True)
        t.start()

    def playfile(self):
        #playsound.playsound('test2.wav', False)
        audio = pyaudio.PyAudio()
        self.wf = wave.open('test2.wav','rb')
        stream = audio.open(format=audio.get_format_from_width(self.wf.getsampwidth()),
                            channels=self.wf.getnchannels(),
                            rate=self.wf.getframerate(),
                            output=True,
                            stream_callback=self.play_cb)
        #wd = self.wf.readframes(1024)
        stream.start_stream() 
        while stream.is_active():
            time.sleep(0.1)
        #while wd != b'':
        #    stream.write(wd)
        #    wd = self.wf.readframes(1024)
           #print(wd)
        stream.stop_stream()
        stream.close()
        audio.terminate()

    def play_cb(self, in_data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        return (data, pyaudio.paContinue)
 
            
#### end def for msfx_window
#class audio_player(object):
    #def __init__(self):
   #def playfile(self):
        #audio = pyaudio.PyAudio()
        #self.wf = wave.open('test2.wav','rb')
        #stream = audio.open(format=audio.get_format_from_width(self.wf.getsampwidth()),
        #                    channels=self.wf.getnchannels(),
        #                    rate=self.wf.getframerate(),
        #                    output=True,
        #                    stream_callback=self.play_cb)
        #wd = self.wf.readframes(1024)
        #stream.start_stream()
        #while stream.is_active():
        #    time.sleep(0.1)
        #while wd != b'':
        #    stream.write(wd)
        #    wd = self.wf.readframes(1024)
            #print(wd)
        #stream.stop_stream()
        #stream.close()
        #audio.terminate()

    #def play_cb(self, in_data, frame_count, time_info, status):
    #    data = self.wf.readframes(frame_count)
    #    return (data, pyaudio.paContinue)
 
app = msfx_window() 
icons = icon_datas()
inv_sawtooth_icon = tk.BitmapImage(data=icons.inv_sawtooth_data)
decline_off_icon = tk.BitmapImage(data=icons.decline_off_data)
incline_off_icon = tk.BitmapImage(data=icons.incline_off_data)
tk.Button(app, image=inv_sawtooth_icon, width=16, height=16).grid(row=12)
app.mainloop() 