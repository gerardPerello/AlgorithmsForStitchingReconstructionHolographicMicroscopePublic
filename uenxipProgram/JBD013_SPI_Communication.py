import os

from display_general import display_general

# Hay que especificar la variable del sistema para saber qué placa tenemos. Si no la siguiente línea da error
os.environ["BLINKA_FT232H"] = '1'
# esto es la libreria de mi placa Adafruit FT232H Breakout.
import board

from pyftdi.spi import SpiController  # Libreria de ftdi, util para la comunicacion via SPi
import digitalio  # tambien de mi adafruit, son propias de CircuitPython!!
import time  # libreria para meter delays

COLUMNS = 640#640
ROWS = 480#480
MAX_ROWS = 100#120

DUMMY = 0x00  # constante para meter dummy bytes cuando sea necesario y saber identificarlos dentro de la list
PIX_OFF = 0x00  # PIXEL APAGADO
PIX_ON = 0xFF  # PIXEL PARA ENCENDER CON EL BRILLO A TOPE EL PIXEL SELECCIONADO MEDIANTE LA DIRECCIÓN DADA Y EL
# SIGUIENTE!
PIX_CLOSING = 0xF0  # PICEL PARA CERRAR TRAMA O PARA ENCENDER UNICAMENTE EL DESEADO DADO POR LA DIRECCION

spi = SpiController()
spi.configure('ftdi://ftdi:232h/1')
# Escojo cs=0 porque solo tengo 1 slave! Frecuencia pongo 32MHz, la maxima del  uDisplay, a la realidad irá a 31MHz
slave = spi.get_port(cs=0, freq=32E6, mode=0)

# PROTOCOLO INCIIACION DE LOS REGULADORES A PARTIR DE PONER SUS ENABLE A 3v3:
# definicion de los pines que los activan como outputs para poder controlarlos
EN_LS = digitalio.DigitalInOut(board.C0)
EN_LS.direction = digitalio.Direction.OUTPUT

EN_12 = digitalio.DigitalInOut(board.C1)
EN_12.direction = digitalio.Direction.OUTPUT

EN_VSS = digitalio.DigitalInOut(board.C2)
EN_VSS.direction = digitalio.Direction.OUTPUT


def POWER_ON():  # PROTOCOLO POWER UP  (DATASHEET PAG. 53 -> 8.2)

    # protocolo:
    # primero se inicializa el regulador de 2.5V, luego minimo 1ms despues se enciende el de 1,2V
    time.sleep(1.5E-3)  # 1.5ms delay, no haria falta pero lo pongo igual!
    EN_12.value = True

    # luego de incializa minimo 5ms despues el de VSS que es el que alimenta los catodos
    time.sleep(7E-3)  # delay de 7ms
    EN_VSS.value = True

    # finalmente van las señales del SPI, de manera que las tramas tienen que empezar a enviarse miinimo 5ms despues
    time.sleep(5E-3)

    # activo por nivel bajo, es decir, necesito poner a 0 esa entrada para que se active mi level shifter!
    EN_LS.value = False
    time.sleep(5E-3)


def POWER_OFF():  # PROTOCLO POWER OFF (DATASHEET PAG. 53 -> 8.2)
    # PARA APAGAR EL EQUIPO LO PRIMERO QUE HAGO ES APAGAR LAS COMUNICACIONES SPI
    EN_LS.value = False
    time.sleep(2E-3)  # DELAY 2MS
    EN_VSS.value = False  # Seguidamente apago la alimentacion de los LEDs
    time.sleep(2E-3)  # DELAY 2MS
    EN_12.value = False
    time.sleep(2E-3)


def sync():  # SYNC (DATASHEET PAG. 32)
    slave.write([0x97])  # sy
    time.sleep(1E-3)  # delay obligatorio despues del sync


def rdid():  # READ IDENTIFICACION ID (DATASHEET PAG. 29)

    # utilizo exchange por que asi puedo leer lo que me devuelve el slave (MISO), este tiene que devolverme:
    # 0xBD 0x40 0x10
    sl = slave.exchange([0x9F], 3)  # INTRUCCION RDID, ME ESPRO 24BITS DE ID INFORMATION


def ruid():  # READ UNIC ID (DATASHEET PAG. 30,31)

    RUID = slave.exchange([0xAB], 15)  # instruccion RUID, ME ESPERO 120 BITS DE UID INFORMATION


def write_en():  # WRITE ENABLE INSTRUCTION (DATASHEET PAG. 44)
    slave.write([0x06])


def write_dis():  # WRITE DISABLE INSTRUCION (DATASHEET PAG. 44)
    slave.write([0x04])


def disp_dis():  # DISPLAY DISABLE INSTRUCTION (DATASHEET PAG. 33)
    slave.write([0xA9])
    sync()


def judgement(
        brillo):  # Funcion de juicio, la cual determina el valor del pixel en funcion del ruido escogido, los valores iran de 0-15 (0 to F (hex)), cualquier otro valor no sera
    # valido y hará que en el pixel pongamos un 0!

    if 0 <= brillo < 16:
        return brillo * 0x10
    return 0x00


def judgement_many(brillos):
    n = len(brillos)
    if n % 2 == 1:
        brillos.append(0)

    pixvalues = [brillos[i] * 0x10 + brillos[i + 1] for i in range(0, n, 2)]
    return pixvalues


"""
Funcion para escribir en la caché de forma rápida sin ir pixel a pixel, lo bueno de esta funcion es que nos 
permite escoger la fila y columna desde la que queremos empezar a escribir a partir de esta generamos una lista de 
65274 bytes, con el pixel que nosotros habremos escogido a partir del brillo seleccionado. Dejamos libres igualmente 
6 bytes en la lista los cuales corresponden a la instruccion de escribir via SPI en la caché (DATASHEET PAG. 38), 
a la direccion que nosotros habremos escogido mediante las filas y columnas (podemos observar que con la funcion 
.to_bytes hacemos que esta direccion tenga 3 bytes (DATASHEET PAG. 21)) y un byte dummy. Esto que hemos hecho nos 
permite llenar por ejemplo si queremos la caché de 4 tiradas como haremos en la funcion CLEAN_CACHE! (MIRAR PARA 
ENTENDER! :D) 
"""


def WRITE_CACHE_DATA(row, col, data):
    n = len(data)
    blocks_written = 0

    while True:

        start = blocks_written * MAX_ROWS * COLUMNS

        if start > n:
            break

        end = min(n, start + MAX_ROWS * COLUMNS)

        addr = [col | ((row + blocks_written * MAX_ROWS) << 10)]
        baddr = addr[0].to_bytes(3, 'big')
        pixvalues = judgement_many(data[start:end]) + [0]
        data2send = [0x02, baddr[0], baddr[1], baddr[2], DUMMY] + pixvalues
        slave.write(data2send)
        blocks_written += 1

    sync()


def WRITE_CACHE(row, col, num, brillo):
    pixel = judgement(brillo)
    data = [pixel for _ in range(num)]
    WRITE_CACHE_DATA(row, col, data)


def WRITE_IMAGE(im):
    pixvalues = im.flatten().tolist()
    WRITE_CACHE_DATA(0, 0, pixvalues)


"""
Funcion para escribir en la caché un solo pixel. Mismo funcionamiento que la funcion anterior pero ahora solo 
lleno a lista con un solo pixel, luego concateno las dos listas y escribo Podemos ver que escogemos la fila y columna 
 donde se encuentra el pixel, así como el brillo que querremos que tenga este! 
"""


def WRITE_PIX(row, col, brillo):
    pixel = judgement(brillo)
    addr = [col | (row << 10)]
    baddr = addr[0].to_bytes(3, 'big')
    pixvalues = [pixel]
    data2send = [0x02, baddr[0], baddr[1], baddr[2], DUMMY] + pixvalues
    slave.write(data2send)
    sync()


# Funcion para llenar toda la caché de ceros, hacemos uso de nuestra funcion WRITE_CACHE y creamos bursts de 65275
# BYTES que escogemos que sean ceros
def CLEAN_CACHE():
    WRITE_CACHE_DATA(0, 0, [0 for _ in range(ROWS * COLUMNS)])

def set_luminance(l):
    slave.write([0x36, l // 0x10, l % 0x10])

def FAST_INIT_PANEL():
    write_en()
    STATUS_REG1 = slave.exchange([0x01, 0x10, 0x04], 0)  # pongo a 0 el bits de enable demura (DEMURA DISABLED)
    # GAMMA DISABLED y refresh frequency 75Hz

    STATUS_REG2 = slave.exchange([0x31, 0x08], 0)
    STATUS_REG3 = slave.exchange([0x57, 0x01], 0)
    LUMINANCE = slave.exchange([0x36, 0xFF, 0xFF], 0)
    CURRENT_REG = slave.exchange([0x46, 0x3F], 0)

    # Limpio la cache, es decir la lleno de ceros.
    CLEAN_CACHE()
    sync()
    write_dis()

    # ¡El offset cubre 24x20 de manera que el centro estarà en 12x10, lo pongo en el centro!
    write_en()
    slave.write([0xC0, 0x00, 0x00])
    sync()
    slave.write([0x0C0, 0x00, 0x014])
    sync()
    slave.write([0xC0, 0x18, 0x00])
    sync()
    slave.write([0xC0, 0x18, 0x14])
    sync()

    slave.write([0xC0, 0x00, 0x00])  # center offset 2'd12 = 2'h18 ,  2'd10 = 2'h0A
    sync()
    write_dis()


def disp_en():
    slave.write([0xA3])  # display enable, fijarnos si es necssario el hecho de tener que poner un sync despues
    sync()


def init_from_0():
    POWER_ON()
    rdid()
    ruid()
    FAST_INIT_PANEL()
    disp_en()
    sync()


def WRITE_PIX2PIX_ALLCACHE(row_init, row_final, col_init, col_final, brillo):
    # CLEAN_CACHE()
    for row in range(row_init, row_final):
        for col in range(col_init, col_final):
            WRITE_PIX(row, col, brillo)


def prueba():
    WRITE_PIX2PIX_ALLCACHE(0, 25, 0, 50, 15)

    WRITE_PIX2PIX_ALLCACHE(0, 25, 428, 453, 10)

    WRITE_PIX2PIX_ALLCACHE(320, 353, 0, 25, 7)

    WRITE_PIX2PIX_ALLCACHE(320, 353, 428, 453, 5)


def cuadrado(row_init, row, col_init):
    for row in range(row_init, row):
        WRITE_CACHE(row, col_init, 107, 15)
    sync()
    CLEAN_CACHE()


def disco_mode(delay):
    j = 0
    while True:
        cuadrado(0, 160, 0)
        time.sleep(delay)
        cuadrado(160, 320, 214)
        time.sleep(delay)
        cuadrado(320, 480, 428)
        time.sleep(delay)
        cuadrado(0, 160, 428)
        time.sleep(delay)
        cuadrado(160, 320, 214)
        time.sleep(delay)
        cuadrado(320, 480, 0)
        time.sleep(delay)
        cuadrado(0, 160, 214)
        time.sleep(delay)
        cuadrado(320, 480, 214)
        time.sleep(delay)
        cuadrado(320, 480, 428)
        time.sleep(delay)
        while j != 2:
            CKECK1 = slave.exchange([0x15], 0)
            sync()
            time.sleep(0.1)
            CKECK2 = slave.exchange([0x16], 0)
            sync()
            time.sleep(0.1)
            j += 1
        j = 0


def test(cycles=-1):
    done = 0

    while cycles < 0 or done < cycles:
        CKECK1 = slave.exchange([0x15], 0)
        sync()
        time.sleep(0.1)
        CHECK2 = slave.exchange([0x16], 0)
        sync()
        time.sleep(0.1)
        done += 1


def heartbit(cycles=100, delay=0.1):
    addr = [10 | (10 << 10)]
    baddr = int(addr[0]).to_bytes(3, 'big')

    for _ in range(cycles):
        data2send = [0x02, baddr[0], baddr[1], baddr[2], DUMMY] + [0xF0]
        slave.write(data2send)
        sync()

        time.sleep(delay)

        data2send = [0x02, baddr[0], baddr[1], baddr[2], DUMMY] + [0x00]
        slave.write(data2send)
        sync()

class JBD_013_SPI_display(display_general):

    def __init__(self):
        self.max_intensity = 15
        self.intensity_value = 15

    def turn_on_led(self, row, col):
        WRITE_PIX(row,col,self.intensity_value)

    def set_sequence(self, datalist):
        pass

    def turn_off_led(self, row, col):
        WRITE_PIX(row,col,0)

    def clear_display(self):
        CLEAN_CACHE()

    def turn_on(self):
        init_from_0()
        #TODO LED CONTROL PARA VER SI ENCIENDE

    def turn_off(self):
        POWER_OFF()

    def restart(self):
        POWER_OFF()
        init_from_0()

    
