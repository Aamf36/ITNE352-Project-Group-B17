import socket
import PySimpleGUI as PySimpleGUI

#step one : establishing the connection to the server 
csock= socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#exception handling for connection
try:
    csock.connect(("ip ", port))
except:
    PySimpleGUI.PopupError("couldn't connect to server")
    exit()

# sending username  
usern= input(" my username is: ")
csock.send(usern.encode("utf-8")) 

# recv from server 
data = csock.recv(2048)

def cwindow(title, layout):
    window = PySimpleGUI.Window(title, layout)
    return window
#step two:  prompt user to choose one of the options
while True:
    menu_layout =[
        [PySimpleGUI.Frame(" options:", [
            [PySimpleGUI.Text("Choose one of the following options : \n")],
            [PySimpleGUI.Text("1. Show arrived flights" )],
            [PySimpleGUI.Text("2. Show delayed flights" )],
            [PySimpleGUI.Text("3. Show all the flights coming from a specific city" )],
            [PySimpleGUI.Text("4. show details of a particular flight" )],
            [PySimpleGUI.Text("5. Quit" )]
        ])]

        option = input("Option: ")
        ]

    
    
    # send the chosen request to the server 
    csock.send((option).encode('utf-8'))

    # if client chooses invalid option 
    if option != "1" or option != "2" or option != "3" or option != "4" :
     print(" invalid ! please enter a valid option ")
     
    
     if option == "1":
        # decode the recv data from the server 
        data = csock.recv(2048).decode("utf-8")
        print("All the arrived flights: ", data)

    elif option == "2":
        # decode the recv data from the server 
        data = csock.recv(2048).decode("utf-8")
        print("All the delayed flights: ", data)

    elif option == "3":
        city_layout = [
            [PySimpleGUI.Text("Enter city ICAO:  ")],
            [PySimpleGUI.Button("Send")]
        ]
        # create window to allow user enter the ICAO code 
        city_code = print("All flights coming from a specific city: ", city_layout)
 
        # send ICAO to the server 
        csock.send(city_code.encode("utf-8"))
        # recv flight data
        flight_data = csock.recv(2048).decode("utf-8")

        print(f"All flights coming from {city_code.capitalize()}", flight_data)

    elif option == "4":
        flight_layout = [
            [PySimpleGUI.Text("Enter city ICAO: ")]
        ]
        # create window to allow user to enter the ICAO code 
        flight_code = print("Flights from a particular flight : ", flight_layout)
        # send icao to the server 
        csock.send(flight_code.encode('utf-8'))
        # recv data from the server
        flight_data = csock.recv(2048).decode("utf-8")
        print(f"Details of flight having this ICAO code: {flight_code.capitalize()}", flight_data)
# step three :closing the connection if user chooses quit
    elif option == "5":
        csock.send((usern + " is disconnected").encode("utf-8"))
        csock.close()
        break         


