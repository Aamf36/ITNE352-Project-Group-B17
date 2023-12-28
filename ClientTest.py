import socket
import PySimpleGUI as PySimpleGUI

#theme for the windows
PySimpleGUI.theme("LightBlue6")

#step one : establishing the connection to the server 
csock= socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#exception handling for connection
try:
    csock.connect(('127.0.0.1', 66666))
except:
    PySimpleGUI.PopupError("Couldn't connect to server")
    exit()

# sending username  
username_layout = [
    [PySimpleGUI.Text("Please enter your username :", font=("Arial Bold", 12)), 
     PySimpleGUI.Input(key="-INPUT-", font=("Arial Bold", 12))],
    [PySimpleGUI.Submit(), 
     PySimpleGUI.Cancel()]
]
# create a window for username 
window = PySimpleGUI.Window("B17 ", username_layout)
event, uname = window.read()
uname= uname[0]
window.close()

# sending the username to server
csock.send(uname.encode("utf-8")) 

#create windows for later use 
def window_creation(title,data):
    window = PySimpleGUI.Window("B17", layout, resizable=True)
    event, value = window.read()
    window.close()

#step two:  prompt user to choose one of the options
while True:
    options_layout =[
            [PySimpleGUI.Text("Choose one of the following options : ")],
            [PySimpleGUI.Text("1. Show arrived flights" )],
            [PySimpleGUI.Text("2. Show delayed flights" )],
            [PySimpleGUI.Text("3. Show all the flights coming from a specific city" )],
            [PySimpleGUI.Text("4. Show details of a particular flight" )],
            [PySimpleGUI.Text("5. Quit" )]
            [PySimpleGUI.Input()],
            [PySimpleGUI.Button("submit")]
        ]
    #create window for options
    window= PySimpleGUI.Window("B17",options_layout,resizable=True)
    event, option = window.read()
    option= option[0]
    window.close()

    # send the chosen request to the server 
    csock.send((option).encode("utf-8"))

    # if client chooses invalid option 
    if option != "1" or option != "2" or option != "3" or option != "4" :
     print(" Invalid ! please enter a valid option ")
     
    #if client chooses one of the valid options
    if option == "1":
        # decode the recv data from the server 
        data = csock.recv(20480).decode("utf-8")
        layout= [
            [PySimpleGUI.Text("All the arrived flights: ",font="Arial")],
            [PySimpleGUI.Column([[PySimpleGUI.Text(data)]],scrollable=True, vertical_scroll_only=True)]
        ]
        #window creation
        window_creation("B17",layout)

    elif option == "2":
        # decode the recv data from the server 
        data = csock.recv(20480).decode("utf-8")
        layout= [
            [PySimpleGUI.Text("All the delayed flights: ",font="Arial")],
            [PySimpleGUI.Column([[PySimpleGUI.Text(data)]],scrollable=True, vertical_scroll_only=True)]
        ]
        #window creation
        window_creation("B17",layout)

    elif option == "3":
        #prompt user to enter icao code 
        layout = [
            [PySimpleGUI.Text("Enter city ICAO:  ",font=("Arial",10))],
            [PySimpleGUI.Input(key="-INPUT-")],
            [PySimpleGUI.Button("Send")]
        ]
        # window creation 
        window = PySimpleGUI.Window("B17",layout,resizable=True)
        event,city= window.read()
        city=city[0]
    
        # send ICAO to the server 
        csock.send(city.encode("utf-8"))
        # recv flight data
        flight_data = csock.recv(20480).decode("utf-8")
        flight_layout = [
            [PySimpleGUI.Text("All the flights coming from "+city.capitalize())],
            [PySimpleGUI.Column([[PySimpleGUI.Text(flight_data)]],scrollable=True, vertical_scroll_only=True)]]
        #window creation 
        window_creation("B17",flight_layout)

    elif option == "4":
        flight_layout = [
            [PySimpleGUI.Text("Enter city ICAO or flight number: ",font=("Arial",12))],
            [PySimpleGUI.Input()],
            [PySimpleGUI.Button("send")]]
        
        # create window  
        window = PySimpleGUI.Window("B17", flight_layout, resizable=True)
        event, flight = window.read()
        flight= flight[0]
        window.close()

        # send icao to the server 
        csock.send(flight.encode("utf-8"))
        # recv data from the server
        flight_data = csock.recv(20480).decode("utf-8")
        layout=[ 
            [PySimpleGUI.Text(f"Details of flight with this city ICAO/flight number: {flight.capitalize()}")]]
        #window creation 
        window_creation("B17",layout)
# step three :closing the connection if user chooses quit 
    elif option == "5":
        csock.send((uname + " is disconnected").encode("utf-8"))
        csock.close()
        break         


