import serial, time
import os
import RPi.GPIO as GPIO
import sqlite3
import subprocess
import Connectpacket
import Publishpacketg
import global_init_file


# Creating Class GpioPins.
class Gpio():

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

    def read(self, pin_number):
        GPIO.setup(pin_number, GPIO.IN)
        i = GPIO.input(pin_number)
        return i

    def write(self, pin_number, value):
        GPIO.setup(pin_number, GPIO.OUT)
        GPIO.output(pin_number, value)

########## GPIO Test ##########
        
#create object of gpio class:

#g = Gpio()
#print(g.read(40))
#g.write(33,1)

################################
        
# Creating Class Digital I/O.
class Digital_io():
    def read_inputs(self):
        g = Gpio()
        a = g.read(16)
        b = g.read(18)
        c = g.read(38)
        d = g.read(40)
        return {"1:16":a,"2:18":b,"3:38":c,"4:40":d}
        
    def write_output(self,dio_number,value):
        g = Gpio()
        if(dio_number == 1):
            g.write(32,value)
            return 1
        elif(dio_number == 2):
            g.write(36,value)
            return 1
        else:
            print("Invalid Digital Output Pin Number")
            return 0
        
########## Digital IO Test ##########
        
#create object of  class:

#d = Digital_io()
#print(d.read_inputs())
#d.write_output(1,0)
#d.write_output(2,0)

################################
            

# Creatin Class Rtc.
class Rtc():

    def set_system_time(self, time):
        os.system('sudo date +"%y-%m-%d %H:%M:%S" --set="' + time + '"')

    def read_time(self):
        p = subprocess.Popen("sudo hwclock --rtc=/dev/rtc0 --get", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        tim = str(output)
        #print(tim[2:21])
        return (tim[2:21])

    def write_system_time_to_rtc(self):
        os.system("sudo hwclock --rtc=/dev/rtc0 -w")

    def write_time(self, time):
        Rtc.set_system_time(time)
        Rtc.write_system_time_to_rtc()

    def write_rtctime_to_system(self):
        x = Rtc.read_time(self)
        Rtc.set_system_time(self, x)
        
########## RTC Test ##########

#r = Rtc()
#rtc_time = r.read_time()
#print(rtc_time)
#r.set_system_time("2019-07-04 17:18:45")
#r.write_system_time_to_rtc()
#r.write_time("2019-07-04 17:18:45")
#r.write_rtctime_to_system()


################################ 
        
class Gsm():
    
    connected = 0
    gsm_port = serial.Serial("/dev/ttyS0",9600,timeout=0.05)
    at = []
    apn = "airtelgprs.com"
    ip = "35.193.221.225"
    packet = ""
    at.append(['AT Communication:','AT+CMEE=1',b"OK"])
    #cn 1
    at.append(['Disable Echo:','ATE0',b"OK"])
    #cn 2
    at.append(['Sim Activity Status:','AT+CPAS',b"CPAS: 0"])
    #cn 3
    at.append(['Network Registered?:','AT+CREG?',b"CREG: 0,1"])
    #cn 4
    at.append(['GPRS Network Registration?:','AT+CGREG?',b"CGREG: 0,1"])
    #cn 5
    at.append(['GPRS Attached?:','AT+CGATT?',b"CGATT: 1"])
    #cn 6
    at.append(['PDP context defined?:','AT+CGDCONT?',b"OK"])
    #cn 7
    at.append(['Define PDP context:','AT+CGDCONT=1,"IP","'+apn+'"',b"OK"])
    #cn 8
    at.append(['PDP context active?:','AT+CGACT?',b"OK"])
    #cn 9
    at.append(['Activate PDP context:','AT+CGACT=1',b"OK"])
    #cn 10
    at.append(['Link Created?:','AT+MIPCALL?',b"OK"])
    #cn 11
    at.append(['Create Link:','AT+MIPCALL=1,"'+apn+'"',b"MIPCALL:"])
    #cn 12
    at.append(['Ping Google:','AT+MPING=1,"8.8.8.8"',b"OK"])
    #cn 13
    at.append(['Disconnect link:','AT+MIPCALL=0,"'+apn+'"',b"OK"])
    #cn 14
    at.append(['Deactivate PDP Context:','AT+CGACT=0',b"OK"])
    #cn 15
    at.append(['Detach GPRS:','AT+CGATT=0',b"OK"])
    #cn 16
    at.append(['Attach GPRS:','AT+CGATT=1',b"OK"])
    #cn 17
    at.append(['Closed sockets:','AT+MIPOPEN?',b"1,3,4"])
    #cn 18
    at.append(['Open Socket:','AT+MIPOPEN=2,8080,"106.51.80.247:8080",1883,0',b"MIPOPEN: 2,1"])
    #cn 19
    at.append(['Send to buffer:','AT+MIPSEND=2,"'+packet+'"',b"OK"])
    #cn 20
    at.append(['Push to TCP Stack:','AT+MIPPUSH=2',b"RTCP"])
    #cn 21
    at.append(['Delete PDP context:','AT+CGDCONT=0',b"OK"])
    #cn 22
    at.append(["disable sleep mode:" , "ATS24=0",b"OK"])
    
    def write_AT(self,at_command_number):
        print(Gsm.at[at_command_number][0]+"\n")
        print(Gsm.at[at_command_number][1]+"\n")
        Gsm.gsm_port.write((Gsm.at[at_command_number][1]+'\r').encode('utf-8'))
    
    def read_rx(self,at_command_number):
        counter = 0
        rx = b""
        while(1):
            curr_rx = Gsm.gsm_port.read(100)
            
            if(rx.find(Gsm.at[at_command_number][2])!=-1):
                print(rx)
                return 1
            else:
                if(counter>=400):
                    print(rx)
                    return 0
                if(rx.find(b"ERROR")!=-1):
                    print(rx)
                    return 0
                rx+=curr_rx
            counter+=1
                
    
    def execute_AT(self,at_command_number):
        Gsm.write_AT(self,at_command_number)
        return(Gsm.read_rx(self,at_command_number))
    
    def disconnect_gprs(self):
        return Gsm.execute_AT(self,15)
        
    def connect_gprs(self):
        return Gsm.execute_AT(self,16)
    
    def gsm_comm_test(self):
        if(Gsm.execute_AT(self,0)):
            if(Gsm.execute_AT(self,1)):
                if(Gsm.execute_AT(self,2)):
                    if(Gsm.execute_AT(self,3)):
                        if(Gsm.execute_AT(self,4)):
                            if(Gsm.execute_AT(self,5)):
                                return 1
                            else:
                                return 0       
                        else:
                            return 0
                    else:
                        return 0
                else:
                    return 0
            else:
                return 0
        else:
            return 0
        
    
    def cloud_connect(self):
        
        if(Gsm.execute_AT(self,7)):
            if(Gsm.execute_AT(self,9)):
                if(Gsm.execute_AT(self,11)):
#                        time.sleep(1)
                    if(Gsm.execute_AT(self,18)):
#                            time.sleep(2)
                        if(Gsm.execute_AT(self,17)):
                            return 1
                        else:
                            return 0
                    else:
                        return 0
                else:
                    return 0
            else:
                return 0 
        else:
            return 0 
       
    
    def mqtt_connect(self):
        cp = Connectpacket.generateconnectpacket()
        print(cp)
        Gsm.at[19][1]='AT+MIPSEND=2,"'+cp+'"'
        
        
        if(Gsm.execute_AT(self,19)):
            if(Gsm.execute_AT(self,20)):
                return 1
            else:
                return 0
        else:
            return 0
        
    
    def mqtt_publish(self,data):
#        global_init_file.msg = data
        pp = Publishpacketg.generatepublishpacket(data)
        print(pp)
        Gsm.at[19][1]='AT+MIPSEND=2,"'+pp+'"'
        
        
        if(Gsm.execute_AT(self,19)):
            time.sleep(2)
            if(Gsm.execute_AT(self,20)):
                return 1
            else:
                return 0
        else:
            return 0
        
#    def write_gpio(self, pin_number, value):
#        GPIO.setwarnings(False)
#        GPIO.setmode(GPIO.BOARD)
#        GPIO.setup(pin_number, GPIO.OUT)
#        GPIO.output(pin_number, value)
#
#        
#        
#    def wake_up(self):
#        Gsm.write_gpio(self,37, 1)
#        time.sleep(1)
#        Gsm.write_gpio(self,37, 0)
#        time.sleep(1)
#
#        Gsm.execute_AT(self,22)
#        
#        
#        time.sleep(3)
    
    def connect(self):
        
        if(Gsm.gsm_comm_test(self)):
            if(Gsm.cloud_connect(self)):
                if(Gsm.mqtt_connect(self)):
                    return 1
                else:
                    Gsm.disconnect_gprs(self)
                    Gsm.connect_gprs(self)
                    
            else:
                Gsm.disconnect_gprs(self)
                Gsm.connect_gprs(self)
                
        else:
            Gsm.disconnect_gprs(self)
            Gsm.connect_gprs(self)
                
        
        return 0
    
    def send_data(self,data):
            
        if(Gsm.mqtt_publish(self,data)):
            return 1
        else:
            Gsm.disconnect_gprs(self)
            Gsm.connect_gprs(self)
                
            
        return 0
    
    def master(self,data):
        
        while(True):
            if(Gsm.connected == 0):
                if(Gsm.connect(self)):
                    Gsm.connected = 1
                    if(Gsm.send_data(self,data)):
                        return 1
                    else:
                        Gsm.connected = 0
                        Gsm.disconnect_gprs(self)
                        Gsm.connect_gprs(self)
                        return 0
                        
                else:
                    Gsm.connected = 0
#                    print("Waking up...")
#                    Gsm.wake_up(self)
                    return 0
            else:
                if(Gsm.send_data(self,data)):
                    return 1
                else:
                    Gsm.connected = 0
                    Gsm.disconnect_gprs(self)
                    Gsm.connect_gprs(self)
                    return 0
                
                
        
            
        
########## GSM Test ##########

g = Gsm()
g.execute_AT(0)
#g.master(str(d.read_inputs()))
#g.master(str(d.read_inputs()))
#g.master(str(d.read_inputs()))
#g.master(str(d.read_inputs()))


################################    
    
