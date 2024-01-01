import socket
import PySimpleGUI as psg
import signal
import sys

# theme for the windows
psg.theme('LightBlue6')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
    [psg.Text("Please enter your username: ", font=("Arial Bold", 12))],
    [psg.Input(key="-INPUT-", font=("Arial Bold", 12))],
    [psg.Submit()],
    [psg.Cancel()]
]

# Function to handle the Ctrl+C signal
def signal_handler(sig, frame):
    termination_message = "User is terminating the connection"
    print(termination_message)
    client_socket.send(termination_message.encode("utf-8"))
    client_socket.close()
    sys.exit(0)

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# create a window for username
window = psg.Window("Group_B17", username_layout, resizable=True)
event, values = window.read()
window.close()

username = values["-INPUT-"]

# sending the username to server
if username is not None:
    client_socket.send(username.encode("utf-8"))
else:
    psg.popup("Username cannot be empty.")
    exit()

def window_creation(title, data):
    window = psg.Window(title, data, resizable=True)
    event, value = window.read()
    window.close()

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
        [psg.Button("Submit")]
    ]
    # create window for options
    window = psg.Window("Group_B17", options_layout, resizable=True)
    event, values = window.read()
    option = values["-INPUT-"]
    window.close()

    # send the chosen request to the server
    client_socket.send(option.encode("utf-8"))

    # Handle window close event
    if event == psg.WINDOW_CLOSED:
        client_socket.send((username + " is disconnected").encode("utf-8"))
        client_socket.close()
        psg.popup("Window closed. Connection terminated.")
        print("Connection being terminated!")
        exit()

    # if client chooses an invalid option
    if option not in ["1", "2", "3", "4", "5"]:
        print("Invalid! Please enter a valid option.")
        break

    # if client chooses one of the valid options
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
        # decode the received data from the server
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
        window = window_creation("Group_B17", layout, resizable=True)
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

    # step three: closing the connection if the user chooses to quit
    elif option == "5":
        client_socket.send((username + " is disconnected").encode("utf-8"))
        print("Quitting...")
        client_socket.close()
        psg.popup("Connection terminated.")
        print("Connection terminated!")
        exit()
