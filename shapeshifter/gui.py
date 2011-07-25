from os.path import basename, dirname
from sys import exit
from Tkinter import Tk
from Tkinter import Button
from Tkinter import Frame

import tkFileDialog

from settings import AppConfig
from log import logger


class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.config = AppConfig()
        self.config.read()
        self.createWidgets()
        self.filenames = []

    def createWidgets(self):
        self.quit = Button(self,
            text='Quit',
            command=self.quit,
            width='10',
        )
        self.quit.pack({
            'side': 'right',
        })

        self.hi = Button(self,
            text='Open...',
            command=self.dialogFilenames,
            width='10',
        )
        self.hi.pack({
            'side': 'left',
        })

    def dialogFilenames(self):
        formats = [
            ('Text files', '*.txt'),
            ('All files', '*.*'),
        ]

        self.filenames = tkFileDialog.askopenfilename(
            multiple=1,
            filetypes=formats,
            initialdir=self.config.get('cwd'),
        )

        if self.filenames:
            cwd = dirname(self.filenames[0])
            self.config['cwd'] = cwd

    def quit(self):
        self.config.write()
        Frame.quit(self)


def center(window):
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    rw = window.winfo_reqwidth()
    rh = window.winfo_reqheight()
    xc = (sw - rw) / 2
    yc = (sh - rh) / 2
    window.geometry("+%d+%d" % (xc, yc))
    window.deiconify()    

if __name__ == '__main__':
    root = Tk()
    center(root)
    app = Application(master=root)
    app.master.title = 'Format Extractor'
    app.mainloop()
    root.destroy()
