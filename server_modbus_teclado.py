from pymodbus.datastore import (
    ModbusBaseDeviceContext,
    ModbusSequentialDataBlock,
    ModbusServerContext
)
from pymodbus.server import StartTcpServer,ServerStop
import threading
import time
from pynput import keyboard


server_running = False

lista_archivo = []
def lectura_archivo():
    global lista_archivo
    try:
        lista_archivo.clear()
        with open("/home/icam-540/CONFISISTEMA.txt","r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.replace('\n','')
                linea_p = validacion_caracteres_linea(linea)
                #if linea_p != '':
                print(linea_p)
                ascii = conversion_str_ASCII(linea_p)
                print(ascii)
                lista_archivo.append(ascii)
    except:
        print("Error lectura")

def actualizar_linea_archivo(linea,valor):
    global lista_archivo
    try:
        lista_archivo.clear()
        with open("/home/icam-540/CONFISISTEMA.txt","r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()

        while len(lineas) <= linea:
            lineas.append("\n")
            
        lineas[linea] = valor + "\n"
        with open("/home/icam-540/CONFISISTEMA.txt","w", encoding="utf-8") as archivo:
            archivo.writelines(lineas)
        print("Modificacion linea Archivo")
        asignacion_direccion_lectura_archivo()
    except:
        print("Error lectura")

server_running = False

def validacion_caracteres_linea(linea):
    
    count = len(linea)
    if count > 10 or count == 0:
        return ''
    else:
        return linea

def conversion_str_ASCII(texto):
    ascii = [ord(char) for char in texto]
    return ascii

def conversion_ASCII_str(list_ascii):
    texto = ''.join(chr(asc) for asc in list_ascii)
    texto = texto.replace('\x00','')
    return texto


def on_press(key):
    global server_running
    try:
        print("PRESIONADA", key.char)
    except:
        print("ESPECIAL",key)

    if key == keyboard.Key.esc:
        try:
            ServerStop()
            print('Server Cerrado')
            server_running = False
        except:
            server_running = True
            pass

    elif key == keyboard.Key.end:
        try:
            thread_server = threading.Thread(target=inicio_Server,daemon=True)
            thread_server.start()
            server_running = True
        except:
            pass
    elif key== keyboard.Key.backspace:
        try:
            consultar_holding_registers(context,0,10)
            server_running = True
        except:
            pass
    else:
        server_running = True
                

def limpiar_holding(context,address,values):
    context[0].setValues(3,address,values)

def enviar_holding_registers(context, address,values):
    context[0].setValues(3,address,values)

def consultar_holding_registers(context, address,values):
    context[0].getValues(3,address,values)
    context[0].getValues(4,address,values)

def inicio_Server():
    
    try:
        print('Inicio Server')
        StartTcpServer(context, address=("192.168.0.43", 1502))
    except:
        print('Server ya esta iniciado')
        pass

def escuchar_Teclado():
    with keyboard.Listener(on_press=on_press) as Listener:
        Listener.join()


def actualizar():
    global lista_archivo
    i = 0
    while True:
        lectura_archivo()
        if i == 0:
            address_a = 0
        else:
            address_a = i * 10
        enviar_holding_registers(context,address_a,lista_archivo[i])
        time.sleep(15)
        i+=1
        if i == len(lista_archivo):
           i = 0
        time.sleep(5)


def asignacion_direccion_lectura_archivo():
    global lista_archivo
    lectura_archivo()
    i = 0
    while i < len(lista_archivo):
        if i == 0:
            address_a = 0
        else:
            address_a = i * 10
        enviar_holding_registers(context,address_a,lista_archivo[i])
        time.sleep(0.1)
        i+=1



class MyDevice(ModbusBaseDeviceContext):


    
    def __init__(self):

        self.coils = ModbusSequentialDataBlock(0, [0]*1200)
        self.holding = ModbusSequentialDataBlock(0, [10]*1200)
        self.input = ModbusSequentialDataBlock(0, [10]*1200)

    def getValues(self, fc_as_hex, address, count=1):

        if fc_as_hex == 1:  # coils
           return print(self.coils.getValues(address, count))

        if fc_as_hex == 3:  # holding registers
          fc_3 = self.holding.getValues(address, count)
          print("FC3" , fc_3)
          return self.holding.getValues(address, count)
        
        if fc_as_hex == 4:  # input registers
          return print(self.holding.getValues(address, count))
    
        if fc_as_hex == 6:  
          fc_6 = self.holding.getValues(address, count)
          print("FC6 " , fc_6)
          return self.holding.getValues(address, count)
        
        if fc_as_hex == 16:  
          fc_16 = self.holding.getValues(address, count)
          print("FC6: " , fc_16)
          return self.holding.getValues(address, count)
        

    def setValues(self, fc_as_hex, address, values):

        if fc_as_hex == 1:
            self.coils.setValues(address, values)

        if fc_as_hex == 3:
            print("Direccion de Inicio: ", address)
            print("Valores: ", values)
            self.holding.setValues(address, values)

        if fc_as_hex == 6:
            print("FC6 Write Single Register")
            print("Direccion de Inicio: ", address)
            print("Valores: ", values)
            self.holding.setValues(address, values)

        if fc_as_hex == 16:
            print("FC16 Write Multiple Register")
            print("Direccion de Inicio: ", address)
            print("Valores: ", values)

            
            if address % 10 == 0:
                linea_a = address // 10
                texto_asii= conversion_ASCII_str(values)
                print("Texto: ", texto_asii)
                actualizar_linea_archivo(linea_a,texto_asii)

            self.holding.setValues(address, values)

device = MyDevice()

context = ModbusServerContext(devices=device, single=True)

thread_server = threading.Thread(target=inicio_Server,daemon=True)
thread_server.start()


#thread_update = threading.Thread(target=actualizar,daemon=True)
#thread_update.start()

thread_teclado = threading.Thread(target=escuchar_Teclado,daemon=True)
thread_teclado.start()

asignacion_direccion_lectura_archivo()
while True:   
    time.sleep(1)