import random 
from collections import deque 


class lfsr(object):
    def __init__(self, init):
        self.bin = format(init, '08b')
        self.int = int(self.bin,2)
        self.d = deque(self.bin)
        self.taps = [3, 4, 5] # and 8!

    def shift(self):
        t = self.d.pop()
        self.d.appendleft(t)
        t_b = int(t,2)
        i = 0
        while i < len(self.d):
            for tap in self.taps:
                if i == tap:
                    s = int(self.d[i],2)
                    s = s ^ t_b 
                    self.d[i] = str(s)
            i += 1
        return self.d 

    def lfsr_to_int(self):
        b = 0
        out = []
        while b < len(self.d):
            out.append(self.d[b])
            b += 1
        out = ''.join(out)
        return int(out,2)

a = lfsr(random.randrange(0,255))
a.shift()
print(a.lfsr_to_int())
a.shift()
print(a.lfsr_to_int())
a.shift()
print(a.lfsr_to_int())
a.shift()
print(a.lfsr_to_int())
a.shift()
print(a.lfsr_to_int())
a.shift()
print(a.lfsr_to_int())

# initial = random.randrange(0,255,1)
# initial = format(initial,'08b')

# taps = [3, 4, 5]

# lfsr = deque(initial)

# def shift(lfsr):
#     t = lfsr.pop()
#     lfsr.appendleft(t)
#     t_b = int(t,2)
#     i = 0
#     while i < len(lfsr):
#         for tap in taps:
#             if i == tap:
#                 s = int(lfsr[i],2)
#                 s = s ^ t_b
#                 lfsr[i] = str(s)  
#         i += 1
#     return lfsr_to_int(lfsr)

# def lfsr_to_int(lfsr):
#     b = 0
#     out = []
#     while b < len(lfsr):
#         out.append(lfsr[b])
#         b += 1
#     out = ''.join(out)
#     return int(out,2)


#k = 0
#while k < 10:
#    shift(lfsr)
#    b = 0
#    out = []
#    while b < len(lfsr): 
#        out.append(lfsr[b])
#        b += 1
#    out = ''.join(out)
#    print(int(out,2))
#    k += 1