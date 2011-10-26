from os.path import basename, dirname, exists
from sys import exit

from Tkinter import *

import tkMessageBox
import tkFileDialog
import tkSimpleDialog

from shapeshifter.settings import AppConfig
from shapeshifter.log import logger
from shapeshifter.reader import ParserList, ParserDict


class RunDialog(Toplevel):

    def parserFrame(self, parsers):
        # we can deal with duplicated references later.
        self.parsers = parsers
        self.config = AppConfig()
        self.frame = ColumnSelectFrame(self)

    def endParserFrame(self):
        # triggers when continue was triggered for the above
        columns = self.frame.columns
        self.config['columns'] = columns
        self.columns = columns
        self.frame.destroy()
        self.frame = DataDisplayFrame(self)
        self.frame.pack(fill=BOTH, expand=1)


class DataDisplayFrame(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.config = AppConfig()
        self.createWidgets()
        self.pack(fill=BOTH, expand=1)

    def createOutput(self):
        def csvline(items):
            return ','.join(['"%s"' % s for s in items])
        lines = []
        columns = self.master.columns
        header = csvline(columns)
        lines.append(header)
        for p in self.master.parsers:
            line = csvline([p.get(c, '') for c in columns])
            lines.append(line)

        return '\n'.join(lines)

    def createWidgets(self):
        logger.info('Display data')
        self.createTextArea()
        self.createButtons()
        self.output = self.createOutput()

        self.textarea.insert('1.0', self.output)
        self.textarea.config(state=DISABLED)

    def createTextArea(self):
        self.textframe = Frame(self)

        self.scrollbar = Scrollbar(self.textframe)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.textarea = Text(self.textframe,
            width='80',
            height='25',
            yscrollcommand=self.scrollbar.set,
        )
        self.scrollbar.config(command=self.textarea.yview)
        self.textarea.pack(side=TOP, fill=BOTH, expand=1,)

        self.textframe.pack(fill=BOTH, expand=1)

    def createButtons(self):
        self.close = Button(self,
            text='Close',
            command=self.master.destroy,
            width='10',
        )
        self.close.pack({
            'side': 'right',
        })

        self.save = Button(self,
            text='Save...',
            command=self.dialogSaveCSV,
            width='10',
        )
        self.save.pack({
            'side': 'right',
        })

    def dialogSaveCSV(self):
        formats = [
            ('Comma Seperated Value file', '*.csv'),
            ('All files', '*.*'),
        ]

        csvfile = self.config.get('csvfile', None)
        filename = tkFileDialog.asksaveasfilename(
            initialfile=csvfile,
            filetypes=formats,
            initialdir=self.config.get('cwd'),
        )

        if filename:
            self.saveoutput(filename)
            self.config['csvfile'] = basename(filename)

    def saveoutput(self, filename):
        # looks like this is built in...
        # if exists(filename):
        #     result = tkMessageBox.askyesno("File exists", 
        #         'Overwrite the file "%s"?' % filename)
        #     if not result:
        #         return

        try:
            f = open(filename, 'w')
        except IOError:
            logger.error('Cannot open "%s" for writing', filename)
            return

        try:
            f.write(self.output)
        except:
            logger.error('Failed to write to "%s"', filename)
        finally:
            f.close()

        logger.info('Wrote result to "%s"', filename)


class ColumnSelectSubFrame(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.config = AppConfig()
        self.pack()
        self.createWidgets()
        self.populateSelections()

    @property
    def parsers(self):
        return self.master.master.parsers

    @property
    def columns(self):
        return [i for i in self.original if i in 
                list(self.lbSelect.get(0, END))]

    def _updateSelection(self, selected):
        self.lbSelect.delete(0, END)
        for i in selected:
            self.lbSelect.insert(END, i)

    def addSelection(self):
        selected = set(self.lbSelect.get(0, END))
        selected = sorted(list(selected.union(
            set([self.lbAll.get(i) for i in self.lbAll.curselection()]))
        ))
        self._updateSelection(selected)

    def removeSelection(self):
        selected = set(self.lbSelect.get(0, END))
        selected = sorted(list(selected.difference([self.lbSelect.get(i)
            for i in self.lbSelect.curselection()])))
        self._updateSelection(selected)

    def populateSelections(self):
        # grab the columns from each of the completed parsers
        result = {}
        for p in self.parsers:
            result.update(p)

        self.original = result.keys()
        available = sorted(self.original)

        raw = set(self.config.get('columns', []))
        raw = raw.intersection(set(available))
        previous = sorted(list(raw))

        for i in available:
            self.lbAll.insert(END, i)

        for i in previous:
            self.lbSelect.insert(END, i)

    def createWidgets(self):

        # List of available selction
        self.scrollbarAll = Scrollbar(self)
        self.lbAll = Listbox(self,
            height='10',
            width='30',
            selectmode=EXTENDED,
            yscrollcommand=self.scrollbarAll.set,
        )
        self.scrollbarAll.config(command=self.lbAll.yview)
        self.lbAll.pack(side=LEFT, fill=BOTH, expand=1)
        self.scrollbarAll.pack(side=LEFT, fill=Y)

        # List of selected selction
        self.scrollbarSelect = Scrollbar(self)
        self.lbSelect = Listbox(self,
            height='10',
            width='30',
            selectmode=EXTENDED,
            yscrollcommand=self.scrollbarSelect.set,
        )
        self.scrollbarSelect.config(command=self.lbSelect.yview)
        self.scrollbarSelect.pack(side=RIGHT, fill=Y)
        self.lbSelect.pack(side=RIGHT, fill=BOTH, expand=1)

        # buttons
        self.buttonFrame = Frame(self)

        self.btnAdd = Button(self.buttonFrame,
            text='Add >>',
            command=self.addSelection,
            width='10',
        )
        self.btnAdd.pack(anchor=CENTER)

        self.btnRem = Button(self.buttonFrame,
            text='<< Remove',
            command=self.removeSelection,
            width='10',
        )
        self.btnRem.pack(anchor=CENTER)

        self.buttonFrame.pack(side=RIGHT)


class ColumnSelectFrame(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.config = AppConfig()
        self.pack(fill=BOTH, expand=1)
        self.createWidgets()

    @property
    def columns(self):
        return self.selectframe.columns

    def createWidgets(self):
        logger.info('creating parser widgets')
        if not self.master.parsers:
            self.createNothingLabel()
            self.createCloseButton()
            return

        self.selectframe = ColumnSelectSubFrame(self)
        self.selectframe.pack(fill=BOTH, expand=1)
        self.createContinueButton()

    def createContinueButton(self):
        self.close = Button(self,
            text='Continue',
            command=self.master.endParserFrame,
            width='10',
        )
        self.close.pack({
            'side': 'right',
        })

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
            height='10',
            width='30',
            yscrollcommand=self.scrollbar.set
        )
        self.scrollbar.config(command=self.filenames.yview)
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

        self.btnRun = Button(self,
            text='Open...',
            command=self.dialogFilenames,
            width='12',
        )
        self.btnRun.pack({
            'side': 'left',
        })

        self.btnRun = Button(self,
            text='Run...',
            command=self.dialogRun,
            width='12',
        )
        self.btnRun.pack({
            'side': 'left',
        })

        self.reset = Button(self,
            text='Reset Settings',
            command=self.resetSettings,
            width='12',
        )
        self.reset.pack({
            'side': 'left',
        })

        self.quit = Button(self,
            text='Quit',
            command=self.quit,
            width='12',
        )
        self.quit.pack({
            'side': 'right',
        })

        self.pack(
            side=LEFT,
            fill=BOTH,
            expand=1,
        )

        filenames = self.config.get('lastparsed', [])
        lb = self.filenameframe.filenames
        for i in filenames:
            lb.insert(END, i)

    @property
    def filenames(self):
        return self.filenameframe.filenames.get(0, END)

    def dialogRun(self):
        self.parsers = []
        filenames = self.filenames
        self.config['lastparsed'] = list(filenames)
        logger.info('%d file(s) to parse', len(filenames))
        for fn in filenames:
            p = ParserList(fn)
            logger.info('parsing "%s"', fn)
            try:
                p.parse()
            except:
                # skip this file
                logger.exception('Failed to parse file "%s"', fn)
                continue
            self.parsers.extend(p)

        rundialog = RunDialog()
        center(rundialog)
        rundialog.parserFrame(self.parsers)
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

        # XXX workaround windows version bug
        if isinstance(filenames, basestring):
            filenames = self.tk.splitlist(filenames)

        if filenames:
            cwd = dirname(filenames[0])
            self.config['cwd'] = cwd

        lb = self.filenameframe.filenames
        lb.delete(0, END)

        for i in filenames:
            lb.insert(END, i)

    def resetSettings(self):
        self.config.delete()

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

def run():
    root = Tk()
    center(root)
    app = Application(master=root)
    app.master.title('Format Extractor')
    app.mainloop()
    root.destroy()

if __name__ == '__main__':
    run()
