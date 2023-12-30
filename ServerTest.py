import socket
import requests
import threading
import json

# Step 1: Starting the server/ Enter arr_icao
print('=' * 5, 'Welcome to our server! Our server is on.', '=' * 5)

flight_icao = input("Please enter the airport code (ICAO code): ")

params = {
    # Step 2: Since that the API should retrieve 100 records of flights
    'limit': 100,
    'arr_icao': flight_icao
}

with open("G_B17Test.json", "w") as file:
    response = requests.get('http://api.aviationstack.com/v1/flights?access_key=521d31a723165e2347ec1f7b0d8fac7c',
                            params)

    if response.status_code != 200:
        state = "Request is not done successfully! Server failure took place."
    else:
        state = "Request is done successfully!"

    print(state)

    if state == "Request is done successfully!":
        json.dump(response.json(), file, indent=4)
        print("Retrieved data is added successfully!")
    else:
        print("Error!, failed to retrieve data!")


# Step 4: handling connections between the server and the clients' requests
def connect(socket, address, thread_no, clients):
    print('+' * 5, ' Thread: ', thread_no, ' is ready to receive the username from the client ', '+' * 5)

    # Error handling and exception handling
    try:
        # receive the client's username from the socket
        username = socket.recv(2048).decode('utf-8')
    except ConnectionResetError:
        print('The connection with ', address, ' is currently closed')
        return

    print(username, 'is connected to the server')
    # add the username of the client to the list defined inorder to return the currently connected clients
    clients.append(username)
    print('Currently connected clients are: ', clients)

    # Listening for requests
    while True:
        CityFound = False
        FlightNoFound = False
        counter = 0  # Inorder to count the number of flights
        try:
            # receiving requests' No. from the client
            option = socket.recv(2048).decode('utf-8')
            if option == '1':
                print(username, 'chose the option number', option, ": All Arrived Flights")
            elif option == '2':
                print(username, 'chose the option number', option, ": All Delayed Flights")
            elif option == '3':
                print(username, 'chose the option number', option, ": All Flights Coming from a Specific City")
            elif option == '4':
                print(username, 'chose the option number', option, ": Details of a Particular Flight")
        except ConnectionResetError:
            print(username, ' is disconnected')
            clients.remove(username)
            socket.close()
            return
        # Opening the json file, inorder to read
        with open('G_B17Test.json', 'r') as file:
            # Retrieving data
            data = json.load(file)

        if option == '1':
            #print("\n -----All Arrived Flights----- \n")
            info = []
            for flight in data['data']:
                if flight['flight_status'] == 'landed':
                    counter += 1
                    flight_info = (
                        f"\n Flight:{counter}",
                        f"\n Flight IATA Code:{flight['flight']['iata']}",
                        f"\n Departure Airpot:{flight['departure']['airport']}",
                        f"\n Arrival Time Scheduled:{flight['arrival']['actual']}",
                        f"\n Arrival Terminal:{flight['arrival']['terminal']}",
                        f"\n Arrival Gate: {flight['arrival']['gate']}",
                        "\n" +"-" * 20
                        )
                    info.append(flight_info)
            if not info:
                info = ['No flights has arrived']
            info = '\n'.join(' '.join(flight_tuple) for flight_tuple in info)
            socket.send(info.encode('utf-8'))
        
        elif option == '2':
            print("\n -----All Delayed Flights----- \n")
            info = ''
            for flight in data['data']:
                if flight['arrival']['delay'] != None:
                    counter += 1
                    info += " \n Flight:", counter
                    info += "\n Flight IATA Code:", str(flight['flight']['iata'])
                    info += "\n Departure Airpot:", str(flight['departure']['airport'])
                    info += "\n Original Departure Time Scheduled:", str(flight['arrival']['scheduled'])  # Or departure estimated?
                    info += "\n Estimated Arrival Time:", str(flight['arrival']['estimated'])
                    info += "\n Arrival Terminal:", str(flight['arrival']['terminal'])
                    info += "\n Arrival Gate:", str(flight['arrival']['gate'])
                    info += "\n Delay:", str(flight['arrival']['delay'])
                    info += "\n", "-" * 20
                if not info:
                    info = 'No delayed flights found'
                socket.send(info.encode('utf-8'))

        elif option == '3':
            print("\n -----All Flights Coming from a Specific City----- \n")
            try:
                # receiving the city name from the client
                city = socket.recv(2048).decode('utf-8')
                print("The client ", username, "wants to check all flights coming from ", city)
            except ConnectionResetError:
                print(username, ' is disconnected')
                clients.remove(username)
                socket.close()
                return

            info = ''
            for flight in data['data']:
                if flight['departure']['airport'] == city: ##
                    counter += 1
                    info += " \n Flight:", counter
                    info += "\n Flight IATA Code:", str(flight['flight']['iata'])
                    info += "\n Departure Airpot:", str(flight['departure']['airport'])
                    info += "\n Arrival Time Scheduled:", str(flight['arrival']['scheduled'])
                    info += "\n Arrival Terminal:", str(flight['arrival']['terminal'])
                    info += "\n Arrival Gate:", str(flight['arrival']['gate'])
                    info += "\n", "-" * 20
                    CityFound = True
            if not CityFound:
                info = 'No flights coming from the specified city'
            socket.send(info.encode('utf-8'))

        elif option == '4':
            print("\n -----Details of a Particular Flight----- \n")
            try:
                # receiving the flight number from the client
                flight_no = socket.recv(2048).decode('utf-8')
                print("The client ", username, "wants to check the details of flight number ", flight_no)
            except ConnectionResetError:
                print(username, ' is disconnected')
                clients.remove(username)
                socket.close()
                return

            info = ''
            for flight in data['data']:
                if flight['flight']['iata'] == flight_no:
                    counter += 1
                    info += "\n Flight:", counter
                    info += "\n Flight IATA Code:", str(flight['flight']['iata'])
                    info += "\n Departure Airpot:", str(flight['departure']['airport'])
                    info += "\n Arrival Time Scheduled:", str(flight['arrival']['scheduled'])
                    info += "\n Arrival Terminal:", str(flight['arrival']['terminal'])
                    info += "\n Arrival Gate:", str(flight['arrival']['gate'])
                    info += "\n", "-" * 20
                    FlightNoFound = True
            if not FlightNoFound:
                info = 'No flight found with the specified flight number'
            socket.send(info.encode('utf-8'))

        elif option == '5':
            # Close the connection with the client
            print('The client', username, 'is disconnected')
            clients.remove(username)
            socket.close()
            return


# Step 3: creating threads to handle the clients' requests
clients = []
threads = []
thread_no = 0

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the host and port
host = '127.0.0.2'
port = 55555

# Bind the socket to a specific address and port
server_socket.bind((host, port))

# Listen for incoming connections
server_socket.listen()

print('Waiting for incoming connections...')

while True:
    # Accept a new connection
    client_socket, address = server_socket.accept()
    thread_no += 1

    # Create and start a new thread to handle the client connection
    thread = threading.Thread(target=connect, args=(client_socket, address, thread_no, clients))
    thread.start()

    threads.append(thread)






