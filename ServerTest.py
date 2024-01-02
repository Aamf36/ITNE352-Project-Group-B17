# Necessary Modules are imported
import socket
import requests
import threading
import json
import time

# Indicates that the server is on
print ('=' * 5, 'Welcome to our server! Our server is on.', '=' * 5, '\n')

# Prompt the user to enter ICAO Code, that will be stored in flight_icao
flight_icao = input("Please enter the airport code (ICAO code): ")

params = {
    # Step 2: Since the API should retrieve 100 records of flights
    'limit': 100,
    'arr_icao': flight_icao
}

# Exception Handling
try:
    # Sends a GET request to the link
    response = requests.get('http://api.aviationstack.com/v1/flights?access_key=5ae1eac9b2a157cb4dbf9f16d838f9b8',
                            params=params)
    # Checks the status code of the response
    if response.status_code != 200:
        print("Error! Failed to retrieve data. Status code:", response.status_code)
    else:
        with open("Group_b17.json", "w") as file:
            json.dump(response.json(), file, indent=4)  # Writes the JSON response
        print("Retrieved data is added successfully!")  # A success message is printed
        print('-' * 15)
except NameError:
    print("Error! 'response' is not defined.")
except Exception as e:
    print('An error occurred: Failed to write data to file')
    print('~' * 10)

# Function Connect: Responsible for handling connections
def connect(client_socket, address, thread_no):
    print('\n', '+' * 5, 'Thread:', thread_no, 'is ready to receive the username from the client with address:',
          address, '+' * 5)

    # Exception Handling
    try:
        username = client_socket.recv(2048).decode('utf-8')  # Username is received
        if username == "User is terminating the connection":  # Terminated
            print('\nUnknown User (No username) terminated its connection')
            print('Currently connected clients are: ', clients)
            print('~' * 10)

        elif username == '':  # Empty username
            print(f"Thread {thread_no}: User did not enter a username. Closing connection.") 
            client_socket.close()  # socket connection is closed
            return

        else:
            print('\n', username, 'is connected to the server')
            clients.append(username)
            print('\nCurrently connected clients are: ', clients)

    except ConnectionResetError:
        print("Connection with address", address, "closed!")
        return

    # Handles the client's requests until they disconnect
    while True:
        CityFound = False
        FlightNoFound = False
        counter = 0  # In order to count the number of flights
        option = client_socket.recv(2048).decode('utf-8')
        try:
            if option == '1':
                print(username, 'chose the option number', option, ": All Arrived Flights")
            elif option == '2':
                print(username, 'chose the option number', option, ": All Delayed Flights")
            elif option == '3':
                print(username, 'chose the option number', option, ": All Flights Coming from a Specific City")
            elif option == '4':
                print(username, 'chose the option number', option, ": Details of a Particular Flight")
            else:
                print('\n', username, ' is disconnected')
                clients.remove(username)
                print('~' * 10)
                client_socket.close()
                return

        except ConnectionResetError:
            print('\n', username, ' connection was reset by the server.')

        # Opening the JSON file, in order to read the data
        with open('Group_b17.json', 'r') as file:
            # Retrieving data
            data = json.load(file)

        # Client wants to retrieve all arrived flights
        if option == '1':
            info = []
            for flight in data['data']:
                if flight['flight_status'] == 'landed':
                    counter += 1
                    flight_info = (
                        f"\n Flight:{counter}",
                        f"\n Flight IATA Code:{flight['flight']['iata']}",
                        f"\n Departure Airport:{flight['departure']['airport']}",
                        f"\n Arrival Time:{flight['arrival']['actual']}",
                        f"\n Arrival Terminal Number:{flight['arrival']['terminal']}",
                        f"\n Arrival Gate: {flight['arrival']['gate']}",
                        "\n" + "-" * 20
                    )
                    info.append(flight_info)
            if not info:
                info = ['No flights were found.']
            info = '\n'.join(' '.join(flight_tuple) for flight_tuple in info)
            client_socket.send(info.encode('utf-8'))

        # Client wants to retrieve all delayed flights
        elif option == '2':
            info = []
            for flight in data['data']:
                if flight['flight_status'] == 'delayed':
                    counter += 1
                    flight_info = (
                        f"\n Flight:{counter}",
                        f"\n Flight IATA Code: {flight['flight']['iata']}",
                        f"\n Departure Airport: {flight['departure']['airport']}",
                        f"\n Original Departure Time:{flight['departure']['scheduled']}", 
                        f"\n Estimated Arrival Time: {flight['arrival']['estimated']}",
                        f"\n Arrival Terminal:{flight['arrival']['terminal']}",
                        f"\n Delay: {flight['arrival']['delay']}",
                        f"\n Arrival Gate:{flight['arrival']['gate']}",
                        "\n", "-" * 20
                    )
                    info.append(flight_info)
            if not info:
                info = ['No flights were found.']
            info = '\n'.join(' '.join(flight_tuple) for flight_tuple in info)
            client_socket.send(json.dumps(info).encode('utf-8'))

        # Client wants to retrieve all flights coming from a specific city
        elif option == '3':
            ClientC = client_socket.recv(2048).decode('utf-8')
            info = []
            for flight in data['data']:
                if flight['departure']['icao'] == ClientC:
                    CityFound = True
                    counter += 1
                    flight_info = (
                        f"\nFlight: {counter}",
                        f"\nFlight IATA Code: {flight['flight']['iata']}",
                        f"\nDeparture Airport: {flight['departure']['airport']}",
                        f"\nOriginal Departure Time: {flight['departure']['scheduled']}",
                        f"\nEstimated Arrival Time: {flight['arrival']['estimated']}",
                        f"\nDeparture Gate: {flight['departure']['gate']}",
                        f"\nArrival Gate: {flight['arrival']['gate']}",
                        f"\nStatus: {flight['flight_status']}",
                        "\n" + "-" * 20
                    )
                    info.append(flight_info)
            if not info:
                info = ['No flights were found.']
            info = '\n'.join(' '.join(flight_tuple) for flight_tuple in info)
            client_socket.send(json.dumps(info).encode('utf-8'))

        # Client wants to retrieve details of a particular flight
        elif option == '4':
            flight_no = client_socket.recv(2048).decode('utf-8')
            info = []
            for flight in data['data']:
                if flight['flight']['iata'] == flight_no:
                    FlightNoFound = True
                    flight_info = (
                        f"\nFlight: {counter}",
                        f"\nFlight IATA Code: {flight['flight']['iata']}",
                        f"\nDeparture Airport: {flight['departure']['airport']}",
                        f"\nDeparture Gate: {flight['departure']['gate']}",
                        f"\nDeparture Terminal: {flight['departure']['terminal']}",
                        f"\nArrival Airport: {flight['arrival']['airport']}",
                        f"\nArrival Gate: {flight['arrival']['gate']}", 
                        f"\nArrival Terminal: {flight['arrival']['terminal']}",
                        f"\nStatus: {flight['flight_status']}",
                        f"\nScheduled Departure Time: {flight['departure']['scheduled']}",
                        f"\nScheduled Arrival Time: {flight['arrival']['scheduled']}",
                        "\n" + "-" * 20
                    )

                    info.append(flight_info)
            if not info:
                info = ['No flight with the specified flight number was found.']
            info = '\n'.join(' '.join(flight_tuple) for flight_tuple in info)
            client_socket.send(json.dumps(info).encode('utf-8'))

        # Client wants to disconnect from the server
        else:
            print('\n', username, ' is disconnected')
            clients.remove(username)
            print('~' * 10)
            client_socket.close()
            return


# Holds the connected clients
clients = []
# Counter for the threads
thread_count = 0

# Initialize a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get the local machine name
host = '127.0.0.2'
port = 55555

# Bind the socket to a specific address and port
server_socket.bind((host, port))

# Listen for incoming connections
server_socket.listen()

while True:
    # Accept a new connection from a client
    client_socket, address = server_socket.accept()

    # Create a new thread for each client
    thread_count += 1
    t = threading.Thread(target=connect, args=(client_socket, address, thread_count))
    t.start()