import RPi.GPIO as GPIO
import time
import os
from socket import *
from time import ctime

def pin_detection_init(input_pin):

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(input_pin,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

def server_communication():
    HOST =''
    PORT = 21567
    BUFSIZE = 1024
    ADDR = (HOST,PORT)

    tcpSerSock = socket(AF_INET, SOCK_STREAM)
    tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcpSerSock.bind(ADDR)
    tcpSerSock.listen(5)

    wait_in_loop = 1
    configuration_successfull = 0# = 1, if user send correct password and configuration got completed

    while wait_in_loop:
        
        print ("Waiting for connection")
        tcpCliSock, addr = tcpSerSock.accept()
        print ('...connected from:', addr)
        
        
        try:
            while wait_in_loop:
                    data = ''
                    data = str(tcpCliSock.recv(BUFSIZE),"utf-8")   #typecast from byte to UTF-8
                    wifiname_and_psw = data.split(",")                #first part = networkname, second part = psw            

                    if not data:
                        break
                    if (wifiname_and_psw[0] != '' and wifiname_and_psw[1] != '' and wifiname_and_psw[2] != ''):# no empty fields
                        wait_in_loop = 0                

        except KeyboardInterrupt:
            print ("do nothing")


    read_hostapd_file = open("/etc/hostapd/hostapd.conf","r")

    lines = read_hostapd_file.readlines()# reading actual psw and wifi name stored in hostapd file

    read_hostapd_file.close()

    wifi_psw_currenthostapd = lines[10].split("=")                    # reading current wifi password/ ends with \n
    wifi_psw_currenthostapd = wifi_psw_currenthostapd[1]



    if wifiname_and_psw[0] == "Psw":   #changing Psw

        wifi_new_psw = wifiname_and_psw[2]+"\n"
        wifi_psw_current_user = wifiname_and_psw[1]+"\n"# current password send by user
        
        
        if wifi_psw_current_user == wifi_psw_currenthostapd:
            wifi_psw_hostapdvar = "wpa_passphrase="
            lines[10] = wifi_psw_hostapdvar+wifi_new_psw
            write_hostapd_file = open("nextfile.conf","w+")  # open hostapd file to write new wifi name
            
            for count in range (0,14):
                write_hostapd_file.write(lines[count])# write new wifi name to file
            
            write_hostapd_file.close()# close hostapd file
            clientsocket.send(bytes("change succefull","utf-8"))
            os.system("sudo cp /home/pi/Dokumente/nextfile.conf /etc/hostapd/hostapd.conf")   # resetting old network configuration
            os.system("sudo systemctl stop hostapd")#ending hostapd if password by user was correct







    if wifiname_and_psw[0] == "Name":
        net_ssid = "ssid="
        wifi_current_psw = wifiname_and_psw[2]+"\n"# copying new password
            
        if wifi_current_psw == wifi_psw_currenthostapd:
            lines[2] = net_ssid+wifiname_and_psw[1]+"\n"     # change ssid name in lines[]
            write_hostapd_file = open("nextfile.conf","w+")  # open hostapd file to write new wifi name

            for count in range(0,14):
                write_hostapd_file.write(lines[count])# write new wifi name to file
            
            write_hostapd_file.close()# close hostapd file
            clientsocket.send(bytes("change succefull","utf-8"))
            os.system("sudo cp /home/pi/Dokumente/nextfile.conf /etc/hostapd/hostapd.conf")   # resetting old network configuration
            os.system("sudo systemctl stop hostapd")#ending hostapd if password by user was correct
        
        
        
        
        
# main Program
input_pin = 18
pin_detection_init(input_pin)
os.system("sudo systemctl start hostapd")   #activate accesspoint
os.system("sudo pkill uv4l")# beenden des Streams
en_uv4l_start = 0

backlight_connected = 0 # bei Ueberwachen des Ruecklichts, manuell backlight_connected =  1 setzen- ansonsten backlight_connected = 0


while True:
    
    if(GPIO.input(input_pin) == backlight_connected):# solange rueckwaertsgang eingelegt / Wenn Ueberwachung backlight_connected =1 muss input_pin =1
        os.system("sudo systemctl start hostapd")   #activate accesspoint
        print("Rücklicht detected")
        
        if en_uv4l_start == 0:
            os.system("sudo service uv4l_raspicam restart")# starten des Streams
            en_uv4l_start = 1
       
        server_communication()
        

        
    if(GPIO.input(input_pin) == ~backlight_connected):
        os.system("sudo pkill uv4l")# beenden des Streams

        
    else:
        print("Not pushed")
        

