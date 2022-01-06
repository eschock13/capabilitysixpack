from tkinter import *
from tkinter.messagebox import showwarning
from tkinter import font
from tkinter.filedialog import askopenfilename
from capabilityplots import Plot
from time import sleep
import pandas as pd
from framework_downloader import Framework_Downloader as fd

class Sixpack:
    def __init__(self):
        self.file_path = ''
        self.data = []

        self.file_opener = self.Open_File(self)
        if self.file_path == '':
            exit()

        self.file_reader = self.File_Reader(self)
        if self.data == []:
            exit()

        for spec in self.data:
            self.selected_plots = []
            self.usl = ''
            self.lsl = ''
            self.specnum = spec.pop(0)
            self.current_data = spec
            self.plot_selector = self.Select_Plots(self)
            if len(self.selected_plots) == 0:
                exit()
            self.Enter_Spec_Limits(self)
            self.plot_graphs(self.current_data)

    def plot_graphs(self, data):
        if len(self.selected_plots) == 6:
            myPlot = Plot(data, self.lsl, self.usl, sixpack=True)
        else:
            myPlot = Plot(data, self.lsl, self.usl)

        for plotType in self.selected_plots:
            myPlot.add_plot(plotType)
        myPlot.show()

    class Open_File:
        def __init__(self, parent):
            self.parent = parent
            self.file_path = ''

            self.root = Tk()
            self.root.title('Open or Download')

            #Main Header
            Label(self.root, text='Would You Like to Select or Download a File?', font=font.Font(size=15)).grid(row=1, column=1, columnspan=3)

            #Download Button
            self.downloadB = Button(self.root, text='DOWNLOAD FILE', command=self.download, width=15, height=2)
            self.downloadB.grid(row=2, column=1)

            #Select Button
            self.selectB = Button(self.root, text='SELECT FILE', command=self.select, width=15, height=2)
            self.selectB.grid(row=2, column=3)


            self.center_window()
            mainloop()
        
        def download(self):
            self.root.destroy()
            downloader = fd()
            self.file_path = downloader.file_path
            self.parent.file_path = self.file_path

        def select(self):
            self.root.destroy()
            self.root = Tk()
            self.root.withdraw()
            self.root.update()
            self.file_path = askopenfilename(filetypes=[("Excel Files", ".xlsx")])
            self.parent.file_path = self.file_path
            self.root.destroy()

        def center_window(self):
            """
            centers a tkinter window
            :param self.root: the main window or Toplevel window to center
            """
            self.root.update_idletasks()
            width = self.root.winfo_width()
            frm_width = self.root.winfo_rootx() - self.root.winfo_x()
            win_width = width + 2 * frm_width
            height = self.root.winfo_height()
            titlebar_height = self.root.winfo_rooty() - self.root.winfo_y()
            win_height = height + titlebar_height + frm_width
            x = self.root.winfo_screenwidth() // 2 - win_width // 2
            y = self.root.winfo_screenheight() // 2 - win_height // 2
            self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
            self.root.deiconify()

    class Select_Plots:
        def __init__(self, parent):
            self.parent = parent
            self.plotTypes = ['I_Chart', 'Capability Histogram', 'Moving Range Chart', 'Normal Probability Plot', 'Last 25 Observations', 'Capability Plot']
            self.spaces  = [' ', ' ', ' ', ' ', ' ', ' ']
            self.selected_plots = []

            self.root = Tk()
            self.root.title('Select Plots')
            self.font_size = font.Font(size=10)

            #Label Frame
            Label(self.root, text='Please Select Which Plots You Would Like To Create!', font=self.font_size).grid(row=1, column=1, sticky='nwes', columnspan=3)

            #ListBox Title Frame
            Label(self.root, text='Available', font=self.font_size).grid(row=2, column=1, sticky='nwes')
            Label(self.root, text='Selected', font=self.font_size).grid(row=2, column=3, sticky='nwes')

            #ListBox Frame
            original_items = StringVar(value=self.plotTypes)
            spaces = StringVar(value=self.spaces)
            self.origLB = Listbox(self.root, listvariable=original_items, font=self.font_size)
            self.plotLB = Listbox(self.root, listvariable=spaces, font=self.font_size)
            self.origLB.grid(row=3, column=1, sticky='nwes')
            self.plotLB.grid(row=3, column=3, sticky='nwes')

            #Button Frame
            Button(self.root, text='Submit', command = self.submit).grid(row=4, column=1, sticky='w')
            Button(self.root, text='Sixpack', command = self.sixpack, ).grid(row=4, column=2, sticky='nwes')
            Button(self.root, text='Cancel', command=exit).grid(row=4, column=3, sticky='e')

            self.origLB.bind('<<ListboxSelect>>', self.select_items)
            self.plotLB.bind('<<ListboxSelect>>', self.deselect_items)

            self.center_window()
            mainloop()
        
        def select_items(self, event):
            try:
                item_index = self.origLB.curselection()[0]
                item = self.origLB.get(item_index)
                if item != ' ':
                    self.origLB.delete(item_index)
                    self.origLB.insert(item_index, ' ')
                    self.plotLB.delete(item_index)
                    self.plotLB.insert(item_index, item)
                    sleep(.1)
            except IndexError:
                pass

        def deselect_items(self, event):
            try:
                item_index = self.plotLB.curselection()[0]
                item = self.plotLB.get(item_index)
                if item != ' ':
                    self.plotLB.delete(item_index)
                    self.plotLB.insert(item_index, ' ')
                    self.origLB.delete(item_index)
                    self.origLB.insert(item_index, item)
                    sleep(.1)
            except IndexError:
                pass

        def sixpack(self):
            self.parent.selected_plots = self.plotTypes
            self.root.destroy()

        def submit(self):
            self.selected_plots = [val for val in list(self.plotLB.get(0,6)) if val != ' ']
            if len(self.selected_plots) == 0:
                showwarning('Warning', 'You Must Select At Least One Plot')
            else:
                self.parent.selected_plots = self.selected_plots
                self.root.destroy()

        def center_window(self):
            """
            centers a tkinter window
            :param self.root: the main window or Toplevel window to center
            """
            self.root.update_idletasks()
            width = self.root.winfo_width()
            frm_width = self.root.winfo_rootx() - self.root.winfo_x()
            win_width = width + 2 * frm_width
            height = self.root.winfo_height()
            titlebar_height = self.root.winfo_rooty() - self.root.winfo_y()
            win_height = height + titlebar_height + frm_width
            x = self.root.winfo_screenwidth() // 2 - win_width // 2
            y = self.root.winfo_screenheight() // 2 - win_height // 2
            self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
            self.root.deiconify()

    class Enter_Spec_Limits:
        def __init__(self, parent):
            self.parent = parent
            self.specnum = self.parent.specnum
            self.lsl = ''
            self.usl = ''
            self.root = Tk()
            self.root.title('Spec Limits')

            #Main label
            Label(self.root, text='Please Enter The Limits For Spec ' + str(self.parent.specnum) + ' Below').grid(row=1, column=1, columnspan=3)

            #Label and Entry for LSL
            self.lvar = StringVar()
            Label(self.root, text='Lower Spec Limit:').grid(row=2, column=1)
            Entry(self.root, textvariable=self.lvar, width=5).grid(row=3,column=1, padx=5, sticky='nwes')

            #Label and Entry for USL
            self.uvar = StringVar()
            Label(self.root, text='Upper Spec Limit:').grid(row=2, column=3)
            Entry(self.root, textvariable=self.uvar, width=5).grid(row=3, column=3, padx=5, sticky='nwes')

            #FRAME 3 FOR ENTER AND QUIT
            Button(self.root, text='Enter', command=self.enter).grid(row=4, column=1, pady=5)
            Button(self.root, text='Exit', command=exit).grid(row=4, column=3, pady=5)

            self.root.bind('<Return>', self.enter_button)

            self.center_window()
            mainloop()

            if self.lsl == '' or self.usl == '':
                exit()

        def enter(self):
            try:
                self.lsl = float(self.lvar.get())
                self.usl = float(self.uvar.get())
                self.limits = [self.lsl, self.usl]
                if self.lsl > self.usl:
                    showwarning('Warning', 'The Lower Spec Limit Cannot Be Greater Than The Upper Spec Limit')
                else:
                    self.parent.usl = self.usl
                    self.parent.lsl = self.lsl
                    self.root.destroy()
            except ValueError:
                showwarning('Warning', 'Spec Limits Must Be Digits')

        def enter_button(self, e):
            try:
                self.lsl = float(self.lvar.get())
                self.usl = float(self.uvar.get())
                self.limits = [self.lsl, self.usl]
                if self.lsl > self.usl:
                    showwarning('Warning', 'The Lower Spec Limit Cannot Be Greater Than The Upper Spec Limit')
                else:
                    self.parent.usl = self.usl
                    self.parent.lsl = self.lsl
                    self.root.destroy()
            except ValueError:
                showwarning('Warning', 'Spec Limits Must Be Digits')

        def center_window(self):
            """
            centers a tkinter window
            :param self.root: the main window or Toplevel window to center
            """
            self.root.update_idletasks()
            width = self.root.winfo_width()
            frm_width = self.root.winfo_rootx() - self.root.winfo_x()
            win_width = width + 2 * frm_width
            height = self.root.winfo_height()
            titlebar_height = self.root.winfo_rooty() - self.root.winfo_y()
            win_height = height + titlebar_height + frm_width
            x = self.root.winfo_screenwidth() // 2 - win_width // 2
            y = self.root.winfo_screenheight() // 2 - win_height // 2
            self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
            self.root.deiconify()

    class File_Reader:
        def __init__(self, parent):
            self.parent = parent
            try:
                data = pd.read_excel(self.parent.file_path)
            except AssertionError:
                exit()

            self.parent.data = data.values.tolist()
