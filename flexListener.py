#/usr/bin/env python3


import json, socket
import keyring
import requests
from reportlab.pdfgen import canvas


authUrl = "https://stagehouse.flexrentalsolutions.com/rest/core/authenticate"
authData = {'username':'apitest', 'password':'w1&O7VQ2^q1LQpDT'}
inquiryUrl = "https://stagehouse.flexrentalsolutions.com/rest/warehouse/inquiry"

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('104.131.138.31', 9100)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('Waiting for Flex to send a label...')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)
        data = connection.recv(1024)
        jdata = data.strip().decode('ascii')
        j=jdata.strip('\x01')
        if (json.loads(j)):
            parsedLabel = json.loads(j)
            try:
                r_auth = requests.post(authUrl, data=authData)
            except Exception as e:
                print(e)
            print("URL:" + r_auth.url + " - " + str(r_auth.status_code))
            r_inquiry = requests.post(inquiryUrl, data=parsedLabel['barcode'])
        print(json.dumps(parsedLabel, indent=4, sort_keys=True))
    finally:
        # Make a label, save it in web-accessible directory
        c = canvas.Canvas("/home/jsm/label.pdf")
        c.drawString(50,500,parsedLabel['itemName'])
        c.drawString(50,400,parsedLabel['barcode'])
        c.drawString(50,300,parsedLabel['manufacturer'])
        c.drawString(50,200,parsedLabel['weight'])
        c.drawString(50,100,"ONE HUNDRED SLASH FIFTY")
        c.showPage()
        c.save()
        # Clean up the connection
        connection.close()

