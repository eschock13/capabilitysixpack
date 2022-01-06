from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.action_chains import ActionChains
import os.path
import os
from datetime import datetime
import glob
from pathlib import Path
from tkinter import *
from tkinter.messagebox import showwarning
import csv
import pandas as pd

class Driver:
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(executable_path = r'K:\QUALITY\Minitab mimic\Chromedriver\chromedriver.exe',options = options)
        self.driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': str(os.path.join(Path.home(), "Downloads"))}}
        self.driver.execute("send_command", params)
        self.driver.get("http://framework/PartsView?modulename=Zeiss")

    #Checks to see if there is an element at an xpath so the program doesn't error out
    def check_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    #gets the text
    def gettext(self, xpath):
        attempts = 0
        ignored_exceptions=(StaleElementReferenceException)
        while attempts < 2:
            try:
                element = WebDriverWait(self.driver, 5).until(presence_of_element_located((By.XPATH, xpath))).text
                break
            except ignored_exceptions:
                pass
            finally:
                attempts += 1
        return element

    def wait_click(self, xpath):
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

    def xpath_click(self, xpath):
        self.driver.find_element_by_xpath(xpath).click()

    def scrollclick(self, xpath):
        target = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
        actions = ActionChains(self.driver)
        actions.move_to_element(target)
        actions.perform()
        target.click()

    def reset(self):
        self.driver.get("http://framework/PartsView?modulename=Zeiss")

class Framework_Downloader(Driver):
    def __init__(self):
        #Initializes the parent class Driver
        super().__init__()
        #Initializing All The Variables I Will Use:
        self.machine = ''
        self.program = ''
        self.file_path = ''
        self.get_machines()
        self.check_machines()
        #GUI Loop
        while True:
            self.back = False
            self.Machine_Select_GUI(self)
            self.get_programs()
            while True:
                self.back = False
                self.Program_Select_GUI(self)
                if self.back == True:
                    self.reset()
                    break
                else:
                    self.download()
                    self.FileEditor(self)
                    if self.back == False:
                        break
            if self.back == False:
                break

    #gets machine list
    def get_machines(self):
        self.machinelist = []
        self.machine_xpath_list = []
        num_machines = 1
        while True:
            machine_xpath = "/html/body/div[2]/div/div[1]/div/div[2]/a[" + str(num_machines) + "]"
            if self.check_exists_by_xpath(machine_xpath) == True:
                self.machinelist.append(self.gettext(machine_xpath))
                self.machine_xpath_list.append(machine_xpath)
                num_machines += 1
            else:
                self.num_machines = num_machines - 1
                break

    #Checks the machines from getmachines to see if there are values behind them
    def check_machines(self):
        for i in self.machine_xpath_list.copy():
            self.wait_click(i)
            testxpath = '/html/body/div[2]/div/div[2]/div/div[1]/table/tbody/tr[1]'
            if self.check_exists_by_xpath(testxpath) == False:
                del self.machinelist[self.machine_xpath_list.index(i)]
                self.machine_xpath_list.remove(i)

    #gets program list
    def get_programs(self):
        self.program_list = []
        self.program_xpath_list = []
        try:
            self.scrollclick(self.machine_xpath_list[self.machinelist.index(self.machine)])
        except ValueError:
            exit()
        # except ElementClickInterceptedException:
        #     self.scrollclick(self.machine_xpath_list[self.machinelist.index(self.machine)])

        num_programs = 1

        while True:
            program_xpath = "/html/body/div[2]/div/div[2]/div/div[1]/table/tbody/tr[" + str(num_programs) + "]/td[2]"
            if self.check_exists_by_xpath(program_xpath) == True:
                text = self.gettext(program_xpath)
                self.program_list.append(text)
                self.program_xpath_list.append(program_xpath)
                num_programs += 1
            else:
                break

    # Downloads the data from the selected program
    def download(self):
        try:
            programpath = self.program_xpath_list[self.program_list.index(self.program)]
        except ValueError:
            exit()
        #Gets the exact time before and after the download so the program can later figure out which file it downloaded
        before = datetime.now().strftime('%H%M.%S')
        self.scrollclick(programpath.replace('/td[2]','/td[4]/a'))
        after = datetime.now().strftime("%H%M.%S")


        while True:
            try:
                files = glob.glob(str(os.path.join(Path.home(), "Downloads")) + '\*csv')
                self.file_path = max(files, key=os.path.getctime).replace("\\", "/")
                if float(before) <= float(self.file_path[-11:-4]) <= float(after):
                    break
            except ValueError:
                pass

    #the class that holds the GUI for selecting a machine
    class Machine_Select_GUI:
        def __init__(self, parent):
            self.parent = parent
            #Creates the main window where the frames are located
            self.root = Tk()
            self.title_font = ('calibre', 15, 'normal')
            self.label_font = ('calibre', 12, 'normal')
            self.radio_button_font = ('calibre', 11, 'bold')
            self.button_font = ('calibre', 10, 'normal')
            self.root.title('Machine Select')
            self.selection = StringVar(value = '1')
            if len(self.parent.machinelist) >= 5:
                self.num_cols = 5
            else:
                self.num_cols = len(self.parent.machinelist)

            #The following frame contains the intro text
            Label(self.root, text='Welcome To The Framework Downloader!', padx=5, pady=10, font=self.title_font).grid(row=1, column=1, columnspan=self.num_cols)

            #textFrame2 contains a prompt for the user to select a machine
            Label(self.root, text='Please Select Which Machine You Would Like To Pull Data From!', padx=5, font=self.label_font).grid(row=2, column=1, columnspan=self.num_cols)
            
            #buttonFrame1 and buttonFrame2 contains a set of radio buttons that correlate to the machines that have data
            num_machines = 1
            for machine in self.parent.machinelist:
                if num_machines <= 6:
                    Radiobutton(self.root,
                            text = machine,
                            variable = self.selection,
                            value = machine,
                            font=self.radio_button_font,
                            padx=10).grid(row=3, column=num_machines)
                    num_machines = num_machines + 1
                else:
                    Radiobutton(self.root,
                            text = machine,
                            variable = self.selection,
                            value = machine,
                            font=self.radio_button_font,
                            padx=5).grid(row=4, column=(num_machines-5))
                    num_machines = num_machines + 1

            #buttonFrame3 contains the Confirm and Cancel Buttons
            Button(self.root,
                text='Confirm',
                command=self.select_machine,
                padx=10,
                font=self.button_font,
                width=15).grid(row=4, column=1, sticky='w')

            Button(self.root,
                text='Cancel',
                command=exit,
                padx=10,
                font=self.button_font,
                width=15).grid(row=4, column=self.num_cols, sticky='e')

            mainloop()

        def select_machine(self):
            if self.selection.get() != '1':
                self.parent.machine = self.selection.get()
                self.root.destroy()
            else:
                showwarning('Warning','Please Select A Machine!')

    #The class that holds the GUI for selecting a program
    class Program_Select_GUI:
        def __init__(self, parent):
            self.parent = parent
            #Generates a new window where the frames will be inserted
            self.root = Tk()
            self.label_font = ('calibre', 13, 'normal')
            self.listbox_font = ('calibre', 11, 'normal')
            #self.root.geometry('300x500+25+75')
            self.root.title('Program Select')
            self.scrollbar = Scrollbar(self.root, orient='vertical')

            #Prompts the user to select a program
            Label(self.root, text='Please Select The Program You Wish To Get Data From!', padx=5, font=self.label_font).grid(row=1, column=1, columnspan=3)

            #Listbox of all possible programs
            self.programsLB = Listbox(self.root, font=('calibre', 11, 'normal'), height=30, width=40, yscrollcommand=self.yscroll1)
            self.fill_listbox(self.parent.program_list)
            self.programsLB.grid(row=2,column=2)

            #Listbox Search Bar
            self.search_str = StringVar()
            self.search_bar = Entry(self.root, textvariable=self.search_str, font=('calibre', 11, 'bold'))
            self.search_bar.grid(row=3, column=2, sticky='nwes')
            

            #Confirm, Cancel and Back
            Button(self.root, text='Back', command=self.back, padx=10, width=13).grid(row=4, column=1)
            Button(self.root, text='Confirm', command=self.select_program, width=13).grid(row=4, column=2)
            Button(self.root, text='Cancel', command=exit, padx=10, width=13).grid(row=4, column=3)
            
            self.scrollbar.config(command=self.yview)
            self.scrollbar.grid(row=2, column=3, sticky='nsw')
            self.search_bar.bind("<KeyRelease>", self.search_programs)
            self.programsLB.bind("<<ListboxSelect>>", self.click)

            mainloop()

        def select_program(self):
            # for i in self.programsLB.curselection():
            #     program = self.programsLB.get(i)
            program = self.search_str.get()
            if program in self.parent.program_list:
                self.parent.program = program
                self.root.destroy()
            else:
                showwarning('Warning','Please Select A Program!')

        def yscroll1(self, *args):
            self.scrollbar.set(*args)

        def yview(self, *args):
            self.programsLB.yview(*args)

        def search_programs(self, event):
            
            sstr=self.search_str.get()
            self.programsLB.delete(0,END)
            #If filter removed show all data
            if sstr=="":
                self.fill_listbox(self.parent.program_list) 
                return
        
            filtered_data=list()
            for item in self.parent.program_list:
                if item.find(sstr)>=0:
                    filtered_data.append(item)
        
            self.fill_listbox(filtered_data)   

        def fill_listbox(self, ld):
            for item in ld:
                self.programsLB.insert(END, item)

        def click(self, event):
            try:
                self.search_bar.delete(0,END)
                for i in self.programsLB.curselection():
                    program = self.programsLB.get(i)
                self.search_bar.insert(0, program)
            except UnboundLocalError:
                pass

        def back(self):
            self.root.destroy()
            self.parent.back = True

    class FileEditor:
        def __init__(self, parent):
            self.parent = parent
            while True:
                try:
                    self.file = open(self.parent.file_path, 'r')
                    break
                except PermissionError:
                    pass
            self.keep_dates = []
            self.keep_specs = []
            self.data = [x for x in list(csv.reader(self.file)) if x != []]
            self.dates = self.data[0][1:].copy()
            self.specs = [line[0] for line in self.data][1:]
            while True:
                self.back = False
                self.DATE_GUI(self)
                if self.back == True:
                    self.parent.back = True
                    self.file.close()
                    os.remove(self.parent.file_path)
                    break
                else:
                    if len(self.keep_dates) == 0:
                        exit()
                    self.SPEC_GUI(self)
                    if self.back == True:
                        pass
                    else:
                        if len(self.keep_specs) == 0:
                            exit()
                        else:
                            self.delete_specs()
                            self.delete_dates()
                            self.write_file()
                            self.parent.back = False
                            break

        def delete_specs(self):
            newData = []
            for spec in self.keep_specs:
                index = self.specs.index(spec) + 1
                newData.append(self.data[index])
            self.data = newData

        def delete_dates(self):
            newData = [self.keep_dates]
            for line in self.data:
                newLine = [line[0]]
                for date in self.keep_dates:
                    index = self.dates.index(date) + 1
                    newLine.append(line[index])
                newData.append(newLine)
            newData[0].insert(0, 'SpecNo')
            self.data = newData

        def write_file(self):
            new_file_path = self.parent.file_path.replace('.csv', '.xlsx')
            data = pd.DataFrame(self.data[1:], columns=self.data[0])
            data.to_excel(new_file_path, index=False)
            self.file.close()
            os.remove(self.parent.file_path)
            self.parent.file_path = new_file_path

        class DATE_GUI:
            def __init__(self, fileEditor):
                self.fileEditor = fileEditor
                self.dates = self.fileEditor.dates
                self.root = Tk()
                self.root.title('Select Dates')
                if len(self.dates) < 40:
                    self.listbox_height = len(self.dates)
                else:
                    self.listbox_height = 40

                self.header_font = ('calibre', 13, 'bold')
                self.label_font = ('calibre', 11, 'bold')
                self.listbox_font = ('calibre', 10, 'normal')
                self.radio_button_font = ('calibre', 8, 'normal')
                
                self.scrollbar = Scrollbar(self.root, orient='vertical')
                #MAIN LABEL
                Label(self.root, text='Please Select the Dates You Wish to Pull.', font=self.header_font).grid(row=1, column=1, columnspan=6)

                #FIRST LISTBOX LABEL
                Label(self.root, text='Available', font=self.label_font).grid(row=2, column=2)
                #SECOND LISTBOX LABEL
                Label(self.root, text='Selected', font=self.label_font).grid(row=2, column=5)

                #LISTBOX CONTAINGING AVAILABLE DATES
                available = StringVar(value=self.dates)
                self.available_dates = Listbox(self.root, 
                                    listvariable=available,
                                    height=self.listbox_height,
                                    width=30,
                                    yscrollcommand=self.yscroll1,
                                    font=self.listbox_font)

                self.available_dates.grid(row=3, column=1, columnspan=3, sticky='nwes')

                #LISTBOX CONTAINING BLANKS THEN SELECTED DATES  
                blanks = StringVar(value=[' ' for _ in range(1, len(self.dates) + 1)])
                self.selected_dates = Listbox(self.root,
                                    listvariable=blanks,
                                    height=self.listbox_height,
                                    width=30,
                                    yscrollcommand=self.yscroll2,
                                    font=self.listbox_font)

                self.selected_dates.grid(row=3, column=4, columnspan=3, sticky='nwes')

                #BACK BUTTON
                Button(self.root, text='Back', command=self.back, width=10).grid(row=4, column=1)
                #ENTER BUTTON
                Button(self.root, text='Confirm', command=self.enter, width=10).grid(row=4, column=3)

                #ALL DATES BUTTON
                Button(self.root, text='All Dates', command=self.all_dates, width=10).grid(row=4, column=4)
                #CANCEL BUTTON
                Button(self.root, text='Cancel', command=exit, width=10).grid(row=4, column=6)

                self.available_dates.bind("<<ListboxSelect>>", self.select_items)
                self.selected_dates.bind("<<ListboxSelect>>", self.deselect_items)

                self.scrollbar.config(command=self.yview)
                self.scrollbar.grid(row=3, column=7, sticky='ns')

                mainloop()

            def select_items(self, event):
                try:
                    item_index = self.available_dates.curselection()[0]
                    item = self.available_dates.get(item_index)
                    if item != ' ':
                        self.available_dates.delete(item_index)
                        self.available_dates.insert(item_index, ' ')
                        self.selected_dates.delete(item_index)
                        self.selected_dates.insert(item_index, item)
                except IndexError:
                    pass

            def deselect_items(self, event):
                try:
                    item_index = self.selected_dates.curselection()[0]
                    item = self.selected_dates.get(item_index)
                    if item != ' ':
                        self.selected_dates.delete(item_index)
                        self.selected_dates.insert(item_index, ' ')
                        self.available_dates.delete(item_index)
                        self.available_dates.insert(item_index, item)
                except IndexError:
                    pass

            def enter(self):
                self.fileEditor.keep_dates = [val for val in list(self.selected_dates.get(0, END)) if val != ' ']
                if len(self.fileEditor.keep_dates) == 0:
                    showwarning('Warning', 'You Must Select At Least One Date')
                else:
                    self.root.destroy()

            def back(self):
                self.root.destroy()
                self.fileEditor.back = True

            def all_dates(self):
                self.fileEditor.keep_dates = self.dates
                self.root.destroy()

            def yscroll1(self, *args):
                if self.selected_dates.yview() != self.available_dates.yview():
                    self.selected_dates.yview_moveto(args[0])
                self.scrollbar.set(*args)

            def yscroll2(self, *args):
                if self.available_dates.yview() != self.selected_dates.yview():
                    self.available_dates.yview_moveto(args[0])
                self.scrollbar.set(*args)

            def yview(self, *args):
                self.available_dates.yview(*args)
                self.selected_dates.yview(*args)

        class SPEC_GUI:
            def __init__(self, fileEditor):
                self.fileEditor = fileEditor
                self.specs = self.fileEditor.specs
                
                self.root = Tk()
                self.root.title('Select Specs')
                self.header_font = ('calibre', 13, 'bold')
                self.label_font = ('calibre', 11, 'bold')
                self.listbox_font = ('calibre', 10, 'normal')
                if len(self.specs) < 40:
                    self.listbox_height = len(self.specs)
                else:
                    self.listbox_height = 40

                self.scrollbar = Scrollbar(self.root, orient='vertical')
                #MAIN LABEL
                Label(self.root, text='Please Select the Specs You Wish to Pull.', font=self.header_font).grid(row=1, column=1, columnspan=6)

                #FIRST LISTBOX LABEL
                Label(self.root, text='Available', font=self.label_font).grid(row=2, column=2)
                #SECOND LISTBOX LABEL
                Label(self.root, text='Selected', font=self.label_font).grid(row=2, column=5)

                #LISTBOX CONTAINGING AVAILABLE SPECS
                available = StringVar(value=self.specs)

                self.available_specs = Listbox(self.root,
                                    listvariable=available,
                                    height=self.listbox_height,
                                    width=30,
                                    yscrollcommand=self.yscroll1,
                                    font=self.listbox_font)

                self.available_specs.grid(row=3, column=1, columnspan=3, sticky='nwes')

                #LISTBOX CONTAINING BLANKS THEN SELECTED SPECS
                blanks = StringVar(value=[' ' for _ in range(len(self.specs))])
                self.selected_specs = Listbox(self.root,
                                    listvariable=blanks,
                                    height=self.listbox_height,
                                    width=30,
                                    yscrollcommand=self.yscroll2,
                                    font=self.listbox_font)

                self.selected_specs.grid(row=3, column=4, columnspan=3, sticky='nwes')

                #BACK BUTTON
                Button(self.root, text='Back', command=self.back, width=13).grid(row=4, column=1)
                #ENTER BUTTON
                Button(self.root, text='Confirm', command=self.enter, width=13).grid(row=4, column=3)
                #ALL SPECS BUTTON
                Button(self.root, text='All Specs', command=self.all_specs, width=13).grid(row=4, column=4)
                #CANCEL BUTTON
                Button(self.root, text='Cancel', command=exit, width=13).grid(row=4, column=6)


                self.available_specs.bind("<<ListboxSelect>>", self.select_items)
                self.selected_specs.bind("<<ListboxSelect>>", self.deselect_items)

                self.scrollbar.config(command=self.yview)
                self.scrollbar.grid(row=3, column=7, sticky='ns')

                mainloop()

            def select_items(self, event):
                try:
                    item_index = self.available_specs.curselection()[0]
                    item = self.available_specs.get(item_index)
                    if item != ' ':
                        self.available_specs.delete(item_index)
                        self.available_specs.insert(item_index, ' ')
                        self.selected_specs.delete(item_index)
                        self.selected_specs.insert(item_index, item)
                except IndexError:
                    pass

            def deselect_items(self, event):
                try:
                    item_index = self.selected_specs.curselection()[0]
                    item = self.selected_specs.get(item_index)
                    if item != ' ':
                        self.selected_specs.delete(item_index)
                        self.selected_specs.insert(item_index, ' ')
                        self.available_specs.delete(item_index)
                        self.available_specs.insert(item_index, item)
                except IndexError:
                    pass

            def enter(self):
                self.fileEditor.keep_specs = [val for val in self.selected_specs.get(0, END) if val != ' ']
                # self.fileEditor.specs = [val for val in list(self.selected_specs.get(0, len(self.specs)+1)) if val != ' ']
                if len(self.fileEditor.keep_specs) == 0:
                    showwarning('Warning', 'You Must Select At Least One Spec')
                else:
                    self.root.destroy()

            def all_specs(self):
                self.fileEditor.keep_specs = self.specs
                self.root.destroy()

            def back(self):
                self.root.destroy()
                self.fileEditor.back = True

            def yscroll1(self, *args):
                if self.selected_specs.yview() != self.available_specs.yview():
                    self.selected_specs.yview_moveto(args[0])
                self.scrollbar.set(*args)

            def yscroll2(self, *args):
                if self.available_specs.yview() != self.selected_specs.yview():
                    self.available_specs.yview_moveto(args[0])
                self.scrollbar.set(*args)

            def yview(self, *args):
                self.available_specs.yview(*args)
                self.selected_specs.yview(*args)

#fd = Framework_Downloader()