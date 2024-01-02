import socket
import PySimpleGUI as psg
import signal
import sys

# theme for the windows
psg.theme('TealMono')

# Function to create a window and handle the window read event
def Creation(title, layout):
    window= psg.Window(title, layout, resizable=True)
    return window
def ShowF(title, data):
    layout = [
        [psg.Text("*"*10 + title + "*"*10, font=('Arial',12, 'bold'))],
        [psg.Column([[psg.Text(data, font=('Arial',10))]], scrollable=True)],
        [psg.Button('OK')]
    ]

    window = Creation(title, layout)
    event, value = window.read()
    window.close()

# Function to handle the Ctrl+C signal
def signal_handler(sig, frame):
    termination_message = "User is terminating the connection"
    print(termination_message)
    client_socket.send(termination_message.encode("utf-8"))
    client_socket.close()
    sys.exit(0)

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

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

client_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# step one: establishing the connection to the server
server_ip = '127.0.0.2'
server_port = 55555

try:
    client_socket.connect((server_ip, server_port))
    print("Connected to the server.")
except ConnectionRefusedError:
    psg.PopupError("Connection refused. Make sure the server is running.")
    exit()
except Exception as e:
    print(f"An error occurred while connecting to the server: {e}")
    exit()

# sending username
username_layout = [
    [psg.Text("Please enter your username: ", font=("Arial Bold", 14))],
    [psg.Input(key="-INPUT-", font=("Arial", 12))],
    [psg.Submit(),psg.Cancel()]
]
user = Input_Window("Group_B17", username_layout)
client_socket.send((user).encode('utf-8'))

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
    option= Input_Window('Group_B17', options_layout)
    client_socket.send((option).encode('utf-8'))

    if option == '1':
        data = client_socket.recv(2048).decode("utf-8")
        ShowF('Arrived Flights', data)

    elif option == '2':
        data = client_socket.recv(2048).decode("utf-8")
        ShowF('Delayed Flights', data)
    
    elif option == '3':
        a_layout=[
            [psg.Text("Enter the City:  ", font=("Arial", 10))],
            [psg.Input(key="-INPUT-")],
            [psg.Button("Send")]
        ]
        A_ICAO = Input_Window('All Flights from a Specific Airport',a_layout)
        client_socket.send(A_ICAO.encode('utf-8'))
        A_flights= client_socket.recv(20480).decode('utf-8')
        ShowF(f'All Flights from {A_ICAO.capitalize()}', A_flights)

    elif option == '4':
        f_layout=[
            [psg.Text("Enter Flight IATA:  ", font=("Arial", 10))],
            [psg.Input(key="-INPUT-")],
            [psg.Button("Send")]
        ]
        F_ICAO= Input_Window('Details about a Specific Flight',f_layout)
        client_socket.send(F_ICAO.encode('utf-8'))
        A_flights= client_socket.recv(20480).decode('utf-8')
        ShowF(f'Details of Flight Number: {F_ICAO.capitalize()}', A_flights)

    elif option == "5":
        client_socket.send((user + " is disconnected").encode("utf-8"))
        print("Quitting...")
        client_socket.close()
        psg.popup("Connection terminated.")
        print("Connection terminated!")
        sys.exit(0)

'''
username = values["-INPUT-"]


# Handle window creation for options
def window_creation(title, data):
    layout = [
        [psg.Text(title)],
        data,
        [psg.Button("Submit")]
    ]
    window = psg.Window("Group_B17", layout, resizable=True)
    event, values = window.read()
    window.close()
    return values

# step two: prompt user to choose one of the options
while True:
    options_layout = [
        [psg.Text("Choose one of the following options: ")],
        [psg.Text("1. Show arrived flights")],
        [psg.Text("2. Show delayed flights")],
        [psg.Text("3. Show all the flights coming from a specific city")],
        [psg.Text("4. Show details of a particular flight")],
        [psg.Text("5. Quit")],
        [psg.Input(key="-INPUT-")],
    ]

    # create window for options
    values = window_creation("Group_B17", options_layout)
    option = values["-INPUT-"]

    # send the chosen request to the server
    client_socket.send(option.encode("utf-8"))

    # Handle the chosen option
    if option == "1":
         # decode the received data from the server
        data = client_socket.recv(20480).decode("utf-8")
        layout = [
            [psg.Text("All the arrived flights:", font="Arial")],
            [psg.Column([[psg.Text(data)]], scrollable=True, vertical_scroll_only=True)]
        ]
        # window creation
        window_creation("Group_B17", layout)

    elif option == "2":
        data = client_socket.recv(20480).decode("utf-8")
        layout = [
            [psg.Text("All the delayed flights:", font="Arial")],
            [psg.Column([[psg.Text(data)]], scrollable=True, vertical_scroll_only=True)]
        ]
        # window creation
        window_creation("Group_B17", layout)

    elif option == "3":
        # prompt user to enter ICAO code
        layout = [
            [psg.Text("Enter city ICAO:  ", font=("Arial", 10))],
            [psg.Input(key="-INPUT-")],
            [psg.Button("Send")]
        ]
        # window creation
        window = window_creation("Group_B17", layout)
        event, values = window.read()
        city = values["-INPUT-"]
        window.close()

        #city = values["-INPUT-"]

        # send ICAO to the server
        client_socket.send(city.encode("utf-8"))
        # receive flight data
        flight_data = client_socket.recv(20480).decode("utf-8")
        flight_layout = [
            [psg.Text("All the flights coming from " + city.capitalize(),font=("Arial", 12))],
            [psg.Column([[psg.Text(flight_data)]], scrollable=True, vertical_scroll_only=True)]
        ]
        # window creation
        window= window_creation("Group_B17", flight_layout)
        event, values = window.read()
        window.close()
        #event, values = window.read()
        #window.close()

    elif option == "4":
        flight_layout = [
            [psg.Text("Enter city ICAO or flight number: ", font=("Arial", 12))],
            [psg.Input(key="-INPUT-")],
            [psg.Button("Send")]
        ]

        # create window
        window = window_creation("Group_B17", flight_layout, resizable=True)
        event, flight = window.read()
        flight =flight["-INPUT-"]
        window.close()

        #flight_number = values["-INPUT-"]

        # send ICAO to the server
        client_socket.send(flight.encode("utf-8"))
        # receive data from the server
        flight_details = client_socket.recv(20480).decode("utf-8")
        layout = [
            [psg.Text(f"Details of flight with this city ICAO/flight number: {flight.capitalize()}")],
            [psg.Column([[psg.Text(flight_details)]], scrollable=True, vertical_scroll_only=True)]
        ]   
        # window creation
        window= window_creation("Group_B17", layout)
        event, values = window.read()
        window.close()

    elif option == "5":
        client_socket.send((username + " is disconnected").encode("utf-8"))
        print("Quitting...")
        client_socket.close()
        psg.popup("Connection terminated.")
        print("Connection terminated!")
        sys.exit(0)
        '''