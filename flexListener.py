#/usr/bin/env python3


import json, socket
import keyring
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics.barcode import code128
from reportlab.platypus import Image
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


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
        c = canvas.Canvas("/var/www/html/labels/" + parsedLabel['itemName'].replace(' ','')+"_label.pdf",pagesize=letter)
        bc=code128.Code128(parsedLabel['barcode'],barHeight=0.75*inch,barWidth=1.5)
        labelFont = r"resources/RobotoCondensed-Bold.ttf"
        pdfmetrics.registerFont(TTFont("Roboto Condensed Bold",labelFont))
        c.drawImage("resources/header.jpg",10,660)
        c.setFont("Helvetica",24) # draw all caption text in 24pt Helvetica
        c.drawCentredString(300,630,"SHOW NAME:")
        c.drawCentredString(300,530,"ITEM NAME:")
        c.drawCentredString(300,430,"MANUFACTURER:")
        c.drawString(30,330,"WEIGHT:")
        c.drawString(180,330,"HEIGHT:")
        c.drawString(330,330,"LENGTH:")
        c.drawString(480,330,"WIDTH:")
        c.setFont("Roboto Condensed Bold",36)
        c.drawCentredString(300,600,parsedLabel['showName'])
        c.drawCentredString(300,500,parsedLabel['itemName'])
        c.drawCentredString(300,400,parsedLabel['manufacturer'])
        c.drawString(30,300,parsedLabel['weight'])
        c.drawString(180,300,parsedLabel['height'])
        c.drawString(330,300,parsedLabel['length'])
        c.drawString(480,300,parsedLabel['width'])
        bc.drawOn(c,225,200) # canvas, x, y
        c.showPage()
        c.save()
        # Clean up the connection
        connection.close()

