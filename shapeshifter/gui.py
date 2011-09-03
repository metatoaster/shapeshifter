import re
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
        results = [k for k, v in self.frame.columns.iteritems() if v.get()]
        self.config['columns'] = results
        self.columns = results
        self.frame.destroy()
        self.frame = DataDisplayFrame(self)
        self.frame.pack(fill=BOTH, expand=1)


class DataDisplayFrame(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.config = AppConfig()
        self.pack()
        self.createWidgets()

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

        filename = tkFileDialog.asksaveasfilename(
            filetypes=formats,
            initialdir=self.config.get('cwd'),
        )

        if filename:
            self.saveoutput(filename)

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

    @property
    def parsers(self):
        return self.master.master.parsers

    def newCheckboxValues(self):
        result = {}
        for p in self.parsers:
            result.update(p)
        for i in result.keys():
            result[i] = IntVar()
        return result

    def createWidgets(self):

        self.columns = self.newCheckboxValues()
        keys = sorted(self.columns.keys())
        # XXX apply settings here
        for c in self.config.get('columns', []):
            if c in keys:
                self.columns[c].set(1)

        self.checkboxes = []
        for k in keys:
            c = Checkbutton(self,
                text=k,
                variable=self.columns[k],
                width='20',
                anchor=W,
            )
            c.pack()


class ColumnSelectFrame(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.config = AppConfig()
        self.pack()
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

    @property
    def filenames(self):
        return self.filenameframe.filenames.get(0, END)

    def dialogRun(self):
        self.parsers = []
        filenames = self.filenames
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
        if isinstance(filenames, basestring) and filenames[0] == '{':
            filenames = re.findall('\{(.*?)\}', filenames)

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
