import sqlite3
from datetime import datetime
from tkinter import *
from tkinter.ttk import *
from tkcalendar import Calendar
from backend import insertNewData, deleteSelectedData, visualAnalysis, queryData

connection = sqlite3.connect("data.db")
connection.execute("CREATE TABLE IF NOT EXISTS data(date text primary key, day text, mood integer, notes text)")

root = Tk()
root.geometry('750x500')
root.title('Mood Tracker App')

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

#Required info label
required_label=Label(root, text="*Fields with a star are required to be filled to save information.")
required_label.grid(row=0, sticky=W)

#Setting up general label
general_label = Label(root, text="")
general_label.grid(row=3, sticky=W)

#GUI BUTTON FUNCTIONS
def displayData():
    date_obj = datetime.strptime(cal.get_date(), "%m/%d/%y")
    formatted_date = date_obj.strftime("%Y-%m-%d")

    result = queryData(connection, formatted_date)
    T.delete(1.0, END)
    cb.delete(0, END)
    if result != None:
        T.insert(END, result['notes'])
        cb.insert(END, result['mood'])
        general_label.configure(text="Data fields updated successfully")
    elif result == None:
        general_label.configure(text="No data inputted for specified date")
    else:
        general_label.configure(text="Something went wrong. Check console")

def saveData():
    date_obj = datetime.strptime(cal.get_date(), "%m/%d/%y")
    formatted_date = date_obj.strftime("%Y-%m-%d")
    day_of_week = date_obj.strftime("%A")

    inputted_result = T.get("1.0", "end-1c")

    selected_mood = cb.get()
    if selected_mood == "":
        general_label.configure(text="Please select a valid mood")
    else:
        if insertNewData(connection, formatted_date, day_of_week, mood_var.get(), inputted_result):
            general_label.configure(text="Saved successfully")
        else:
            general_label.configure(text="Something went wrong. Check console")

def deleteData():
    date_obj = datetime.strptime(cal.get_date(), "%m/%d/%y")
    formatted_date = date_obj.strftime("%Y-%m-%d")

    def closeNewWindow():
        #close right away
        newWindow.destroy()
    
    def deleteFromDB():
        #first delete
        if deleteSelectedData(connection, formatted_date):
            T.delete(1.0, END)
            cb.delete(0, END)
            general_label.configure(text="Deleted successfully")
        else:
            general_label.configure(text="Something went wrong. Check console")
        #then close
        newWindow.destroy()

    #setting up new window
    newWindow = Toplevel(root)
    newWindow.title("Confirmation")
    newWindow.geometry('400x200')

    # Configure grid columns to center the label and buttons
    newWindow.grid_columnconfigure(0, weight=1)
    newWindow.grid_columnconfigure(1, weight=1)

    question_label = Label(newWindow, text="Are you sure? This action cannot be undone")
    question_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="n")  

    # Adding Yes and No buttons
    yes_button = Button(newWindow, text="Yes", command=deleteFromDB)
    no_button = Button(newWindow, text="No", command=closeNewWindow)

    yes_button.grid(row=1, column=0, pady=20, padx=20)  
    no_button.grid(row=1, column=1, pady=20, padx=20)  

def displayVisual():
    if not visualAnalysis(connection):
        general_label.configure(text="No data to be visualized")

#Calendar Frame
calendar_frame = LabelFrame(root, text="Calendar")
calendar_frame.grid(row=1, sticky=W)
cal = Calendar(calendar_frame, selectmode = 'day')
cal.grid(row=0)
Label(calendar_frame, text='Please select a date to display info: ').grid(row=1, sticky=W)
display_button = Button(calendar_frame, text='Display', command=displayData)
display_button.grid(row=1, column=1, sticky=W)

#Selection Frame
selection_frame = LabelFrame(root, text="Selection")
selection_frame.grid(row=2, sticky=W)

Label(selection_frame, text='*Mood').grid(row=0, sticky=W)
selection_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
mood_var = IntVar()
cb = Combobox(selection_frame, textvariable=mood_var)
cb['values'] = selection_values
cb.grid(row=1, sticky=W)

Label(selection_frame, text='Notes').grid(row=2, sticky=W)
T = Text(selection_frame, height=5, width=40, wrap=WORD)
T.grid(row=3, sticky=W)

save_button = Button(selection_frame, text='Save', command=saveData)
save_button.grid(row=4, sticky=W)

delete_button = Button(selection_frame, text='Delete', command=deleteData)
delete_button.grid(row=4, sticky=E)

#Display & Analysis Frame
display_selection_frame = LabelFrame(root, text="Dispay & Analysis")
display_selection_frame.grid(row=0, column=1, sticky=W)

display_trend_button = Button(display_selection_frame, text='Visual Trend & Analysis', command=displayVisual)
display_trend_button.grid(row=0, sticky=W)

displayData() #update with current date data upon application opening
root.mainloop()
connection.close()