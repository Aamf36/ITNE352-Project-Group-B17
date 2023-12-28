import socket
import requests
import threading
import json

#Step 1: Starting the server/ Enter arr_icao
print ('='*5,'Welcome to our server! Our server is on.','='*5)

flight_icao = input("Please enter the airport code (ICAO code):  ")

params= {
    #Step 2: Since that the API should retrieve 100 records of flights
    'limit':100,
    'arr_icao':flight_icao
}

try: #Error handling and exception handling
    with open("G_B17Test.json","w") as file:
        #Get request to the specidfied API
        response = requests.get('http://api.aviationstack.com/v1/flights?access_key=521d31a723165e2347ec1f7b0d8fac7c', params)
        
        if response.status_code!=200:
            state="Request is not done successfully! Server failure took place."
        else:
            state="Request is done successfully!"
    #dump function is used to push the incoming data from the API to the file
    json.dump(response.json(),file, indent=4)
    print("Retrieved data is added successfully!")
except Exception:
    print("Error!, failled to retreive data!")

#Step 4: handling connections between the server and the clients' requests
def connect(socket,address,thread_no,clients):
    print('+'*5,' Thread: ',thread_no,' is ready to receive the username from the client ', '+'*5)

#Error handling and exception handling
    try:
        # receive the client's username from the socket 
        username = socket.recv(2048).decode('utf-8')
    except ConnectionResetError:
        print('The connection with ', address,' is currently closed')
        return

    print(username, 'is connected to the server')
    # add the username of the client to the list defined inorder to return the currently connected clients
    clients.append(username)
    print('Currently connected clients are: ', clients)
    
    #Listening for requests 
    while True:
        CityFound=False
        FlightNoFound=False
        counter=0 #Inorder to count the number of flights
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
        #Opening the json file, inorder to read
        with open('G_B17_Test.json', 'r') as file:
            #Retrieving data
            data = json.load(file)

        if option == '1':
            print("\n -----All Arrived Flights----- \n")
            info=''
            for flight in data['data']:
                if flight['flight_status']=='landed':
                    counter+=1
                    info += " \n Flight:",counter
                    info += "\n Flight IATA Code:",(str(flight['flight']['iata']))
                    info += "\n Departure Airpot:",(str(flight['departure']['airport']))
                    info += "\n Arrival Time Scheduled:",(str(flight['arrival']['scheduled']))
                    info += "\n Arrival Terminal:",(str(flight['arrival']['terminal']))
                    info += "\n Arrival Gate:",(str(flight['arrival']['gate']))
                    info += "\n","-"*20
                if not info:
                    info='No flights has arrived'
                socket.send(info.encode('utf-8'))
                
        elif option == '2':
            print("\n -----All Delayed Flights----- \n")
            info=''
            for flight in data['data']:
                if flight['arrival']['delay']!= None:
                    counter+=1
                    info += " \n Flight:",counter
                    info += "\n Flight IATA Code:",(str(flight['flight']['iata']))
                    info += "\n Departure Airpot:",(str(flight['departure']['airport']))
                    info += "\n Original Departure Time Scheduled:",(str(flight['arrival']['scheduled'])) #Or departure estimated?
                    info += "\n Estimated Arrival Time:",(str(flight['arrival']['estimated']))
                    info += "\n Arrival Terminal:",(str(flight['arrival']['terminal']))
                    info += "\n Delay:",(str(flight['arrival']['delay']))
                    info += "\n Arrival Gate:",(str(flight['arrival']['gate']))
                    info += "\n","-"*20
                if not info:
                    info='No delayed flights has been found'
                socket.send(info.encode('utf-8'))

                
        elif option == '3':
            city=socket.recv(2048).decode('utf-8')
            print("\n -----All Flights Coming from Specific City----- \n")
            info=''
            for flight in data['data']:
                if city in flight['departure']['airport']:
                    CityFound=True
                    counter+=1
                    info += " \n Flight:",counter
                    info += "\n Flight IATA Code:",(str(flight['flight']['iata']))
                    info += "\n Departure Airpot:",(str(flight['departure']['airport']))
                    info += "\n Original Departure Time Scheduled:",(str(flight['arrival']['scheduled'])) #departure actual or estimated?
                    info += "\n Estimated Arrival Time:",(str(flight['arrival']['estimated']))
                    info += "\n Arrival Gate:",(str(flight['arrival']['gate']))
                    info += "\n Departure Gate:",(str(flight['departure']['gate']))
                    info += "\n Flight Status:",(str(flight['flight_status']))
                    info += "\n","-"*20
                if not CityFound:
                    info+='No flights has been found for the specified city'
                socket.send(info.encode('utf-8'))           

        elif option == '4':
            FlightNO=socket.recv(2048).decode('utf-8')
            print('\n -----Details of Flight Number:',FlightNO,'----- \n')
            info=''
            for flight in data['data']:
                if flight['flight']['number']== FlightNO:
                    FlightNoFound=True
                    info += " \n Flight Number:",FlightNO
                    info += "\n Flight IATA Code:",(str(flight['flight']['iata']))
                    info += "\n Flight Date:",(str(flight['flight_date']))
                    info += "\n Departure Airpot:",(str(flight['departure']['airport']))
                    info += "\n Departure Gate:",(str(flight['departure']['gate']))
                    info += "\n Arrival Airport:",(str(flight["arrival"]["airport"]))
                    info += "\n Arrival Gate:",(str(flight['arrival']['gate']))
                    info += "\n Arrival Terminal:",(str(flight['arrival']['terminal']))
                    info += "\n Flight Status:",(str(flight['flight_status']))
                    info += "\n Scheduled Departure Time:",(str(flight['departure']['scheduled']))
                    info += "\n Scheduled Arrival Time:",(str(flight['arrival']['scheduled']))
                    info += "\n","-"*20
                    #break
                if not FlightNoFound:
                    info+='No flight has been found for the flight number specified'
                socket.send(info.encode('utf-8'))           

        elif option == '5':
            print(username, 'is being disconnected') 
            clients.remove(username)
            print('Here are the connected clients:',clients)
            socket.close()
            return

        # Incase an invalid option is chosen
        else:
            print('Invalid request from', username, 'so the connection is closing')
            clients.remove(username)
            print('Currently connected clients are:',clients)
            socket.close()
            return

# Creating the server socket and accepting incoming connections
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to IP address
server_socket.bind(('192.167.0.0', 65535))
# listen for incoming connections
server_socket.listen()

clients = []  # List to keep track of connected clients

# Function to handle each client connection
def handle_client_connection(client_socket, address):
    # Your existing code for handling the client connection

# Accept incoming connections and create threads to handle each connection
 while True:
    client_socket, address = server_socket.accept()
    print('Accepted connection from:', address)
    # Create a new thread to handle the client connection
    client_thread = threading.Thread(target=handle_client_connection, args=(client_socket, address))
    client_thread.start()






