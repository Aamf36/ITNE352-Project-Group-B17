#Necessary Modules are imported
import socket
import requests
import threading
import json
import time

#Indicates that the server is on
print('=' * 5, 'Welcome to our server! Our server is on.', '=' * 5, '\n')

#Prompt the user to enter ICAO Code, that will be stored in flight_icao
flight_icao = input("Please enter the airport code (ICAO code): ")

params = {
    # Step 2: Since the API should retrieve 100 records of flights
    'limit': 100,
    'arr_icao': flight_icao
}

#Exception Handling
try: 
    #Sends a GET request to the link
    response = requests.get('http://api.aviationstack.com/v1/flights?access_key=9f5375b1daab02a35c8d0e751eb60be1', params=params)
    #Checks the status code of the response
    if response.status_code != 200:
        print("Error! Failed to retrieve data. Status code:", response.status_code)
    else:
        with open("F_test.json", "w") as file:
            json.dump(response.json(), file, indent=4) #Writes the JSON response
        print("Retrieved data is added successfully!") #A success message is printed
        print('-' * 15)
except NameError:
    print("Error! 'response' is not defined.")
except Exception as e:
    print('An error occurred: Failed to write data to file')
    print('~' * 10)
    socket.close()

#Function Connect: Responsible for handling connections
def connect(socket, address, thread_no):
    print('\n', '+' * 5, 'Thread:', thread_no, 'is ready to receive the username from the client with address:',
          address, '+' * 5)

    #Exception Handling
    try:
        username = socket.recv(2048).decode('utf-8') #Username is received
        if username == "User is terminating the connection": #Terminated
            print('\nUnknown User (No username) terminated its connection')
            print('Currently connected clients are: ', clients)
            print('~' * 10)

        elif username == '': #Empty username
            print(f"Thread {thread_no}: User did not enter a username. Closing connection.")
            socket.close() #socket connection is closed
            return
        
        else:
            print('\n', username, 'is connected to the server')
            clients.append(username)
            print('\nCurrently connected clients are: ', clients)

    except ConnectionResetError:
        print("Connection with address", address, "closed!")
        return
    
    #Handles the client's requests until he disconnects
    while True:
        CityFound = False
        FlightNoFound = False
        counter = 0  # In order to count the number of flights
        option = socket.recv(2048).decode('utf-8')
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
                socket.close()
                return

        except ConnectionResetError:
            print('\n', username, ' connection was reset by the server.')

        # Opening the JSON file, in order to read the data
        with open('G_B17T.json', 'r') as file:
            # Retrieving data
            data = json.load(file)

        #Client wants to retrieve all arrived flights
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
                        "\n" + "-" * 20)
                    info.append(flight_info)
            if not info:
                info = ['No flights have arrived']
            info = '\n'.join(' '.join(flight_tuple) for flight_tuple in info)
            socket.send(info.encode('utf-8')) #

        #Client wants to retrieve all delayed flights
        elif option == '2':
            info = []
            for flight in data['data']:
                if flight['arrival']['delay'] != None:
                    counter += 1
                    flight_info = ( 
                        f" \n Flight:{counter}",
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
                info = ['No delayed flights found']
            info = '\n'.join(' '.join(flight_tuple) for flight_tuple in info)
            socket.send(info.encode('utf-8'))

        #Client wants to retrieve all incoming flights from a specific city
        elif option == '3':
            try:
                # receiving the city name from the client
                city = socket.recv(2048).decode('utf-8')
                print("The client", username, "wants to check all flights coming from ", city)
            except ConnectionResetError:
                print(username, 'is disconnected')
                clients.remove(username)
                socket.close()
                return

            info = []
            for flight in data['data']:
                if flight['departure']['airport'] == city: 
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
                    CityFound = True

            if not CityFound:
                info = ['No flights coming from the specified city']
            info = '\n'.join(' '.join(flight_tuple) for flight_tuple in info)
            socket.send(info.encode('utf-8'))

        #Client wants to retrieve details of a specific flight (IATA)
        elif option == '4':
            try:
                # receiving the flight number from the client
                flight_no = socket.recv(2048).decode('utf-8')
                print("The client", username, "wants to check the details of flight number ", flight_no)
            except ConnectionResetError:
                print(username, 'is disconnected')
                clients.remove(username)
                socket.close()
                return

            info = []
            for flight in data['data']:
                if flight['flight']['iata'] == flight_no:
                    counter += 1
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
                    FlightNoFound = True
            if not FlightNoFound:
                info = ['No flight found with the specified flight number']
            info = '\n'.join(' '.join(flight_tuple) for flight_tuple in info)
            socket.send(info.encode('utf-8'))

        #Client wants to disconnect
        elif option == '5':
            # Close the connection with the client
            print('The client', username, 'is disconnected')
            clients.remove(username)
            socket.close()
            return

#Creating threads to handle the clients' requests
clients = []
threads = []
thread_no = 0

#Create a socket 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Define the ip and port
ip = '127.0.0.2'
port = 55555

# Bind the socket to a specific ip and port
server_socket.bind((ip, port))

# Listen for incoming connections
server_socket.listen()

print('\nWaiting for incoming connections...')
#print('*'*10)

#An infininte loop, in order to accept incoming connections
while True:
    # Accept a new connection
    client_socket, address = server_socket.accept()

    thread_no += 1

    # Create a new thread to handle the client connection
    thread = threading.Thread(target=connect, args=(client_socket, address, thread_no))

    #Start the thread
    thread.start()

    #Stores the thread in the thread list
    threads.append(thread)
