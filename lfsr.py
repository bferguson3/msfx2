import random 
from collections import deque 

initial = random.randrange(0,255,1)
initial = format(initial,'08b')

taps = [3, 4, 5]

lfsr = deque(initial)

def shift(lfsr):
    t = lfsr.pop()
    lfsr.appendleft(t)
    t_b = int(t,2)
    i = 0
    while i < len(lfsr):
        for tap in taps:
            if i == tap:
                s = int(lfsr[i],2)
                s = s ^ t_b
                lfsr[i] = str(s)  
        i += 1


k = 0
while k < 10:
    shift(lfsr)
    b = 0
    out = []
    while b < len(lfsr): 
        out.append(lfsr[b])
        b += 1
    out = ''.join(out)
    print(int(out,2))
    k += 1