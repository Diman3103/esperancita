import re

from normalizador import (
    normalizar_producto,
    normalizar_solicitud,
)


# =========================================================
# PALABRAS QUE PUEDEN GENERAR FALSOS POSITIVOS
# =========================================================

TERMINOS_EXCLUIDOS = {

    "azucar": [
        "sin azucar",
        "sin azucares",
        "azucarados",
        "azucarada",
    ],

}


# =========================================================
# OBTENER PALABRAS DEL TEXTO
# =========================================================

def obtener_palabras(texto):

    return re.findall(
        r"\b[a-z0-9]+\b",
        texto.lower()
    )


# =========================================================
# ¿EL NOMBRE EMPIEZA CON EL PRODUCTO?
# =========================================================

def empieza_con_producto(
    nombre,
    producto
):

    nombre = nombre.lower().strip()
    producto = producto.lower().strip()

    if not producto:
        return False

    return (
        nombre == producto
        or nombre.startswith(
            producto + " "
        )
        or nombre.startswith(
            producto + "x"
        )
    )


# =========================================================
# ¿CONTIENE LAS PALABRAS DEL PRODUCTO?
# =========================================================

def contiene_producto(
    nombre,
    producto
):

    palabras_nombre = obtener_palabras(
        nombre
    )

    palabras_producto = obtener_palabras(
        producto
    )

    if not palabras_producto:
        return False

    return all(
        palabra in palabras_nombre
        for palabra in palabras_producto
    )


# =========================================================
# COMPROBAR CANTIDAD
# =========================================================

def cantidad_compatible(
    producto,
    solicitud
):

    cantidad_solicitada = solicitud.get(
        "cantidad"
    )

    unidad_solicitada = solicitud.get(
        "unidad"
    )

    # Si el usuario no indicó cantidad,
    # no filtramos por cantidad.
    if (
        cantidad_solicitada is None
        or unidad_solicitada is None
    ):
        return True

    cantidad_producto = producto.get(
        "cantidad_base"
    )

    unidad_producto = producto.get(
        "unidad_base"
    )

    # Si el producto no tiene cantidad
    # no podemos confirmar que sea compatible.
    if (
        cantidad_producto is None
        or unidad_producto is None
    ):
        return False

    if unidad_producto != unidad_solicitada:
        return False

    return abs(
        cantidad_producto
        - cantidad_solicitada
    ) < 0.01


# =========================================================
# DETECTAR FALSOS POSITIVOS
# =========================================================

def es_falso_positivo(
    nombre,
    producto_buscado
):

    nombre = nombre.lower()
    producto_buscado = producto_buscado.lower()

    terminos = TERMINOS_EXCLUIDOS.get(
        producto_buscado,
        []
    )

    for termino in terminos:

        if termino in nombre:
            return True

    return False

# =========================================================
# BUSCAR APROXIMACIONES
# =========================================================

def buscar_aproximaciones(
    productos,
    consulta,
    limite=5
):

    if isinstance(
        consulta,
        dict
    ):
        solicitud = consulta

    else:
        solicitud = normalizar_solicitud(
            consulta
        )

    productos_normalizados = []

    for producto in productos:

        producto_normalizado = normalizar_producto(
            producto
        )

        productos_normalizados.append(
            producto_normalizado
        )

    aproximaciones = []

    producto_buscado = solicitud.get(
        "producto",
        ""
    )

    if not producto_buscado:
        return []

    # -----------------------------------------------------
    # EVALUAR PRODUCTOS
    # -----------------------------------------------------

    for producto in productos_normalizados:

        nombre = producto.get(
            "nombre_normalizado",
            ""
        )

        # No queremos falsos positivos obvios.
        if es_falso_positivo(
            nombre,
            producto_buscado
        ):
            continue

        # -------------------------------------------------
        # COINCIDENCIA DEL NOMBRE
        # -------------------------------------------------

        if empieza_con_producto(
            nombre,
            producto_buscado
        ):

            puntuacion = 100

        elif contiene_producto(
            nombre,
            producto_buscado
        ):

            puntuacion = 60

        else:

            continue

        # -------------------------------------------------
        # DIFERENCIA DE PRESENTACIÓN
        # -------------------------------------------------

        cantidad_solicitada = solicitud.get(
            "cantidad"
        )

        unidad_solicitada = solicitud.get(
            "unidad"
        )

        cantidad_producto = producto.get(
            "cantidad_base"
        )

        unidad_producto = producto.get(
            "unidad_base"
        )

        diferencia = None

        if (
            cantidad_solicitada is not None
            and cantidad_producto is not None
            and unidad_solicitada == unidad_producto
        ):

            diferencia = abs(
                cantidad_producto
                -
                cantidad_solicitada
            )

            # Cuanto más cerca esté la presentación,
            # mayor puntuación.

            if diferencia == 0:

                puntuacion += 30

            else:

                porcentaje = (
                    diferencia
                    /
                    cantidad_solicitada
                )

                if porcentaje <= 0.10:

                    puntuacion += 20

                elif porcentaje <= 0.25:

                    puntuacion += 10

        # -------------------------------------------------
        # SI NO TENEMOS PRESENTACIÓN
        # -------------------------------------------------

        elif (
            cantidad_solicitada is not None
            and cantidad_producto is None
        ):

            # No sabemos si coincide.
            # Penalizamos para que quede debajo
            # de las opciones con presentación conocida.

            puntuacion -= 20

        # -------------------------------------------------
        # GUARDAR
        # -------------------------------------------------

        resultado = dict(
            producto
        )

        resultado[
            "puntuacion_aproximada"
        ] = puntuacion

        resultado[
            "diferencia_cantidad"
        ] = diferencia

        aproximaciones.append(
            resultado
        )

    # -----------------------------------------------------
    # ORDENAR
    # -----------------------------------------------------

    aproximaciones.sort(
        key=lambda producto: (
            -producto[
                "puntuacion_aproximada"
            ],

            producto.get(
                "precio"
            )
            if producto.get(
                "precio"
            ) is not None
            else float("inf")
        )
    )

    return aproximaciones[:limite]
# =========================================================
# PUNTUAR COINCIDENCIA
# =========================================================

def puntuar_producto(
    producto,
    solicitud
):

    nombre = producto.get(
        "nombre_normalizado",
        ""
    )

    producto_buscado = solicitud.get(
        "producto",
        ""
    )

    if not producto_buscado:
        return -1, [
            "solicitud vacia"
        ]

    # -----------------------------------------------------
    # FALSOS POSITIVOS
    # -----------------------------------------------------

    if es_falso_positivo(
        nombre,
        producto_buscado
    ):

        return -1, [
            "posible falso positivo"
        ]

    # -----------------------------------------------------
    # CANTIDAD
    # -----------------------------------------------------

    if not cantidad_compatible(
        producto,
        solicitud
    ):

        return -1, [
            "cantidad o unidad incompatible"
        ]

    puntuacion = 0

    razones = []

    # -----------------------------------------------------
    # COINCIDENCIA PRINCIPAL
    # -----------------------------------------------------

    if empieza_con_producto(
        nombre,
        producto_buscado
    ):

        # La coincidencia que queremos
        # tiene prioridad máxima.

        puntuacion += 70

        razones.append(
            "el nombre empieza con el producto"
        )

    elif contiene_producto(
        nombre,
        producto_buscado
    ):

        puntuacion += 35

        razones.append(
            "contiene las palabras del producto"
        )

    else:

        return -1, [
            "no coincide el producto"
        ]

    # -----------------------------------------------------
    # CANTIDAD COMPATIBLE
    # -----------------------------------------------------

    if (
        solicitud.get("cantidad")
        is not None
    ):

        puntuacion += 25

        razones.append(
            "cantidad y unidad compatibles"
        )

    return puntuacion, razones


# =========================================================
# BUSCAR PRODUCTOS
# =========================================================

def buscar_productos(
    productos,
    consulta,
    limite=None
):

    # La consulta puede ser:
    #
    # "azucar 1kg"
    #
    # o directamente un diccionario
    # producido por normalizar_solicitud().

    if isinstance(
        consulta,
        dict
    ):

        solicitud = consulta

    else:

        solicitud = normalizar_solicitud(
            consulta
        )

    productos_normalizados = []

    for producto in productos:

        producto_normalizado = normalizar_producto(
            producto
        )

        productos_normalizados.append(
            producto_normalizado
        )

    resultados = []

    # -----------------------------------------------------
    # EVALUAR PRODUCTOS
    # -----------------------------------------------------

    for producto in productos_normalizados:

        puntuacion, razones = puntuar_producto(
            producto,
            solicitud
        )

        # -1 significa que no es compatible.

        if puntuacion < 0:
            continue

        resultado = dict(
            producto
        )

        resultado["puntuacion"] = puntuacion

        resultado["razones"] = razones

        resultados.append(
            resultado
        )

    # -----------------------------------------------------
    # ORDENAR
    # -----------------------------------------------------
    #
    # Primero:
    #   mayor coincidencia
    #
    # Después:
    #   menor precio
    #
    # Esto es importante.
    #
    # NO queremos que un producto barato pero
    # incorrecto gane simplemente por precio.
    # -----------------------------------------------------

    resultados.sort(
        key=lambda producto: (
            -producto["puntuacion"],
            producto.get(
                "precio"
            )
            if producto.get(
                "precio"
            ) is not None
            else float("inf")
        )
    )

    if limite is not None:

        resultados = resultados[
            :limite
        ]

    return resultados


# =========================================================
# PRUEBAS
# =========================================================

if __name__ == "__main__":

    productos_prueba = [

        {
            "nombre":
                "AZUCAR MYRIAM LA PRINCESA X1KG",

            "marca":
                "Myriam",

            "precio":
                1390,

            "cantidad":
                1,

            "unidad":
                "kg",
        },

        {
            "nombre":
                "AZUCAR CHANGO BOLSA POLIET X1KG",

            "marca":
                "Chango",

            "precio":
                1590,

            "cantidad":
                1,

            "unidad":
                "kg",
        },

        {
            "nombre":
                "BIZCOCHO 9 DE ORO AZUCARADOS X210",

            "marca":
                None,

            "precio":
                1190,

            "cantidad":
                None,

            "unidad":
                None,
        },

        {
            "nombre":
                "azucar impalpable chango x250gr",

            "marca":
                "Chango",

            "precio":
                1840,

            "cantidad":
                250,

            "unidad":
                "g",
        },

        {
            "nombre":
                "SEVEN UP LIMA LIMON SIN AZUCAR X1.5",

            "marca":
                None,

            "precio":
                3250,

            "cantidad":
                1.5,

            "unidad":
                "l",
        },

    ]

    # -----------------------------------------------------
    # PRUEBA 1
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("PRUEBA 1: azucar")
    print("=" * 70)

    resultados = buscar_productos(
        productos_prueba,
        "azucar"
    )

    for producto in resultados:

        print(
            f"{producto['nombre_original']}"
        )

        print(
            f"Precio: ${producto['precio']:.2f}"
        )

        print(
            f"Score: {producto['puntuacion']}"
        )

        print(
            f"Razones: {producto['razones']}"
        )

        print()

    # -----------------------------------------------------
    # PRUEBA 2
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("PRUEBA 2: azucar 1kg")
    print("=" * 70)

    resultados = buscar_productos(
        productos_prueba,
        "azucar 1kg"
    )

    for producto in resultados:

        print(
            f"{producto['nombre_original']}"
        )

        print(
            f"Precio: ${producto['precio']:.2f}"
        )

        print(
            f"Score: {producto['puntuacion']}"
        )

        print()

    # -----------------------------------------------------
    # PRUEBA 3
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("PRUEBA 3: azucar 250g")
    print("=" * 70)

    resultados = buscar_productos(
        productos_prueba,
        "azucar 250g"
    )

    for producto in resultados:

        print(
            f"{producto['nombre_original']}"
        )

        print(
            f"Precio: ${producto['precio']:.2f}"
        )

        print(
            f"Score: {producto['puntuacion']}"
        )

        print()