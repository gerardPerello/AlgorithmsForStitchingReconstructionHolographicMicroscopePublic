# CÀRREGA D'IMATGES
import glob
from skimage import io
import skimage.transform
from skimage import img_as_float
import glob
import cv2 as cv
import numpy as np
import cmath
import math
from sklearn.linear_model import LinearRegression

VALID_FORMAT = ('.BMP', '.GIF', '.JPG', '.JPEG', '.PNG', '.PBM', '.PGM', '.PPM', '.TIFF', '.XBM')


def sortPaths(paths, route):
    filenames = [path[len(route):] for path in paths]
    filenames.sort(key=lambda s: int(s[1:s.index('_')]))
    paths = [route + '/' + filename for filename in filenames]
    return paths


def loadImages(path, first=0, step=1, last=-1, typeImage='*.tiff', typeSorted=0):
    paths = glob.glob(path + "/" + typeImage)
    # Ens serveix per carregar les imatges en ordre.
    if last == -1:
        last = len(paths)

    # Dependiendo de si tenemos el sistema nuevo o el antiguo hacemos una cosa u otra.
    if typeSorted == 0:
        paths = sortPaths(paths, path)
    else:
        paths.sort()

    images = []
    for i in range(first, last, step):
        if typeImage == '*.tiff':
            im = img_as_float(io.imread(paths[i], plugin='tifffile'))
        else:
            im = img_as_float(io.imread(paths[i]))
        images.append(im)

    return images

def loadMuestraAndFondo(pathMuestra, pathFondo, typeImage='*.tiff'):
    
    if typeImage == '*.tiff':
        muestra = img_as_float(io.imread(pathMuestra, plugin='tifffile'))
        fondo = img_as_float(io.imread(pathFondo, plugin='tifffile'))
    else:
        muestra = img_as_float(io.imread(pathMuestra))
        fondo = img_as_float(io.imread(pathFondo))

    return (muestra - fondo) / fondo


def loadImage(path):
    im = img_as_float(io.imread(path))
    return im


def loadAndNormalize(path, typeImage, typeSorted):
    fondos = loadImages(path + '/Fondos', typeImage=typeImage, typeSorted=typeSorted)
    muestras = loadImages(path + '/Muestras', typeImage=typeImage, typeSorted=typeSorted)
    normalized = []
    for i in range(len(fondos)):
        normalized.append((muestras[i] - fondos[i]) / fondos[i])

    return normalized


# SIFT
def nsift(img):
    # Normalizing image to use CV.
    return cv.normalize(img, None, 0, 255, cv.NORM_MINMAX).astype('uint8')


# Extracting sift features.
def extract_sift_features(img):
    # Normalizing image
    img = nsift(img)
    # Creating sift
    sift = cv.SIFT.create(nfeatures=50, sigma=1.3)
    # Detecting and computing sift
    kp, des = sift.detectAndCompute(img, None)
    # Return kp and descriptor of the image.
    return kp, des


"""
Sift process of 2 images where "opt" = good filter of matches and "k" is a param for knn

Return ==> Good matches, (keypoints of image 1, keypoints of image 2),
(descriptors of image1 and descriptors of image2), (src_points, dst_pints)
a match is only considered "good" if the keypoints have similar orientations, as we do not wish to perform any rotation
"""


def siftProcess(img1, img2, opt=1):
    kp, d = extract_sift_features(img1)
    kp2, d2 = extract_sift_features(img2)

    bf = cv.BFMatcher()
    matches = bf.knnMatch(d, d2, k=2)
    good = []

    for match in matches:
        if len(match) == 2:
            m, n = match
            if m.distance < opt * n.distance:
                angle = (kp[m.queryIdx].angle - kp2[m.trainIdx].angle) % 360

                # TODO: comprobar que los tamaños de las features (kp[m.queryIdx].size, kp2[m.trainIdx].angle) sean parecidos
                if angle < 10 or angle > 350:
                    good.append([m])

    return good, (kp, kp2), (d, d2)  # ,(src_pts,dst_pts)


"""
Uses the previous method to find (a list of the) displacements between matches
"""


def siftDistanceVectorsImages(image1, image2, optSift):
    (good, kp, des) = siftProcess(image1, image2, opt=optSift)

    src_pts = np.float32([kp[0][m[0].queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp[1][m[0].trainIdx].pt for m in good]).reshape(-1, 1, 2)

    dif_vect = [src_pts[i][0] - dst_pts[i][0] for i in range(1, len(src_pts))]
    return dif_vect


# Clustering per proximitat, cada datapoint com a molt a distància epsilon de la resta del cluster
def clusterEpsilon(data, epsilon):
    k = 1
    n = data.shape[0]
    indices = np.zeros(n, dtype=int)

    for i in range(n):

        clusters = []

        for j in range(i):
            if not indices[j] in clusters and np.linalg.norm(data[i] - data[j]) < epsilon:
                clusters.append(indices[j])

        if not clusters:
            indices[i] = k
            k += 1

        else:
            indices[i] = clusters[0]
            for c in clusters[1:]:
                indices[indices == c] = clusters[0]

    clusters = []
    for i in range(k):
        cl = data[indices == i]
        if cl.shape[0] > 0:
            clusters.append(cl)

    clusters.sort(key=lambda cluster: cluster.shape[0], reverse=True)
    return clusters


"""
Using previous method to remove outliers, then find the mean of the translation vectors.
ddx is the translation vector from one image to the one to its right, while ddy is the 
translation vector from one image to the one below it.
"""


# Using previous method to remove outliers, then find the mean of the translation vectors
def totalMedDistanceVector(ims, nx, ny):
    ddx = []
    ddy = []

    for i in range(ny):
        for j in range(nx - 1):
            v = siftDistanceVectorsImages(ims[i * nx + j], ims[i * nx + (j + 1)])
            ddx += v

    for i in range(ny - 1):
        for j in range(nx):
            v = siftDistanceVectorsImages(ims[i * nx + j], ims[(i + 1) * nx + j])
            ddy += v

    ddx = np.asarray(ddx)
    ddy = np.asarray(ddy)

    clusterddx = clusterEpsilon(ddx, 5)[0]
    clusterddy = clusterEpsilon(ddy, 5)[0]

    finalddx = np.mean(clusterddx, axis=0)
    finalddy = np.mean(clusterddy, axis=0)

    return finalddx, finalddy


# FUNCIONS AUXILIARS PER A LA RECONSTRUCCIÓ

# FUNCIONS AUXILIARS PER A LA RECONSTRUCCIÓ. VEURE PAPER TATIANA.

imaI = 0 + 1j


def PropagatorS(Nvalue, Mvalue, lambdaValue, areaValueX, areaValueY, zValue):
    p = np.zeros((Nvalue, Mvalue), dtype='complex')

    for ii in range(0, Nvalue):
        for jj in range(0, Mvalue):
            u = (ii - Nvalue / 2) / areaValueY
            v = (jj - Mvalue / 2) / areaValueX

            p[ii, jj] = cmath.exp(imaI * np.pi * lambdaValue * zValue * (u ** 2 + v ** 2))

    return p


def Propagator(Nvalue, Mvalue, lambdaValue, areaValueX, areaValueY, zValue):
    p = np.zeros((Nvalue, Mvalue), dtype='complex')

    for ii in range(Nvalue):
        for jj in range(Mvalue):

            alpha = lambdaValue * (ii - Nvalue / 2) / areaValueX
            beta = lambdaValue * (jj - Mvalue / 2) / areaValueY

            if (alpha ** 2 + beta ** 2) <= 1:
                p[ii, jj] = cmath.exp(-2 * np.pi * imaI * zValue * np.sqrt(1 - alpha ** 2 - beta ** 2) / lambdaValue)

    return p


def FT2Dc(invalue):
    Nx, Ny = invalue.shape

    f1 = np.zeros((Nx, Ny), dtype='complex')

    for ii in range(Nx):

        for jj in range(Ny):
            f1[ii, jj] = cmath.exp(imaI * np.pi * (ii + jj))

    FT = np.fft.fft2(f1 * invalue)

    return f1 * FT


def IFT2Dc(invalue):
    Nx, Ny = invalue.shape

    f1 = np.zeros((Nx, Ny), dtype='complex')

    for ii in range(0, Nx):

        for jj in range(0, Ny):
            f1[ii, jj] = cmath.exp(-imaI * np.pi * (ii + jj))

    FT = np.fft.ifft2(f1 * invalue)

    return f1 * FT


# RECONSTRUCCIÓ D'HOLOGRAMES


def reconstructHologramSph(im, lamb=500e-9, h=0.05, z=0.1, z0=0.08):
    areaY = z0 * h / z
    areaX = areaY * im.shape[1] / im.shape[0]
    prop = PropagatorS(im.shape[0], im.shape[1], lamb, areaX, areaY, z0)
    p = np.abs(IFT2Dc(FT2Dc(im) * prop))
    return p


def reconstructHologramPlane(im, lamb=500e-9, h=0.05, z=0.1, z0=0.08):
    areaY = z0 * h / z
    areaX = areaY * im.shape[1] / im.shape[0]
    prop = Propagator(im.shape[0], im.shape[1], lamb, areaX, areaY, z0)
    p = np.abs(IFT2Dc(FT2Dc(im) * prop))
    return p


# Adaptación del apodization filter (paper Tatiana) a imágenes rectangulares: sólo recorta el borde.
def apodize(im, length):
    im2 = np.copy(im)

    for i in range(length):
        for j in range(i, im.shape[1] - i):
            m = math.cos(math.pi / (2 * length) * (length - i)) ** 2
            im2[i, j] *= m
            im2[im.shape[0] - i - 1, j] *= m

    for i in range(length):
        for j in range(i, im.shape[0] - i):
            m = math.cos(math.pi / (2 * length) * (length - i)) ** 2
            im2[j, i] *= m
            im2[j, im.shape[1] - i - 1] *= m

    return im2


# Clustering per proximitat, com a molt distància epsilon de la resta del cluster. Retornem els índexs a la llista
# dels elements de cada cluster, enlloc dels clusters en si.
def clusterEpsilonIndices(data, epsilon):
    k = 1
    n = data.shape[0]
    indices = np.zeros(n, dtype=int)

    for i in range(n):

        clusters = []

        for j in range(i):
            if not indices[j] in clusters and np.linalg.norm(data[i] - data[j]) < epsilon:
                clusters.append(indices[j])

        if not clusters:
            indices[i] = k
            k += 1

        else:
            indices[i] = clusters[0]
            for c in clusters[1:]:
                indices[indices == c] = clusters[0]

    clusters = []
    zeroToN = np.asarray([i for i in range(n)], dtype=int)
    for i in range(k):
        cl = zeroToN[indices == i]
        if cl.shape[0] > 0:
            clusters.append(cl)

    clusters.sort(key=lambda cluster: cluster.shape[0], reverse=True)
    return clusters


"""
Entrena modelos lineales para predecir ddx (vector de desplazamiento de una imagen a la de la derecha) 
y ddy (vector dedesplazamiento de una imagen a la de abajo) dependiendo de la posición i,j de la imagen en la "cuadrícula" de imágenes.

No podemos considerar un modelo estático (independiente de i y j) ya que eso se da en el caso de que
muestra, cámara y display estén perfectamente alineados en planos paralelos.

ModelX pretende calcular ddx: modela ddx(i, j) = (A, B) + (C, D) * i + (E, F) * j, y similarmente para ddy.
(tomando j = x, i = y) Podemos interpretar (A, B) como la derivada dp/dx donde p es la  posición inicial de cada imagen,
tomando j ≈ x, i ≈ y (de ahí el nombre). 

Entonces, (C, D) será la derivada d(ddx)/dy y (E, F) la derivada d(ddx)/dx. El modelo por tanto consiste de un término
independiente (modelX.intercept_ = ddx) y una parte lineal(modelX.coef_ = (dddx_dy, dddx_dx)). Estos nombres de variables
nos serán útiles al hacer el stitching.
"""


def totalMedDistanceVectorTest(ims, nx, ny, optSift=1, epsilon=5):
    saltos = []
    desplazamientos = []

    # Recorremos todas las imágenes, sin la última fila ya que no tiene vecina inferior
    for i in range(ny - 1):
        for j in range(nx):
            # Obtenemos vectores de desplazamiento hacia abajo
            v = siftDistanceVectorsImages(ims[i * nx + j], ims[(i + 1) * nx + j], optSift=optSift)
            desplazamientos += v
            saltos += [[i, j]] * len(v)
    # Hacemos el clustering por índices para quitarnos outliers
    buenos = clusterEpsilonIndices(np.asarray(desplazamientos), epsilon)[0]
    #
    x = np.array([saltos[k] for k in buenos])
    y = np.array([desplazamientos[k] for k in buenos])

    modelY = LinearRegression(fit_intercept=True).fit(x, y)

    saltos = []
    desplazamientos = []

    for i in range(ny):
        for j in range(nx - 1):
            v = siftDistanceVectorsImages(ims[i * nx + j], ims[i * nx + (j + 1)], optSift=optSift)
            desplazamientos += v
            saltos += [[i, j]] * len(v)
    buenos = clusterEpsilonIndices(np.asarray(desplazamientos), epsilon)[0]
    x = np.array([saltos[k] for k in buenos])
    y = np.array([desplazamientos[k] for k in buenos])

    modelX = LinearRegression(fit_intercept=True).fit(x, y)

    return modelX, modelY


"""
Método para crear un mosaico con los parámetros calculados en totalMedDistanceVectorTest. Parámetros:

    images: imágenes ordenadas por filas
    
    nx, ny: Número de imágenes por fila y columna, resp.
    
    ddx, ddy dddx_dx, dddx_dy, dddy_dx, dddy_dy: parámetros del vector de desplazamiento, explicados en totalMedDistanceVectorTest.
    
    factAugment: Factor por el cual se escalarán todas las imágenes a fin de mejorar la precisión del stitching (o ahorrar
    tiempo, si es inferior a 1).
    
    wiggle: Margen (en número de píxeles) que le damos al algoritmo para encontrar un mejor punto inicial para cada imagen.
    Ojo: el algoritmo es cuadrático en la variable wiggle, es decir, tarda mucho más si la aumentamos. Aún así, es lo 
    más preciso para hacer el stitching perfecto. Debería ser aumentada proporcionalmente a factAugment, ya que imágenes
    más grandes -> error más grande, en número de píxeles.
    
    stack: booleano que dice si, en zonas donde se solapan, las imágenes deberían hacer media (true) o, no, y por tanto poner la más nueva encima.
    
    cut: booleano que dice si recortamos la imagen final para quitar espacio en blanco al final de todo.
    
"""


def mosaicModel(images, nx, ny, ddx, ddy, dddx_dx=np.array([0, 0]), dddx_dy=np.array([0, 0]), dddy_dx=np.array([0, 0]),
                dddy_dy=np.array([0, 0]),
                factAugment=1, wiggle=0, stack=True, cut=True):
    """
    Hemos observado que la mayor parte del efecto de las derivadas de segundo orden (dddx_dx, etc.) viene de una escala
    inconsistente en las imágenes. Reescalando las imágenes, estas encajan mejor en el mosaico. En lugar de para cada imagen
    calcular su desplazamiento respecto a la anterior (esto es inconsistente dependiendo de si lo hacemos respecto a la de arriba
    o la de la izquierda), escalamos cada imagen para que los vectores de desplazamiento (escalados) se correspondan aproximadamente
    con los de la primera imagen (i = j = 0). Así, con un ddx y ddy fijos podemos completar el mosaico.
    """

    # Esto es una media de la "escala" de cada imagen
    original = np.linalg.norm(ddx) + np.linalg.norm(ddy)

    #
    imsScaled = [
        skimage.transform.rescale(
            images[nx * i + j],
            factAugment / (np.linalg.norm(ddx + i * dddx_dy + j * dddx_dx) + np.linalg.norm(
                ddy + i * dddy_dy + j * dddy_dx)) * original
        ) for i in range(ny) for j in range(nx)
    ]

    # Dimensions de les imatges
    h, w = imsScaled[0].shape
    hmax = max(imsScaled[0].shape[0], imsScaled[nx - 1].shape[0], imsScaled[nx*(ny-1)].shape[0], imsScaled[-1].shape[0])
    wmax = max(imsScaled[0].shape[1], imsScaled[nx - 1].shape[1], imsScaled[nx*(ny-1)].shape[1], imsScaled[-1].shape[1])

    ddx *= factAugment
    ddy *= factAugment

    # Punts inicials de la primera imatge
    x0 = round(max(0, - (nx - 1) * ddx[0], - (ny - 1) * ddy[0], - (nx - 1) * ddx[0] - (ny - 1) * ddy[0]) + wiggle * (
            nx + ny - 2)) + nx + ny - 2
    y0 = round(max(0, - (nx - 1) * ddx[1], - (ny - 1) * ddy[1], - (nx - 1) * ddx[1] - (ny - 1) * ddy[1]) + wiggle * (
            nx + ny - 2)) + nx + ny - 2

    # Dimensions del mosaic
    W = round(
        x0 + wmax + 
        max(0, (nx - 1) * abs(ddx[0]), (ny - 1) * abs(ddy[0]), (nx - 1) * abs(ddx[0] + (ny - 1) * ddy[0])) +
        2 * wiggle * (nx + ny - 2)
    ) + 2 * (nx + ny - 2)

    H = round(
        y0 + hmax +
        max(0, (nx - 1) * abs(ddx[1]), (ny - 1) * abs(ddy[1]), abs((nx - 1) * ddx[1] + (ny - 1) * ddy[1])) +
        2 * wiggle * (nx + ny - 2)
    ) + 2 * (nx + ny - 2)

    minStartX = x0
    minStartY = y0
    maxEndX = 0
    maxEndY = 0

    # Imatge del mosaic inicialitzada a 0
    imFinal = np.zeros((H, W), dtype=float)
    layers = np.zeros((H, W), dtype=float)

    imFinal[y0: y0 + h, x0: x0 + w] = imsScaled[0]
    layers[y0: y0 + h, x0: x0 + w] = 1

    prevStart = np.array([x0, y0])
    prevRowStart = prevStart

    
    # Recorrem totes les imatges, ordenades per files i columnes
    for i in range(ny):
        for j in range(nx):
            if i != 0 or j != 0:

                # Imatge que volem incrustar al mosaic
                im = imsScaled[nx * i + j]
                h, w = im.shape

                if j == 0:
                    s = prevRowStart + ddy
                else:
                    s = prevStart + ddx

                sx0 = round(s[0])
                sy0 = round(s[1])

                # inicialitzem score a infinit
                scoreFinal = float('inf')

                finalsx, finalsy = sx0, sy0
                finalex, finaley = sx0 + w, sy0 + h
                # Provem de moure'ns una mica
                for wigglex in range(-wiggle, wiggle + 1):
                    for wiggley in range(-wiggle, wiggle + 1):

                        # Punts inicials i finals de la imatge al mosaic
                        sx = sx0 + wigglex
                        sy = sy0 + wiggley
                        ex = sx + w
                        ey = sy + h

                        # Calculem score de similitud pertinent
                        prev = imFinal[sy: ey, sx: ex]
                        layersPrev = layers[sy: ey, sx: ex]

                        score = np.linalg.norm(im * layersPrev - prev) / (1 + np.sum(layersPrev))

                        if score < scoreFinal:
                            scoreFinal = score
                            finalsx, finalsy, finalex, finaley = sx, sy, ex, ey

                prevStart = np.array([finalsx, finalsy])
                if j == 0:
                    prevRowStart = prevStart

                minStartX = min(minStartX, finalsx)
                maxEndX = max(maxEndX, finalex)
                minStartY = min(minStartY, finalsy)
                maxEndY = max(maxEndY, finaley)

                if stack:
                    # Assignem els píxels corresponents
                    imFinal[finalsy: finaley, finalsx: finalex] += im
                    layers[finalsy: finaley, finalsx: finalex] += 1
                else:

                    # Assignem els píxels corresponents
                    imFinal[finalsy: finaley, finalsx: finalex] = im
                    layers[finalsy: finaley, finalsx: finalex] = 1

    layers[layers == 0] = 1
    imFinal /= layers

    if cut:
        imFinal = imFinal[minStartY: maxEndY, minStartX: maxEndX]

    return imFinal

def detectaAltura(separation_pixels_camera, separation_pixels_display, npixels_camera, npixels_display, z):
    A = separation_pixels_display * npixels_display
    B = separation_pixels_camera * npixels_camera
    return z * A / (A + B)