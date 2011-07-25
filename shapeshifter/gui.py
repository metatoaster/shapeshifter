from os.path import basename, dirname
from sys import exit

from Tkinter import *

import tkFileDialog
import tkSimpleDialog

from settings import AppConfig
from log import logger
from parser import Parser


class ParserDialog(Frame):

    def __init__(self, master=None, parsers=None):
        Frame.__init__(self, master)
        self.parsers = parsers
        self.config = AppConfig()
        self.pack()
        self.createWidgets()

    def newCheckboxValues(self):
        result = {}
        for p in self.parsers:
            result.update(p)
        for i in result.keys():
            result[i] = IntVar()
        return result

    def createWidgets(self):
        logger.info('creating parser widgets')
        if not self.parsers:
            self.createNothingLabel()
            self.createCloseButton()
            return

        self.columns = self.newCheckboxValues()
        # XXX apply settings here
        keys = sorted(self.columns.keys())

        self.checkboxes = []
        for k in keys:
            c = Checkbutton(self,
                text=k,
                variable=self.columns[k],
                width='20',
                anchor=W,
            )
            c.pack()

        self.createCloseButton()

    def createNothingLabel(self):
        self.label = Label(self,
            text='Nothing was extracted',
            width='30',
            justify=LEFT,
            anchor=W,
        )
        self.label.pack(fill=X)

    def createCloseButton(self):
        self.close = Button(self,
            text='Close',
            command=self.master.destroy,
            width='10',
        )
        self.close.pack({
            'side': 'right',
        })


class FilenameFrame(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.scrollbar = Scrollbar(self)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.filenames = Listbox(self,
            bg='white',
            height='10',
            width='30',
            yscrollcommand=self.scrollbar.set
        )
        self.filenames.pack(fill=BOTH, expand=1)


class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.config = AppConfig()
        self.config.read()
        self.createWidgets()
        self.parsers = []

    def createWidgets(self):

        self.label = Label(self,
            text='Files to be parsed:',
            width='30',
            justify=LEFT,
            anchor=W,
        )
        self.label.pack(fill=X)

        self.filenameframe = FilenameFrame(self)
        self.filenameframe.pack(fill=BOTH, expand=1)

        self.hi = Button(self,
            text='Open...',
            command=self.dialogFilenames,
            width='10',
        )
        self.hi.pack({
            'side': 'left',
        })

        self.hi = Button(self,
            text='Run...',
            command=self.dialogRun,
            width='10',
        )
        self.hi.pack({
            'side': 'left',
        })

        self.quit = Button(self,
            text='Quit',
            command=self.quit,
            width='10',
        )
        self.quit.pack({
            'side': 'right',
        })

        self.pack(
            side=LEFT,
            fill=BOTH,
            expand=1,
        )

    @property
    def filenames(self):
        return self.filenameframe.filenames.get(0, END)

    def dialogRun(self):
        self.parsers = []
        filenames = self.filenames
        logger.info('%d file(s) to parse', len(filenames))
        for fn in filenames:
            p = Parser(fn)
            try:
                p.parse()
            except:
                # skip this file
                logger.error('Failed to parse file "%s"', fn)
                continue
            self.parsers.append(p)

        rundialog = Toplevel()
        center(rundialog)
        parserdialog = ParserDialog(rundialog, parsers=self.parsers)
        rundialog.focus_set()
        rundialog.grab_set()
        rundialog.transient(self)
        rundialog.wait_window(rundialog)

    def dialogFilenames(self):
        formats = [
            ('Text files', '*.txt'),
            ('All files', '*.*'),
        ]

        filenames = tkFileDialog.askopenfilename(
            multiple=1,
            filetypes=formats,
            initialdir=self.config.get('cwd'),
        )

        if filenames:
            cwd = dirname(filenames[0])
            self.config['cwd'] = cwd

        lb = self.filenameframe.filenames
        lb.delete(0, END)
        for i in filenames:
            lb.insert(END, i)

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
    app.master.title('Format Extractor')
    app.mainloop()
    root.destroy()
