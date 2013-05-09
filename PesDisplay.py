from tkinter import *

import PesTest as pes





master = Tk()

w = Canvas(master, width=500, height=100)
w.pack()

fileData = pes.loadPESFile('FB_text_objects.pes')
translate = fileData['blockData']['translateStart']

fill = lambda a: "#%02x%02x%02x"%a

for blk in fileData['blockData']['blocks']:
	pts = blk.getPoints(translate)
	color = fill(blk.color)
	w.create_line(pts,fill=color)

mainloop()