import tkinter as tk 
import math 

class sccvis_win(tk.Tk):
    def __init__(self):
        super().__init__()
        
        visw = 640
        vish = 480

        self.visframe = tk.Canvas(self, width=visw, height=vish, background='#FFF')

        self.wfpx = []
        self.wf_data = []

        self.pxw = visw/32
        self.pxh = vish/256
        
        j = 0
        while j < 256:
            y = self.pxh*j 
            i = 0
            while i < 32:
                x = self.pxw*i
                            
                self.wfpx.append(self.visframe.create_rectangle(x, y, x+self.pxw, y+self.pxh, fill='#FFF', outline='#aaa'))
                
                i += 1
            j += 1

        i = 0
        while i < 32:
            self.visframe.itemconfig(self.wfpx[(32*128)+i], fill='#000')
            self.wf_data.append(128)
            i += 1

        self.visframe.bind("<Button-1>", self.draw_wave_shape)
        self.visframe.bind("<B1-Motion>", self.draw_wave_shape)

        self.visframe.grid(row=0, column=0, columnspan=8, rowspan=8)
        
        tk.Label(self, text='Frequency (0-15):').grid(row=9,column=0,sticky='e')
        self.freq_input = tk.Entry(self, width=4)
        self.freq_input.grid(row=9, column=1, sticky='w')
        self.button_make = tk.Button(self, text='Make .z80', command=self.writefile)
        self.button_make.grid(row=9,column=2,sticky='ew')
        #tk.Label(self, text='Frequency:').grid(row=0, column=1, sticky='s')
        #self.channel_no = tk.Entry(self, width=4)
        #self.channel_no.grid(row=1, column=1, sticky='n')

    #
    def writefile(self):
        try:
            fv = int(self.freq_input.get())
        except:
            self.freq_input.delete(0, tk.END)
            self.freq_input.insert(tk.END, '0')
            fv = 0 
        if fv < 0:
            self.freq_input.delete(0, tk.END)
            self.freq_input.insert(tk.END, '0')
            fv = 0
        if fv > 15:
            self.freq_input.delete(0, tk.END)
            self.freq_input.insert(tk.END, '15')
            fv = 15
        out = []
        out.append(' fname \"sccplus.bin\"\n\n')
        out.append('header:\n db $fe\n dw init\n dw EOF\n dw init\n\n')
        out.append(' org $c000\n\n')

        out.append("""
init:
DetectSCC:

ENASLT:		EQU	$0024
EXPTBL:		EQU	$FCC1
SCCSLOT: equ $ce34

SCANSLT:
	XOR	A		; start from slot 0
	LD	HL,EXPTBL
.loop:
	LD	C,(HL)
	OR	C
.loop2:
	EXX

	LD	(CHK_SCC.c_slt),A	; save current slot

	PUSH	AF

	LD	H,$80
	CALL	ENASLT

	CALL	CHK_SCC

	POP	AF

	EXX

	ADD	A,%00000100	; increase subslot number
	LD	C,A		; C = new slot + subslot
	BIT	7,A		; check if slot expanded
	JR	Z,.next		; if not expanded go for next slot
	AND	%00001100	; check if already checked all subslots
	LD	A,C
	JR	NZ,.loop2	; still some subslots left
.next:
	INC	HL
	LD	A,C
	INC	A
	AND	%00000011
	RET	Z		; return if all slots & subslots are checked!
;
	JR	.loop

CHK_SCC:
	LD	HL,$A000
	LD	DE,$BFFE
	LD	BC,$2000	; C = 00h -> SCC = YES if found
	XOR	A
	LD	(DE),A		; SET ROM + SCC if SCC-I cartridge
	LD	A,(HL)
	INC	A
	LD	(HL),A
	CP	(HL)
	RET	Z		; found RAM -> return

	LD	HL,$97FF
	LD	(HL),L		; activate SCC write (write xx111111)
	INC	HL		; HL = 9800h
	LD	A,(HL)
	INC	A
	LD	(HL),A
	CP	(HL)
	RET	NZ
	DEC	A
	LD	(HL),A

.f_SCC:
	XOR	A
	DEC	HL
	LD	(HL),A		; disable write to SCC RAM

	LD	A,B
	LD	(DE),A		; SET ROM + SCC+ if SCC-I present
	LD	HL,$B7FF
	LD	(HL),L		; activate SCC+ write (write 1xxxxxxx)
	INC	HL		; HL = B800h
	LD	A,(HL)
	INC	A
	LD	(HL),A
	CP	(HL)
	JR	NZ,.setSCC
	DEC	A
	LD	(HL),A

.f_SCCI:
	INC	C		; C = 1 -> SCC+ = YES

.setSCC:
	XOR	A
	DEC	HL
	LD	(HL),A		; disable write to SCC+ RAM

	LD	A,$00	; register "A" will contain slot/subslot with SCC Cartridge
.c_slt:	EQU	$ - 1	; register "C" will contain "0" for SCC and "1" for SCC+

    ld (SCCSLOT), a 

    pop af 
    pop af 

	ld a, $20
	ld ($bffe), a 

	ld a, $80
	ld ($b000), a 

	ld a, 15
	ld ($b8aa), a 

	ld a, $ff 
	ld ($b8af), a 

	ld a, """+ str(fv) + """ 
	ld ($b8a1), a 
	
	ld hl, waveform
    ld de, $b800
    ld bc, 32
    ldir 

    ld a, 1
    call $5f 


loop: jp loop 

""")
        out.append('waveform:\n')
        i = 0
        while i < 4:
            j = 0
            out.append(' db ')
            while j < 8:
                if j != 7:
                    out.append('$'+ format(self.wf_data[(i*8)+j], '02x')+',')
                else:
                    out.append('$'+ format(self.wf_data[(i*8)+j], '02x'))
                j += 1
            out.append('\n')
            i += 1
        out.append('EOF:')
        out = ''.join(out)
        f = open('sccvis.z80', 'w')
        for c in out:
            f.write(c)
        f.close()
        #print(out)
        return

    def draw_wave_shape(self, o):
        if o.x > self.visframe.winfo_width() or o.x < 0:
            return 
        if o.y > self.visframe.winfo_height() or o.y < 0:
            return 
        
        xp = math.floor(o.x/self.pxw)
        yp = math.floor(o.y/self.pxh)
        
        i = 0
        while i < 255:
            self.visframe.itemconfig(self.wfpx[(i*32)+xp], fill='#FFF')
            i += 1
        if yp <= 128: # positive amplitude
            i = 128
            while i > yp:
                self.visframe.itemconfig(self.wfpx[((yp-(i-128))*32)+xp], fill='#000')
                i -= 1
        if yp > 128: # negative amplitude
            i = 128
            while i < yp:
                self.visframe.itemconfig(self.wfpx[((yp+(128-i))*32)+xp], fill='#000')
                i += 1

        if yp <= 128:
            self.wf_data[xp] = 256-(128+yp)
        else:
            self.wf_data[xp] = 127+(256-yp) 
    #       
##

app = sccvis_win()
app.mainloop()