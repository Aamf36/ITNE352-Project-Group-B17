import socket
import requests
import threading
import json

#Step 1: Starting the server/ Enter arr_icao
print ('='*5,'Welcome to our server! Our server is on.','='*5)

Link= 'https://api.aviationstack.com/v1/flights'

flight_icao = input("Please enter the airport code (ICAO code):  ")

flight_para= {
    'access_key':'521d31a723165e2347ec1f7b0d8fac7c'
    #Since that the API should retrieve 100 records of flights
    'limit':100
    'arr_icao':flight_icao
}







