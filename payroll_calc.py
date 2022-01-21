import tkinter as tk  # import tkinter
import tkinter.messagebox as msgbox  # import tkinter.messagebox
import datetime # import datetime
import json # import json
import base64 # import base64

class Payroll:
    frame: tk.Frame # create main window variable
    data = [] # create data variable
    history: tk.Toplevel = None # create history window variable

    def __init__(self, frame: tk.Frame): # constructor
        self.frame = frame # set main window variable
        self.retrieve_from_file() # retrieve data from file

    def time_cal(self, hours: float): # calculate time
        if hours <= 240: # if less than 4 hours or no overtime
            return [hours, False]
        return [hours - 240, True] # if overtime

    def rate_cal(self, hours, rate: float): # calculate rate
        if hours[1]: # if overtime
            othours = hours[0] # get overtime hours
            otpay = othours * (rate * 1.5) # calculate overtime pay
            return otpay # return overtime pay

        return None # if not overtime

    def write_to_file(self):
        data_str = json.dumps(self.data) # convert data to string
        data_sec = base64.b64encode(data_str.encode()) # encode data to base64
        try:
            with open("payroll.txt", "w") as f: # overwrite file
                f.write(data_sec.decode()) # write data to file
                f.close() # close file
        except:
            pass # if error occurs, ignore it
    
    def retrieve_from_file(self):
        try:
            with open("payroll.txt", "r") as f: # open file
                data_str = f.read() # read data
                data_str = base64.b64decode(data_str).decode() # decode data
                self.data = json.loads(data_str) # convert data to list
                f.close() # close file
        except: # if file not found
            pass    # do nothing

    def delete_selected(self):
        i = self.history_list.curselection()[0] # get selected index
        del self.data[i] # delete data from list
        self.history_list.delete(i) # delete selected item from listbox

        # save changes to file
        try:
            with open("payroll.txt", "w") as f: # overwrite file with empty string
                f.write(json.dumps(self.data)) # write data to file
                f.close() # close file
        except:
            pass # do nothing if file not found

        if len(self.data) == 0:
            # destroy history window if no data
            self.history.destroy()

    def view_selected(self):
        i = self.history_list.curselection()[0] # get selected index
        hours = self.data[i][1] # get hours
        rate = self.data[i][2] # get rate
        name = self.data[i][3] # get name
        self.calculate(name, hours, rate, False) # calculate and show result

    def create_history(self):
        if len(self.data) > 0:
            # if data is not empty

            if self.history:
                # destroy history window if history window is already open
                self.history.destroy()
            
            # create history window
            self.history = tk.Toplevel(self.frame) # create toplevel window
            self.history.title('Payroll History') # set title
            self.history.geometry('400x400') # set window size
            self.history.resizable(False, False) # disable resizing

            # create menu bar
            menu = tk.Menu(self.history)
            self.history.config(menu=menu)

            # create actions in menu
            menu.add_command(label='Delete', command=self.delete_selected) # add delete label and command
            menu.add_command(label='View', command=self.view_selected) # add view label and command

            scrollbar = tk.Scrollbar(self.history)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y) # create and pack scrollbar

            self.history_list = None # reset history list
            self.history_list = tk.Listbox(self.history,width=400, height=20, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE) # create listbox
            for i in range(len(self.data)):
                self.history_list.insert(i, f'{self.data[i][3]:<30}  {self.data[i][0]:>30}') # insert name date from data to list
            self.history_list.pack(side=tk.LEFT, fill=tk.BOTH) # pack listbox
            scrollbar.config(command=self.history_list.yview) # set scrollbar to listbox

        else:
            # show error message if no data
            msgbox.showerror(title='Error', message='Empty data')

    def clear(self):
        self.data = [] # clear data

        # save changes to file 
        try:
            with open("payroll.txt", "w") as f: # overwrite file with empty string
                f.write(json.dumps(self.data)) # write data to file
                f.close() # close file
        except:
            pass # do nothing if file not found

        msgbox.showinfo(title='Clear', message='Data cleared') # show messagebox
        
        if self.history:
            # destroy history window if history window is open
            self.history.destroy()

    def calculate(self, name, hours, rate, save: bool = False):
        date = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S") # get current date
        hours = float(hours) # convert hours to float
        rate = float(rate) # convert rate to float

        if self.rate_cal(self.time_cal(hours), rate)==None:
            # if not overtime
            # construct message for non-overtime
            message = f"{'Payroll Information':<75}\n\n" \
                f"Employee Name:  {name}\n" \
                f"Pay rate:             ₱{rate:7.2f}\n" \
                f"Regular Hours:  {hours:2.0f}\n" \
                f"Overtime Hours: 0\n" \
                f"Regular Pay:      ₱{hours*rate:7.2f}\n" \
                f"Total pay:           ₱{hours*rate:7.2f}"
            
            # show messagebox
            msgbox.showinfo(title='Payroll Information', message=message)
        else:
            # if overtime
            otpay = self.rate_cal(self.time_cal(hours), rate) # calculate overtime pay
            # construct the message for messagebox
            message = f"{'Payroll Information':<75}\n\n" \
                f"Employee Name:  {name}\n" \
                f"Pay rate:             ₱{rate:7.2f}\n" \
                f"Regular Hours:  {hours:2.0f}\n" \
                f"Regular Pay:      ₱{hours*rate:7.2f}\n" \
                f"Overtime pay:    ₱{otpay:7.2f}\n" \
                f"Total pay:           ₱{(hours*rate) + otpay:7.2f}"
            
            # show messagebox
            msgbox.showinfo(title='Payroll Information', message=message)

        if save:
            # if save is true
            self.data.append([date, hours, rate, name]) # add data to list
            self.write_to_file()

    def calculate_last(self):
        if len(self.data) > 0:
            # if data is not empty
            self.calculate(self.data[-1][3],self.data[-1][1], self.data[-1][2], False)
        else:
            # show error message if no data
            msgbox.showerror(title='Error', message='Empty data')

class Application(tk.Frame):  # Class that inherits from tk.Frame
    def __init__(self, master=None):  # constructor
        super().__init__(master)  # call the parent class's constructor

        self.master = master  # master is the root window
        self.pack()  # pack() is a method of the Frame 
        self.master.title("Payroll Calculator")  # Edit title of window
        self.master.geometry("500x300")  # set width and height of window
        # self.master.resizable(width=False, height=False) # disable resizing of window
        self.payroll = Payroll(self)  # create payroll object and pass self as parameter or as a parent tkinter Frame
        self.create_widgets()  # call the method to create the widgets

    def create_widgets(self):  # method to create widgets

         # Menu Bar
        menu = tk.Menu(self.master) # create menu container
        self.master.config(menu=menu) # attach menu to root window

        # Menu Buttons
        menu.add_command(label="History", command=self.payroll.create_history)  # button to view history
        menu.add_command(label="Clear", command=self.payroll.clear)  # button to clear data
        menu.add_command(label="Last Entry", command=self.payroll.calculate_last)  # button to view last entry
    
        # name label
        self.name_label = tk.Label(self, text="What is your name?", width=35, justify="left") # create label
        self.name_label.grid(row=0, column=0, pady=20) # place label to row 0, column 0

        # name textbox
        self.name_entry = tk.Entry(self, width=20) # name text input
        self.name_entry.grid(row=0, column=1) # place text input to row 0, column 1

        # hours label
        hours_label = tk.Label(self, text="How many hours did you work?", width=35, justify="left") # create label
        hours_label.grid(row=1, column=0, pady=20) # place label to row 1, column 0

        # hours textbox
        self.hours_entry = tk.Entry(self, width=20) # create hours textbox
        self.hours_entry.grid(row=1, column=1) # place textbox to row 1, column 1
        self.hours_entry.focus() # set cursor focus to hours textbox

        # rate label
        rate_label = tk.Label(self, text="What is your hourly rate?", width=35, justify="left") # create label
        rate_label.grid(row=2, column=0, pady=20) # place label to row 2, column 0

        # rate textbox
        self.rate_entry = tk.Entry(self, width=20) # rate text input
        self.rate_entry.grid(row=2, column=1) # place text input to row 2, column 1

        # calculate button
        calculate_button = tk.Button(self, text="Calculate", command=self.calculate) # create button
        calculate_button.grid(row=3, column=0, columnspan=2, pady=30) # place button to row 3, column 0, columnspan 2

    def exit(self):  # method to exit the program
        self.master.destroy()  # destroy the root window

    def calculate(self):  # method to get the values from the entry boxes and show the result
        # get the hours from the entry widget
        try:
            hours = float(self.hours_entry.get())  # get the hours from the entry widget
            # if hours is less than 240 or greater than 320, show msgbox error and return
            if hours < 240 or hours > 320:
                msgbox.showerror(title="Invalid Hours Input", message="Hours must be at least 240 hours per month")
                self.hours_entry.delete(0, "end") # delete the text in the hours textbox
                return
        except ValueError:  # if hours is not a number, show msgbox error and return
            msgbox.showerror(title="Invalid Hours Input", message="Please enter a valid hours number")
            self.hours_entry.delete(0, "end") # delete the text in the hours textbox
            return

        # get the rate from the entry widget
        try:
            rate = float(self.rate_entry.get())  # get the rate from the entry widget
            if rate < 67 or rate > 180:
                msgbox.showerror(title="Invalid Rate Input", message="Pay rate must be at least ₱67.00 and less than ₱180.00")
                self.rate_entry.delete(0, "end") # delete the text in the rate textbox
                return
        except ValueError:  # if rate is not a number, show msgbox error and return
            msgbox.showerror(title="Invalid Rate Input",  message="Please enter a valid rate")
            self.rate_entry.delete(0, "end") # delete the text in the rate textbox
            return
        
        # get the name from the entry widget
        try:
            name = self.name_entry.get()  # get the name from the entry widget
            if name == "":
                msgbox.showerror(title="Invalid Name Input", message="Please enter a valid name")
                self.name_entry.delete(0, "end") # delete the text in the name textbox
                return
        except ValueError:  # if name is not a string, show msgbox error and return
            msgbox.showerror(title="Invalid Name Input", message="Please enter a valid name")
            self.name_entry.delete(0, "end") # delete the text in the name textbox
            return

        self.payroll.calculate(name, hours, rate, True)  # call the calculate method of the payroll object
        self.hours_entry.delete(0, "end") # delete the text in the hours textbox
        self.rate_entry.delete(0, "end") # delete the text in the rate textbox


root = tk.Tk()  # create a root window
app = Application(master=root)  # create an instance of the Application class
app.mainloop()  # run the TK Window Frame loop
