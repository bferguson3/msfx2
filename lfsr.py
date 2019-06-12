################################
# Linear feedback shift register example

# Example usage:
#  a = lfsr(random.randrange(0,255))
#  print(format(int(a.tick_output(8),2), '02x'))
# Will initialize a random 8-bit initeger in the register, 
# then print an 8-tick (one byte) output from the register in hex form


import random 
from collections import deque 


class lfsr(object):
    ''' creates lfsr object '''
    def __init__(self, init=26, taps=[3, 4, 5, 7]):
        if init < 256:
            self.bin = format(init, '08b')
        elif init < 65536:
            self.bin = format(init, '016b')
        elif init < 16777216:
            self.bin = format(init, '024b')
        elif init < 4294967296:
            self.bin = format(init, '032b')
        self.int = int(self.bin,2)
        self.d = deque(self.bin)
        self.taps = taps # and always highest bit!
        self.output = 0

    def shift(self):
        ''' performs shift ''' 
        # rotate right
        r = self.d.pop()
        self.d.appendleft(r)
        # first, check to see if there are any 1s in the tap positions
        i = 0
        ok = False
        while i < len(self.d):
            if self.d[i] == '1':
                ok = True
                break
            i += 1
        if ok == False:
            self.shift()
            return 

        t = self.d.pop()
        t_b = int(t,2)
        self.output = t_b
        i = len(self.d)-1
        while i >= 0:
            for tap in self.taps:
                if i == tap:
                    s = int(self.d[i],2)
                    t_b = s ^ t_b
            i -= 1
        self.d.appendleft(str(t_b))
        return self.d 

    def state_to_int(self):
        ''' returns current state of LFSR in integer form '''
        b = 0
        out = []
        while b < len(self.d):
            out.append(self.d[b])
            b += 1
        out = ''.join(out)
        return int(out,2)

    def state_to_hex(self):
        ''' returns current state of LFSR in format: $xx '''
        b = 0
        out = []
        while b < len(self.d):
            out.append(self.d[b])
            b += 1
        out = ''.join(out)
        return '$' + format(int(out,2), '02x')

    def tick_output(self, n=1):
        ''' returns 'n' outputs [0/1] concatenated to a single integer '''
        i = 0
        out = []
        while i < n:
            self.shift()
            out.append(str(self.output))
            i += 1
        out = ''.join(out)
        return out
