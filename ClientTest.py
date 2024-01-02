#Necessary Modules are imported
import socket
import PySimpleGUI as psg
import signal
import sys

#Theme for the PySimpleGUI windows
psg.theme('TealMono')

#Functions
#Creation Function: To create a PySimpleGUI window with a specific title & layout
def Creation(title, layout):
    window= psg.Window(title, layout, resizable=True)
    return window

#ShowF Function: To display data in the PySimpleGUI window
def ShowF(title, data):
    layout = [
        [psg.Text("*"*10 + title + "*"*10, font=('Arial',12, 'bold'))],
        [psg.Column([[psg.Text(data, font=('Arial',10))]], scrollable=True)],
        [psg.Button('OK')]
    ]

    window = Creation(title, layout)
    event, value = window.read()
    window.close()

#Signal_Handler Function: To handle the Ctrl+C signal with by sending a termination message
def Signal_Handler(sig, frame):
    termination_message = "User is terminating the connection"
    print(termination_message)
    client_socket.send(termination_message.encode("utf-8"))
    client_socket.close()
    sys.exit(0)

#Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, Signal_Handler)

#Input_Window Function: To create an input window & handle the user's input
def Input_Window (title, layout):
    window = Creation(title, layout)

    while True:
        event, values = window.read()
        if event in (psg.WINDOW_CLOSED, 'Cancel'):
            window.close()
            return None
            #sys.exit(0)
        if values['-INPUT-']:
            input=values['-INPUT-']
            window.close()
            return input

#Socket is crreated
client_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# step one: establishing the connection to the server
server_ip = '127.0.0.2'
server_port = 55555

#Exception Handling
try:
    #Establishes a connection to the server
    client_socket.connect((server_ip, server_port))
    print("Connected to the server.")
except ConnectionRefusedError:
    psg.PopupError("Connection refused. Make sure the server is running.")
    exit()
except Exception as e:
    print(f"An error occurred while connecting to the server: {e}")
    exit()


username_layout = [
    [psg.Text("Please enter your username: ", font=("Arial Bold", 14))],
    [psg.Input(key="-INPUT-", font=("Arial", 12))],
    [psg.Submit(),psg.Cancel()]
]
#User is prompted to enter their username by the use of a PySimpleGUI window
user = Input_Window("Username", username_layout)
#The inserted username is sent to the server
client_socket.send((user).encode('utf-8'))

#Infinite loop to handle the user's options.
while True:
    options_layout = [
        [psg.Text("Choose one of the following options: ",font=("Arial", 12))],
        [psg.Text("1. Show arrived flights",font=("Arial", 12))],
        [psg.Text("2. Show delayed flights",font=("Arial", 12))],
        [psg.Text("3. Show all the flights coming from a specific city",font=("Arial", 12))],
        [psg.Text("4. Show details of a particular flight",font=("Arial", 12))],
        [psg.Text("5. Quit",font=("Arial", 12))],
        [psg.Text('Choose a number between 1-5:',font=("Arial Bold", 14)), psg.Input(key="-INPUT-",font=("Arial", 14))],
        [psg.Button('Send'), psg.Button('Cancel')]
    ]
    #User is prompted to choose from the options listed by the use of a PySimpleGUI window
    option= Input_Window('Options', options_layout)
    #The option selected is sent to the server
    client_socket.send((option).encode('utf-8'))

    #All arrived flights are displayed 
    if option == '1':
        data = client_socket.recv(2048).decode("utf-8")
        ShowF('Arrived Flights', data)

    #All delayed flights are displayed 
    elif option == '2':
        data = client_socket.recv(2048).decode("utf-8")
        ShowF('Delayed Flights', data)
    
    #All flights coming from a specific city are displayed 
    elif option == '3':
        a_layout=[
            [psg.Text("Enter the City:  ", font=("Arial", 10))],
            [psg.Input(key="-INPUT-")],
            [psg.Button("Send")]
        ]
        #User is prompted to enter a city's name 
        A_ICAO = Input_Window('All Flights from a Specific Airport',a_layout)
        #The city's name is sent to the server
        client_socket.send(A_ICAO.encode('utf-8'))
        A_flights= client_socket.recv(20480).decode('utf-8')
        ShowF(f'All Flights from {A_ICAO.capitalize()}', A_flights)

    #All flights coming from a specific city are displayed 
    elif option == '4':
        f_layout=[
            [psg.Text("Enter Flight IATA:  ", font=("Arial", 10))],
            [psg.Input(key="-INPUT-")],
            [psg.Button("Send")]
        ]
        #User is prompted to a flight's IATA Code 
        F_ICAO= Input_Window('Details about a Specific Flight',f_layout)
        #Flight's IATA Code is sent to the server
        client_socket.send(F_ICAO.encode('utf-8'))
        A_flights= client_socket.recv(20480).decode('utf-8')
        ShowF(f'Details of Flight Number: {F_ICAO.capitalize()}', A_flights)

    #Allows the user to quit 
    elif option == "5":
        client_socket.send((user + " is disconnected").encode("utf-8"))
        print("Quitting...")
        client_socket.close()
        psg.popup("Connection terminated.")
        print("Connection terminated!")
        sys.exit(0)