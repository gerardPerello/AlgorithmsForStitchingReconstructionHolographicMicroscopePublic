PARA CAMBIAR LA INTERFAZ (AÑADIR / QUTAR / MOVER / RENOMBRAR ELEMENTOS):

    - Editar el documento form.ui en el programa QT Creator.

    - Desde esta carpeta, ejecutar, en esta misma carpeta:
        pyuic5 form.ui -o form.py

    - Para cambiar la funcionalidad de los botones, editar el archivo mainpantalla.ui.Este archivo importa muchas funciones de holoUtils.py. En los comentarios hay información detallada de cómo funcionan.

    - Al ejecutar el programa (mainpantalla.ui), se podrá ver la interfaz cambiada.

    - Para más información, ver documentación de la librería PyQt5.

WORKFLOW PRINCIPAL DEL PROGRAMA

    - Importar una imagen normalizada:

        - TODO

    - Importar y normalizar un set de imágenes:

        - Para poder hacer el stitching y reconstrucción correctamente, tiene que haber para cada imagen de muestra, una imagentomada con el mismo píxel del display encendico pero sin la muestra (la llamaremos "fondo"). Las imágenes se tienen que tomaren cuadrícula de tamaño Ny * Nx, a intervalos regulares (pitchY y pitchX).Por ejemplo, si queremos tomar una cuadrícula 2*3 con pitchX = 10 y pitchY = 5,empezando con el led en la fila 100 y columna 100 las imágenes corresponderían a los leds de fila y columna:

         (100, 100) (100, 110) (100, 120)
         (105, 100) (105, 110) (105, 120)

        - Las imágenes tienen que estar en dos carpetas, una llamada Muestras y la otra llamada Fondos, ambas en un mismo directorio y todas ordenadas por un íncide seguido de una barra baja, donde el índice va aumentando de izquierda a derecha y de arriba a abajo.
        Por ejemplo: 1_f100c100, 2_f100c110, 3_f100c120, 4_f105c100, 5_f105c110, 6_f105c120. Notemos que los íncices de fila y columna son útiles pero innnecesarios para nuestro programa

        - Iniciar el programa (python3 mainpantalla.py).

        - Situarse en la pestaña izquierda (Stitching) del programa.

        - Introducir los valores de Nx y Ny correspondientes a las imágenes tomadas.

        - Seleccionar el modo New en el selector Order (esto hace referencia a como se ordenan las imágenes en la carpeta).

        - Seleccionar el formato de imagen apropiado (tiff, jpg, png) en el selector Format.

        - Clicar en Cargar Set y seleccionar el directorio que contiene las dos carpetas. Vemos que se modifican los parámetros de stitching a unos por defecto.

        - Si clicamos en Stitch, se visualizarán las imágenes en cuadrícula. Comprobamos que cada imagen sea cercana a sus vecinas verticales y horizontales, si no, seguramente nos hayamos equivocado con el valor de Nx.

    - Construir un mosaico a partir de las imágenes normalizadas:

        - Seguimos en la pestaña izquierda de las tres principales (Stitching)

        - Clicamos en Calcula Valores. Ello rellenará los 12 campos numéricos que se ven a la parte inferior. Su significado se expica en detalle en la función MosaicModel del archivo holoUtils.py. Intuitivamente, representan la separación que hay, en número de píxeles, entre imágenes contiguas, y sirven para hacer que las imágenes que enganchamos coincidan correctamente. Para saber como se relacionan las imágenes, buscamos coincidencias entre puntos clave de estas. Algunos parámetros atener en cuenta:

            - Sigma sift: En principio no hace falta tocarlo, ver documentación de opencv para más información

            - nFeatures: número de puntos clave que se buscan para cada imagen

            - % Sift Good: Para cada punto clave, buscaremos en las imágenes vecinas su mejor "pareja" (match). Para saber si el match es bueno, lo compararemos con el segundo mejor, y vemos cuánto mejor es.
            Cada match tiene una medida de lo "diferentes" que son (distancia). Para considerarlo para el resto de cálculos, exigiremos que su distancia sea, como mucho, este porcentaje de la distancia del segundo mejor match para el mismo punto clave de la imagen que nos interesa.

            -Epsilon: Para acabar de filtrar entre los matches y quitar los que no nos interesan, aplicaremos un algoritmo de clustering a los "desplazamientos" detectados entre las imágenes. Para ello, consideraremos estos desplazamientos en número de píxeles, y seleccionaremos un subconjunto de estos que estén próximos entre ellos. Como mucho, estarán a distancia epsilon, que es este parámetro.

        - Si no se consigue calcular los valores de manera automática, es porque no hemos encontrado ninguna coincidencia suficientemente buena entre las imágenes. Podemos probar a bajar el parámetro % sift good o subir nfeatures (notemos que esto significa que encontraremos puntos clave menos significativos). También se pueden introducir los parámetros a mano.

        - Clicamos en el botón Stitch y esperamos a obtener el mosaico en la pantalla izquierda. Algunos parámetros a tener en cuenta:

            - Factor de reescalado: Nos permite reescalar la imagen final por un factor, lo cual implica más o menos precisión a la hora de alinear las imágenes individuales (por ejemplo, si el factor es 2.0 tenemos una precisión de 1/2.0 = 0.5 píxeles para alinearlas). Notemos que aumentar este factor implica también aumentar el tiempo de procesado a la hora de crear el mosaico.

            - Wiggle: Libertad (en número de píxeles) que le damos al algoritmo de stitching para mover cada imagen individualmente a la hora de colocarla en el mosaico, realizando pequeños ajustes para mejorar la compatibilidad con las imágenes vecinas. Hacer estos pequeños ajustes es muy costoso, del orden de (2 * wiggle + 1) ^ 2: Si passamos de wiggle=0 a wiggle=1, tardamos el 9 veces más, y con wiggle=2 tardamos 25 veces más, Pero suele dar resultados mucho mejores. Hay que tener en cuenta que, si cambiamos el factor de reescalado, hay que ajustar el parámetro wiggle proporcionalmente para obtener los mismos resultados, y que si el resultado ya es muy bueno, esto no lo mejorará más. Si vemos que ciertas partes de la imagen se ven borrosas, podemos aumentar wiggle. Alternativamente, podemos ir ajustando los parámetros de stitching ddx, ddy, etc. Entender qué significa cada uno es importante: ver comentarios en el código de la función mosaicModel de holoUtils. Recordemos que la dirección de x positiva es hacia la derecha, y la de y positiva es hacia abajo. Se recomienda poner wiggle=0 mientras ajustamos los otros parámetros para poder hacer muchas pruebas rápido, y cuando conseguimos eliminar por la mayor parte las zonas borrosas ir aumentando wiggle en una o dos unidades como se desee.


    - Reconstruir la muestra a partir de una imagen normalizada o mosaico (véanse pasos anteriores):

        - Nos situamos en la pestaña central del programa (IFFT).

        - Si tenemos una imagen cargada en el panel de la izquierda, veremos activada la opción Calcular, que reconstruirá la muestra. Parámetros a tener en cuenta:

            - Lambda: Longitud de onda, en nm, utilizada para iluminar la muestra.

            - Separación entre píxeles de la cámara (sensor) en um: Para saber la escala de la imagen. Observemos que si la imagen ha sido reescalada, debemos tenerlo en cuenta. Realmente es la separación entre píxeles de la imagen en el mundo real. En el caso de haber construido el mosaico en la propia sesión con un cierto factor de reescalado distinto a 1 (ver construcción del mosaico), esto ya lo tiene en cuenta el programa automáticamente. Sólo modificar respecto al real si las propias imágenes importadas han sido reescaladas.

            - Z: Distancia, en metros, entre display y cámara.

            - Z0: Distancia, en metros, entre display y muestra.

                - Si, además, disponemos de varias imágenes tomadas con píxeles distintos, podemos aplicar métodos geométricos (triángulos semejantes) para calcular el valor de Z0 a partir de los demás. Para ello, debemos presionar el botón "Calcular Z0", introduciendo antes los siguientes parámetros:

                    - Pitch camera: Distancia, en número de píxeles, entre las imágenes. Por defecto, al crear un mosaico, este valor se pone como la longitud del vector ddx.

                    - Pitch display: Distancia, en número de píxeles, entre los píxeles del display de las imágenes. Si usamos el anterior parámetro por defecto, debería ser la distancia pitchX (ver primer paso de la importación de sets de imágenes).

                    - Separación entre píxeles del display.

            - Apodization: Longitud,en píxeles, del filtro de oscurecimiento que se aplica a los bordes de la imagen, para evitar artefactos derivados de la aplicación de la transformada de Fourier en estas zonas.

    - Una vez se ha reconstruido podemos usar los botones Retroceder y Avanzar para aumentar o disminuir ligeramente (en la cantidad indicada por el parámetro Paso Z0) El parámetro Z0 y calcular la reconstrucción correspondiente. Esto permite corregir dicho parámetro, o, en caso de muestras con un espesor considerable, observar distintas partes de la muestra. Con el procesamiento adecuado, se podrían exportar estas distintas reconstrucciones y hacer una reconstrucción tridimensional.


    #TODO: EXPLICAR EXPORTACIÓN DE IMÁGENES Y PARÁMETROS, ASÍ COMO RESTORE LAST SESSION






