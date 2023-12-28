import socket
import PySimpleGUI as PySimpleGUI

# theme for the windows
PySimpleGUI.theme('LightBlue6')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# step one: establishing the connection to the server
server_ip = '127.0.0.2'
server_port = 55555

try:
    client_socket.connect((server_ip, server_port))
    print("Connected to the server.")
except ConnectionRefusedError:
    print("Connection refused. Make sure the server is running.")
    exit()
except Exception as e:
    print(f"An error occurred while connecting to the server: {e}")
    exit()

# sending username
username_layout = [
    [PySimpleGUI.Text("Please enter your username: ", font=("Arial Bold", 12))],
    [PySimpleGUI.Input(key="-INPUT-", font=("Arial Bold", 12))],
    [PySimpleGUI.Submit()],
    [PySimpleGUI.Cancel()]
]
# create a window for username
window = PySimpleGUI.Window("Group_B17", username_layout, resizable=True)
event, values = window.read()
window.close()

uname = values["-INPUT-"]

# sending the username to server
client_socket.send(uname.encode("utf-8"))

# create windows for later use
def window_creation(title, data):
    window = PySimpleGUI.Window(title, data, resizable=True)
    event, value = window.read()
    window.close()

# step two: prompt user to choose one of the options
while True:
    options_layout = [
        [PySimpleGUI.Text("Choose one of the following options: ")],
        [PySimpleGUI.Text("1. Show arrived flights")],
        [PySimpleGUI.Text("2. Show delayed flights")],
        [PySimpleGUI.Text("3. Show all the flights coming from a specific city")],
        [PySimpleGUI.Text("4. Show details of a particular flight")],
        [PySimpleGUI.Text("5. Quit")],
        [PySimpleGUI.Input()],
        [PySimpleGUI.Button("Submit")]
    ]
    # create window for options
    window = PySimpleGUI.Window("Group_B17", options_layout, resizable=True)
    event, option = window.read()
    option = option[0]
    window.close()

    # send the chosen request to the server
    client_socket.send(option.encode("utf-8"))

    # if client chooses an invalid option
    if option not in ["1", "2", "3", "4", "5"]:
        print("Invalid! Please enter a valid option.")

    # if client chooses one of the valid options
    if option == "1":
        # decode the received data from the server
        data = client_socket.recv(20480).decode("utf-8")
        layout = [
            [PySimpleGUI.Text("All the arrived flights:", font="Arial")],
            [PySimpleGUI.Column([[PySimpleGUI.Text(data)]], scrollable=True, vertical_scroll_only=True)]
        ]
        # window creation
        window_creation("Group_B17", layout)

    elif option == "2":
        # decode the received data from the server
        data = client_socket.recv(20480).decode("utf-8")
        layout = [
            [PySimpleGUI.Text("All the delayed flights:", font="Arial")],
            [PySimpleGUI.Column([[PySimpleGUI.Text(data)]], scrollable=True, vertical_scroll_only=True)]
        ]
        # window creation
        window_creation("Group_B17", layout)

    elif option == "3":
        # prompt user to enter ICAO code
        layout = [
            [PySimpleGUI.Text("Enter city ICAO:  ", font=("Arial", 10))],
            [PySimpleGUI.Input(key="-INPUT-")],
            [PySimpleGUI.Button("Send")]
        ]
        # window creation
        window = PySimpleGUI.Window("Group_B17", layout, resizable=True)
        event, city = window.read()
        city = city["-INPUT-"]
        window.close()

        # send ICAO to the server
        client_socket.send(city.encode("utf-8"))
        # receive flight data
        flight_data = client_socket.recv(20480).decode("utf-8")
        flight_layout = [
            [PySimpleGUI.Text("All the flights coming from " + city.capitalize())],
            [PySimpleGUI.Column([[PySimpleGUI.Text(flight_data)]], scrollable=True, vertical_scroll_only=True)]
        ]
        # window creation
        window_creation("Group_B17", flight_layout)

    elif option == "4":
        flight_layout = [
            [PySimpleGUI.Text("Enter city ICAO or flight number: ", font=("Arial", 12))],
            [PySimpleGUI.Input()],
            [PySimpleGUI.Button("Send")]
        ]

        # create window
        window = PySimpleGUI.Window("Group_B17", flight_layout, resizable=True)
        event, flight = window.read()
        flight = flight[0]
        window.close()

        # send ICAO to the server
        client_socket.send(flight.encode("utf-8"))
        # receive data from the server
        flight_data = client_socket.recv(20480).decode("utf-8")
        layout = [
            [PySimpleGUI.Text(f"Details of flight with this city ICAO/flight number: {flight.capitalize()}")],
            [PySimpleGUI.Column([[PySimpleGUI.Text(flight_data)]], scrollable=True, vertical_scroll_only=True)]
        ]
        # window creation
        window_creation("Group_B17", layout)

    # step three: closing the connection if the user chooses to quit
    elif option == "5":
        client_socket.send((uname + " is disconnected").encode("utf-8"))
        client_socket.close()
        break

