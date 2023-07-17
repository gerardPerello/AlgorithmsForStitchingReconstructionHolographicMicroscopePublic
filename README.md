# uenxip - Stitcher Programs

- Soportado en linux con Python3 ;
- Necesario soporte de camara Iberoptics, mirar especificaciones https://github.com/TheImagingSource/tiscamera;
- Soporte para dos tipos de display==> JBD013-SPI, Display por HDMI con pygame;


![](https://upload.wikimedia.org/wikipedia/ca/thumb/2/2c/Logotip_UB.svg/800px-Logotip_UB.svg.png?20151126150328)


**Table of Contents**

- [uenxip - Stitcher Programs](#uenxip---stitcher-programs)
  * [Descarga del proyecto.](#descarga-del-proyecto)
  * [Instalacion de Python y Librerias.](#instalacion-de-python-y-librerias)
  * [Instalacion de la Camara.](#instalacion-de-la-camara)
  * [Instalacion de display JBD013-SPI](#instalacion-de-display-jbd013-spi)
- [Estructura del proyecto](#estructura-del-proyecto)
  * [uenxip Program](#uenxip-program)
      - [Resumen](#resumen)
      - [Arranque](#arranque)
      - [Manual de Uso](#manual-de-uso)
  * [Stitcher Program](#stitcher-program)
      - [Resumen](#resumen-1)
      - [Arranque](#arranque-1)
      - [Manual de Uso](#manual-de-uso-1)
      - [Funcionalidades](#funcionalidades)
  * [ImagesLibrary](#imageslibrary)
      - [DummySets](#dummysets)
      - [HistorialSets](#historialsets)
- [Informacion para el desarrollador.](#informacion-para-el-desarrollador)
    + [FlowChart](#flowchart)
    + [Sequence Diagram](#sequence-diagram)
    + [End](#end)

# Manual de Instalacion

## Descarga del proyecto.

0. Update del sistema

		sudo apt-get update

1. Comprobar que esta instalado GIT en el ordenador `git --version` , en caso contrario: Instalar GIT en el ordenador.  https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
2. Descargar el proyecto en la **carpeta de destino**

		git clone https://github.com/gerardPerello/micProj
	e introducir la cuenta autorizada y su respectiva contraseña.
3. Esperar a que se descargue el proyecto.
----

## Instalacion de Python y Librerias.

1. Comprobar que esta instalado PYTHON3 en el ordenador `python3 --version` , en caso contrario: Instalar PYTHON3 en el ordenador. https://python-guide-es.readthedocs.io/es/latest/starting/install3/linux.html
2. (Opcional) Crear un virtualEnvirontment para el proyecto:

		python3 -m pip install --upgrade pip
		
		pip3 install virtualenv
		
	Y en la **carpeta del proyecto**:
		
		cd micProj
		
		virtualenv env
		
	A continuacion **activamos** nuestro **virtualEnvirontment**
	
		source env/bin/activate
		
	Si queremos salir del entorno virtual, usaremos
	
		deactivate
		
3. Instalar las librerias necesarias

		pip install -r requeriments.txt
		
	Si tenemos algun problema en este paso, revisar las librerias e instalar 1 a 1.
----

## Instalacion de la Camara.

1. Copiar en consola los siguientes comandos.

		git clone https://github.com/TheImagingSource/tiscamera.git
		cd tiscamera
		# only works on Debian based systems like Ubuntu
		sudo ./scripts/dependency-manager install
		mkdir build
		cd build

		cmake -DTCAM_BUILD_ARAVIS=OFF ..

		make
		sudo make install

2. Una vez instalados los drivers de la camara, para comprobar que funciona usa el siguiente comando:

		tcam-capture

Más información en https://github.com/TheImagingSource/tiscamera


## Instalacion de display JBD013-SPI

1. Instalar libusb:

		sudo apt-get install libusb-1.0
		
2. Crear las rules correspondientes. Para ello, usamos el root para crear en la ruta **/etc/udev/rules.d** el archivo con nombre **11-ftdi.rules** y colocamos el siguiente texto (podemos usar el cat o un editor)

		SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6001", GROUP="plugdev", MODE="0666"
		SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6011", GROUP="plugdev", MODE="0666"
		SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6010", GROUP="plugdev", MODE="0666"
		SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6014", GROUP="plugdev", MODE="0666"
		SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6015", GROUP="plugdev", MODE="0666"
		
3. Ejectuar los comandos:
		
		sudo udevadm control --reload-rules
		sudo udevadm trigger
		
4. Intentar colocar el usuario en el usergrup *plugdev*

		sudo adduser $USER plugdev
		
5.  (OPCIONAL) Post install checks:

https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h/troubleshooting

Información extraida de:

https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h/linux
	
https://github.com/eblot/pyftdi/blob/master/pyftdi/doc/installation.rst

Consultar para más respuestas.

### Extras JBD013-SPI: 

LINK para Windows:

https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h/windows

Libreria FTDI, el que se encarga de la comunicación via protocolo SPI:

https://eblot.github.io/pyftdi/api/spi.html

Pagina placa de desarrollo donde se  encuentra el FTDI y hace que se comunique con la PCB:

https://www.adafruit.com/product/2264
https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h

# Estructura del proyecto
![](https://github.com/gerardPerello/micProj/blob/master/assets/DiagramaPrograma.png?raw=true)
## uenxip Program
### Resumen
### Arranque
El arranque del uenxip Program tiene un parametro de entrada para poder decidir que Placa de Leds se usará.
El parametro és **--display=x** donde x=0 ==> SPI display o x=1 ==> HDMI display
Por defecto se pondra x = 0.

Por lo tanto, para arrancar el programa se haría:

		cd micProj
		python uenxipProgram/Main_ControlPanel.py --display=x

Si tenemos cualquier error hay que revisar la instalación o estar seguros de estar usando el environtment de Python correspondiente.

### Manual de Uso
![](https://github.com/gerardPerello/micProj/blob/master/assets/uenxip.png?raw=true)

**1. Ventana de control General**

Ventana des de donde tenemos todas las utilidades para hacer uso del programa.

**2. Ventana de NIM (Visor de Mosaico)**

Ventana donde nos aparecen las imagenes ordenadas en mosaico cuando hacemos un recorrido.

**3. Ventana de CMOS (Visor de Camara)**

Ventana que nos muestra en directo lo que se ve por la camara.

**4. StatusBar**

Barra de Status que nos informa de la situacion del programa i nos informa de errores.

**5. Variables de Barrido**

Variables que se usan para configurar la instrucción de barrido de imagenes.


| | Led Inicial | Salto entre Leds | nº de Leds |
|:-------------------:|---|---|---|
| (X,Y) | Posicion donde Empieza el barrido | Espaciado entre 2 leds consecutivos | Numero de leds barridos |

**6. Ruta de importacion o exportacion de configuracions CSV para variables de barrido.**

Se usa para guardar configuraciones de barrido en un archivo CSV para poder tenerlas e realizarlas de nuevo en un futuro. Pueden modificarse siempre con el botor SAVE. Por otro lado, para editar una configuracion cargada o guardada, hay que marcar el boton EDIT.

**7. Ruta de exportacion donde se guardan las muestras en el barrido, con eleccion de formato.**

Nombre de la carpeta donde se guardaran las imagenes que se realicen en el barrido. Siempre dentro de ImagesLibrary/HistorialSets/.

**8. Boton START.**

Boton para empezar el barrido, se pueden o no guardar las muestras en la ruta (7) segun el checkBox.

**9. Boton STOP**

Boton que para la función de barrido.

**10. Barra de configuracion.**


| | DisplaySelected | Size | SnapButton | Connect Camera | Reset | Open Stitcher Program|
|:-------------------:|---|---|---|---|---|---|
| |Indica el Display Seleccionado* | Indica el RowsXColumns del display seleccionado | Hace una foto | Conecta la camara | Resetea todos los parametros | Abre el programa de Stitching |


![](https://github.com/gerardPerello/micProj/blob/master/assets/uenxipDisplay.png?raw=true)

**11. Luminancia del display SPI**

Variable de Luminancia en caso de que este conectado el display SPI

**12. CurrentBIAS del display SPI**

Variable de CURRENTBIAS en caso de que este conectado el display SPI

**13. Botones de configuracion del Display**


**14. Boton para enviar los parametros 11 y 12 al Display.**


![](https://github.com/gerardPerello/micProj/blob/master/assets/uenxipCamera.png?raw=true)

**15. Selecciona el modelo de camara**

**16. Parametro de Gain de la camara**

**17. Parameto de Exposure de la camara**

**18. Modos de la camara.**

**19. Configuracion de la camara.**

## Stitcher Program
### Resumen
### Arranque
Para arrancar el programa se haría:

		cd micProj
		python StitcherProgram/mainpantalla.py
		
### Manual de Uso

![](https://github.com/gerardPerello/micProj/blob/master/assets/Stitching.png?raw=true)

**1. Visor de MOSAICO / IMAGEN sin IFFT**

Visor con sus opciones de Zoom de la imagen o del mosaico de imagenes sin el IFFT.

**2. Visor de IMAGEN CON IFFT.**

Visor con sus opciones de Zoom del resultado de la funcionalidad IFFT

**3. Barra de Status**

Barra de estado que muestra información sobre el programa y possibles errores.

**4. Botones de carga:**

| | Cargar Imagen | Cargar Set | Restore Last Session |
|:-------------------:|---|---|---|
| | Carga 1 sola imagen, teniendo que seleccionar primero la muestra y luego el fondo | Carga un Set de imagenes, teniendo que seleccionar una carpeta donde se encuentre dentro una carpeta MUESTRAS y otra FONDOS | Restaura la ultima session. |

**5. Formato de importacion y orden de importación.**

**6. Menus**

![](https://github.com/gerardPerello/micProj/blob/master/assets/StitchingParams.png?raw=true)

**7. Variables para el Calculo de valores**

- Sigma sift: En principio no hace falta tocarlo, ver documentación de opencv para más información

- nFeatures: número de puntos clave que se buscan para cada imagen
- % Sift Good: Para cada punto clave, buscaremos en las imágenes vecinas su mejor "pareja" (match). Para saber si el match es bueno, lo compararemos con el segundo mejor, y vemos cuánto mejor es. 
Cada match tiene una medida de lo "diferentes" que son (distancia). Para considerarlo para el resto de cálculos, exigiremos que su distancia sea, como mucho, este porcentaje de la distancia del segundo mejor match para el mismo punto clave de la imagen que nos interesa.

- Epsilon: Para acabar de filtrar entre los matches y quitar los que no nos interesan, aplicaremos un algoritmo de clustering a los "desplazamientos" detectados entre las imágenes. Para ello, consideraremos estos desplazamientos en número de píxeles, y seleccionaremos un subconjunto de estos que estén próximos entre ellos. Como mucho, estarán a distancia epsilon, que es este parámetro.

- Factor de reescalado: Nos permite reescalar la imagen final por un factor, lo cual implica más o menos precisión a la hora de alinear las imágenes individuales (por ejemplo, si el factor es 2.0 tenemos una precisión de 1/2.0 = 0.5 píxeles para alinearlas). Notemos que aumentar este factor implica también aumentar el tiempo de procesado a la hora de crear el mosaico.

- Wiggle: Libertad (en número de píxeles) que le damos al algoritmo de stitching para mover cada imagen individualmente a la hora de colocarla en el mosaico, realizando pequeños ajustes para mejorar la compatibilidad con las imágenes vecinas. Hacer estos pequeños ajustes es muy costoso, del orden de (2 * wiggle + 1) ^ 2: Si passamos de wiggle=0 a wiggle=1, tardamos el 9 veces más, y con wiggle=2 tardamos 25 veces más, Pero suele dar resultados mucho mejores. Hay que tener en cuenta que, si cambiamos el factor de reescalado, hay que ajustar el parámetro wiggle proporcionalmente para obtener los mismos resultados, y que si el resultado ya es muy bueno, esto no lo mejorará más. Si vemos que ciertas partes de la imagen se ven borrosas, podemos aumentar wiggle. Alternativamente, podemos ir ajustando los parámetros de stitching ddx, ddy, etc. Entender qué significa cada uno es importante: ver comentarios en el código de la función mosaicModel de holoUtils. Recordemos que la dirección de x positiva es hacia la derecha, y la de y positiva es hacia abajo. Se recomienda poner wiggle=0 mientras ajustamos los otros parámetros para poder hacer muchas pruebas rápido, y cuando conseguimos eliminar por la mayor parte las zonas borrosas ir aumentando wiggle en una o dos unidades como se desee.

**8. Variables de Stitching 1r orden**

**9. Variables de Stitching 2o orden**

**10. NX-NY**

- NX: Numero de imagenes en X en el mosaico
- NY: Numero de imagenes en Y en el mosaico

Por ejemplo, si hemos cogido un Set de imagenes de 90 imagenes con 10 filas y 9 columnas, tendremos que poner NX = 9, NY = 10.

**11. Botones de arranque**

Activan las distintas funcionalidades.

**12. IFFT Inverso**

![](https://github.com/gerardPerello/micProj/blob/master/assets/StitchingIFFT.png?raw=true)

**13. Longitud de Onda + SepPixCam**

- Lambda: Longitud de onda, en nm, utilizada para iluminar la muestra.

- Separación entre píxeles de la cámara (sensor) en um: Para saber la escala de la imagen. Observemos que si la imagen ha sido reescalada, debemos tenerlo en cuenta. Realmente es la separación entre píxeles de la imagen en el mundo real. En el caso de haber construido el mosaico en la propia sesión con un cierto factor de reescalado distinto a 1 (ver construcción del mosaico), esto ya lo tiene en cuenta el programa automáticamente. Sólo modificar respecto al real si las propias imágenes importadas han sido reescaladas.


**14. Distancias camara/muestra/luz (z/z0)**


- Z: Distancia, en metros, entre display y cámara.

- Z0: Distancia, en metros, entre display y muestra.

**15. Variables Display/Camara para el calculo automatico de z0.**

- Pitch camera: Distancia, en número de píxeles, entre las imágenes. Por defecto, al crear un mosaico, este valor se pone como la longitud del vector ddx.

 - Pitch display: Distancia, en número de píxeles, entre los píxeles del display de las imágenes. Si usamos el anterior parámetro por defecto, debería ser la distancia pitchX (ver primer paso de la importación de sets de imágenes).

- Separación entre píxeles del display.

**16. Apodization**

- Apodization: Longitud,en píxeles, del filtro de oscurecimiento que se aplica a los bordes de la imagen, para evitar artefactos derivados de la aplicación de la transformada de Fourier en estas zonas.

**17. Boton Calcular IFFT**

**18. Avanzar/Retroceder IFFT el paso**

**19. Boton Calcular Todos**

![](https://github.com/gerardPerello/micProj/blob/master/assets/StitchingExport.png?raw=true)

**20. Directory to Export**

**21. Filename**

**22. Formato**

**23. Botones Export/Import**

### Funcionalidades

#### Importar una imagen normalizada

#### Importar y normalizar un set de imágenes
- Para poder hacer el stitching y reconstrucción correctamente, tiene que haber para cada imagen de muestra, una imagentomada con el mismo píxel del display encendico pero sin la muestra (la llamaremos "fondo"). Las imágenes se tienen que tomaren cuadrícula de tamaño Ny * Nx, a intervalos regulares (pitchY y pitchX).Por ejemplo, si queremos tomar una cuadrícula 2*3 con pitchX = 10 y pitchY = 5,empezando con el led en la fila 100 y columna 100 las imágenes corresponderían a los leds de fila y columna:

         (100, 100) (100, 110) (100, 120)
         (105, 100) (105, 110) (105, 120)

- Las imágenes tienen que estar en dos carpetas, una llamada **Muestras** y la otra llamada **Fondos**, ambas en un mismo directorio y todas ordenadas por un íncide seguido de una barra baja, donde el índice va aumentando de izquierda a derecha y de arriba a abajo.
        Por ejemplo: 1_f100c100, 2_f100c110, 3_f100c120, 4_f105c100, 5_f105c110, 6_f105c120. Notemos que los íncices de fila y columna son útiles pero innnecesarios para nuestro programa

1. Iniciar el programa (python3 mainpantalla.py).

2. Situarse en la pestaña izquierda (Stitching) del programa.

3. Introducir los valores de Nx y Ny correspondientes a las imágenes tomadas.

4. Seleccionar el modo New en el selector Order (esto hace referencia a como se ordenan las imágenes en la carpeta).

5. Seleccionar el formato de imagen apropiado (tiff, jpg, png) en el selector Format.

6. Clicar en Cargar Set y seleccionar el directorio que contiene las dos carpetas. Vemos que se modifican los parámetros de stitching a unos por defecto.

7. Si clicamos en Stitch, se visualizarán las imágenes en cuadrícula. Comprobamos que cada imagen sea cercana a sus vecinas verticales y horizontales, si no, seguramente nos hayamos equivocado con el valor de Nx.

#### Construir un mosaico a partir de las imágenes normalizadas

1. Seguimos en la pestaña izquierda de las tres principales (Stitching)

2. Clicamos en Calcula Valores. Ello rellenará los 12 campos numéricos que se ven a la parte inferior. Su significado se expica en detalle en la función MosaicModel del archivo holoUtils.py. Intuitivamente, representan la separación que hay, en número de píxeles, entre imágenes contiguas, y sirven para hacer que las imágenes que enganchamos coincidan correctamente. Para saber como se relacionan las imágenes, buscamos coincidencias entre puntos clave de estas. Algunos parámetros atener en cuenta: 

	- Sigma Sift
	- nFeatures
	- Epsilon
	- % Sift Good

3. Si no se consigue calcular los valores de manera automática, es porque no hemos encontrado ninguna coincidencia suficientemente buena entre las imágenes. Podemos probar a bajar el parámetro % sift good o subir nfeatures (notemos que esto significa que encontraremos puntos clave menos significativos). También se pueden introducir los parámetros a mano.

4. Clicamos en el botón Stitch y esperamos a obtener el mosaico en la pantalla izquierda. Algunos parámetros a tener en cuenta:

	- Factor de reescalado
	- Wiggle


#### Reconstruir la muestra a partir de una imagen normalizada o mosaico (véanse pasos anteriores)

1. Nos situamos en la pestaña central del programa (IFFT).

2. Si tenemos una imagen cargada en el panel de la izquierda, veremos activada la opción Calcular, que reconstruirá la muestra. Parámetros a tener en cuenta:

	- Lambda
	- SepPixCam
	- Z
	- Z0

3. Si, además, disponemos de varias imágenes tomadas con píxeles distintos, podemos aplicar métodos geométricos (triángulos semejantes) para calcular el valor de Z0 a partir de los demás. Para ello, debemos presionar el botón "Calcular Z0", introduciendo antes los siguientes parámetros:

	- Pitch camera
	- Pitch display
	- Separacion entre pixeles del display
	- apodization

4. Una vez se ha reconstruido podemos usar los botones Retroceder y Avanzar para aumentar o disminuir ligeramente (en la cantidad indicada por el parámetro Paso Z0) El parámetro Z0 y calcular la reconstrucción correspondiente. Esto permite corregir dicho parámetro, o, en caso de muestras con un espesor considerable, observar distintas partes de la muestra. Con el procesamiento adecuado, se podrían exportar estas distintas reconstrucciones y hacer una reconstrucción tridimensional.


## ImagesLibrary
### DummySets
### HistorialSets

# Informacion para el desarrollador.
TO INSTALL DRIVERS OF THE SERVO ==> ./INSTALL ==> y,y,y,y,y,y ==> USERGROUP ==> dialout



  
<p align="right">By Gerard Perelló and Ferran Espuña</p>


