from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusSequentialDataBlock,
    ModbusServerContext
)
from pymodbus.server import StartTcpServer,ServerStop
import threading
import time
import subprocess
import os



server_running = False

lista_archivo = []
def lectura_archivo():
    global lista_archivo
    try:
        lista_archivo.clear()
        with open("/home/icam-540/CONFISISTEMA_EL.txt","r", encoding="utf-8") as archivo:
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
        with open("/home/icam-540/CONFISISTEMA_EL.txt","r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()

        while len(lineas) <= linea:
            lineas.append("\n")
            
        lineas[linea] = valor + "\n"
        with open("/home/icam-540/CONFISISTEMA_EL.txt","w", encoding="utf-8") as archivo:
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
        StartTcpServer(context, address=("192.168.0.27", 1502))
    except:
        print('Server ya esta iniciado')
        pass



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
        
proceso_yolo = None

def iniciar_yolo(script_path):
    global proceso_yolo

    if proceso_yolo is not None and proceso_yolo.poll() is None:
        print("⚠️ El proceso ya está en ejecución")
        return

    env = os.environ.copy()
    env["PYTHONPATH"] = "/opt/advantech/sdk"
    env["LB_LIBRARY_PATH"] = "/opt/advantech/sdk:/opt/advantech/sdk/CamNavi2:/opt/advantech/sdk/bin:/usr/lib/aarch64-linux-gnu"
    env["GST_PLUGIN_PATH"] = "/opt/advantech/sdk/gst"
    env["DISPLAY"] = ":0"

    try:
        proceso_yolo = subprocess.Popen(
            ["/usr/bin/python3", "-u", script_path],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"✅ Script iniciado correctamente: {script_path} (PID: {proceso_yolo.pid})")
    except Exception as e:
        print(f"❌ Error al iniciar script: {e}")
        proceso_yolo = None



class MyDevice(ModbusDeviceContext):


    
    def __init__(self):

        self.coils = ModbusSequentialDataBlock(1, [0]*10)
        self.holding = ModbusSequentialDataBlock(1, [10]*10)
        self.input = ModbusSequentialDataBlock(1, [10]*10)

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

asignacion_direccion_lectura_archivo()

thread_yolo = threading.Thread(target=iniciar_yolo, args=("/home/icam-540/Proyectos/ICAM_540_ELEC_SERVICIO/Video_contnuo_modbus_cl.py",), daemon=True)
thread_yolo.start()

while True:
    time.sleep(1)