import re


def extraer_cantidad_unidad(texto):
    """
    Busca una cantidad y una unidad dentro del texto.

    Ejemplos:
        1L
        1 kg
        500g
        250 ml
        1,5L
        1 unidad
        12 unidades
    """

    patron = re.search(
        r"(\d+(?:[.,]\d+)?)\s*"
        r"(kg|kgs|k|g|gr|grs|l|lt|lts|ml|cc|"
        r"u|unidad|unidades)\b",
        texto,
        re.IGNORECASE
    )

    if not patron:
        return None, None

    cantidad = float(
        patron.group(1).replace(",", ".")
    )

    unidad = patron.group(2).lower()

    equivalencias = {
        "k": "kg",
        "kgs": "kg",

        "gr": "g",
        "grs": "g",

        "lt": "l",
        "lts": "l",

        "cc": "ml",

        "u": "un",
        "unidad": "un",
        "unidades": "un"
    }

    unidad = equivalencias.get(
        unidad,
        unidad
    )

    if unidad == "kg":
        cantidad *= 1000
        unidad = "g"

    elif unidad == "l":
        cantidad *= 1000
        unidad = "ml"

    return cantidad, unidad


def limpiar_nombre(texto):
    """
    Elimina la cantidad y unidad del nombre
    del producto.
    """

    nombre = re.sub(
        r"\s*(\d+(?:[.,]\d+)?)\s*"
        r"(kg|kgs|k|g|gr|grs|l|lt|lts|ml|cc|"
        r"u|unidad|unidades)\b",
        "",
        texto,
        flags=re.IGNORECASE
    )

    return nombre.strip()


def pedir_cantidad_unidad(nombre):
    """
    Solicita al usuario la cantidad y unidad cuando
    no fueron especificadas en la lista.
    """

    print(
        f"\nNo especificaste la cantidad "
        f"para '{nombre}'."
    )

    while True:

        cantidad_texto = input(
            "¿Qué cantidad querés? "
        ).strip()

        try:

            cantidad = float(
                cantidad_texto.replace(",", ".")
            )

            if cantidad <= 0:
                print(
                    "La cantidad debe ser mayor que 0."
                )
                continue

            break

        except ValueError:

            print(
                "Ingresá una cantidad válida."
            )

    print("\nElegí la unidad:")

    print("1. kg")
    print("2. g")
    print("3. L")
    print("4. ml")
    print("5. unidad")

    equivalencias = {
        "1": "kg",
        "2": "g",
        "3": "l",
        "4": "ml",
        "5": "un"
    }

    while True:

        opcion = input("> ").strip()

        if opcion in equivalencias:

            unidad = equivalencias[opcion]

            break

        print(
            "Opción inválida. "
            "Elegí un número del 1 al 5."
        )

    # Normalizamos las unidades igual que cuando
    # vienen escritas directamente en la lista.

    if unidad == "kg":

        cantidad *= 1000
        unidad = "g"

    elif unidad == "l":

        cantidad *= 1000
        unidad = "ml"

    return cantidad, unidad


def procesar_producto(texto):
    """
    Convierte una línea escrita por el usuario
    en un producto estructurado.

    Si la cantidad no fue especificada,
    se le solicita al usuario.
    """

    texto = texto.strip()

    if not texto:
        return None

    cantidad, unidad = extraer_cantidad_unidad(
        texto
    )

    nombre = limpiar_nombre(texto)

    if cantidad is None or unidad is None:

        cantidad, unidad = pedir_cantidad_unidad(
            nombre
        )

    return {
        "nombre": nombre,
        "cantidad": cantidad,
        "unidad": unidad
    }


def cargar_lista():
    """
    Permite al usuario ingresar una lista de compras.

    La entrada finaliza escribiendo FIN.
    """

    productos = []

    print("\nEscribí tu lista de compras.")
    print("Una cosa por línea.")
    print("Cuando termines, escribí FIN.\n")

    while True:

        linea = input("> ").strip()

        if linea.upper() == "FIN":
            break

        if not linea:
            continue

        producto = procesar_producto(linea)

        if producto:

            productos.append(producto)

    return productos