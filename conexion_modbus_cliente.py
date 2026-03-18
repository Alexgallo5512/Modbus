import pymodbus
from pymodbus.client import ModbusTcpClient
import inspect


print(pymodbus.__version__)
client = ModbusTcpClient('192.168.0.210', port=502)
unitIdentifierSlave =[0x01]
print(inspect.signature(client.read_holding_registers))

estado = client.connected
if False == estado: 
    client.connect()
    result = client.read_holding_registers(0,count=4,device_id=1)
    print(result)
else:
    print("El cliente esta abierto" + estado)

def funcion_consulta_datos_wise_cables():
    global client
    global unitIdentifierSlave

    try:

        k = 0 
        valores_txt = []
        boxes_cable = [[],[],[]]
        for slave_ in unitIdentifierSlave:
            #print(slave_)
            #print(client.read_holding_registers.__doc__)
            result = client.read_holding_registers(0, count=4,device_id=slave_)
            if result.isError():
                raise Exception("Error leyendo registros")
            serverResponse = result.registers

            boxes_cable[k]= []
            for value in serverResponse:
                boxes_cable[k].append(value)

            valores_txt.append([
                str(serverResponse[0]),
                str(serverResponse[1]),
                str(serverResponse[2]),
                str(serverResponse[3])
            ])

            k += 1

        Txt_Indice_0_Cable = valores_txt[0][0]
        Txt_Indice_1_Cable = valores_txt[0][1]
        Txt_Indice_3_Cable = valores_txt[0][2]
        Txt_Indice_2_Cable = valores_txt[0][3]

        Txt_Contador_Cable = Txt_Indice_3_Cable
        print("")
        print("Indice 0:", Txt_Indice_0_Cable)
        print("Indice 1:", Txt_Indice_1_Cable)
        print("Indice 2:", Txt_Indice_2_Cable)
        print("Indice 3:", Txt_Indice_3_Cable)
        print("")

        num_pos = 0
        bytes_0 = int(valores_txt[num_pos][0])
        bytes_1 = int(valores_txt[num_pos][1])
        resultado_lsb_sin_signo_a = bytes_0
        resultado_msb_sin_signo_a = bytes_1

        conteo_wise_a = (resultado_msb_sin_signo_a << 16) | resultado_lsb_sin_signo_a

        bytes_2 = int(valores_txt[num_pos][2])
        bytes_3 = int(valores_txt[num_pos][3])
        resultado_lsb_sin_signo_b = bytes_2
        resultado_msb_sin_signo_b = bytes_3

        conteo_wise_b = (resultado_msb_sin_signo_b << 16) | resultado_lsb_sin_signo_b
        print(conteo_wise_b)

    except Exception as exc:

        print("334567 Exception Reading values from Server:", str(exc))
        print("Conexion fallida Cable")




i = 0
while i < 31:
    funcion_consulta_datos_wise_cables()
    i+=1





