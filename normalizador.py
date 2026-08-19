import re
import unicodedata


# ---------------------------------------------------------
# NORMALIZACIÓN DE UNIDADES
# ---------------------------------------------------------

EQUIVALENCIAS_UNIDADES = {
    # Peso
    "kg": ("g", 1000),
    "kgs": ("g", 1000),
    "k": ("g", 1000),
    "kilo": ("g", 1000),
    "kilos": ("g", 1000),
    "kilogramo": ("g", 1000),
    "kilogramos": ("g", 1000),

    "g": ("g", 1),
    "gr": ("g", 1),
    "grs": ("g", 1),
    "gramo": ("g", 1),
    "gramos": ("g", 1),

    # Volumen
    "l": ("ml", 1000),
    "lt": ("ml", 1000),
    "lts": ("ml", 1000),
    "litro": ("ml", 1000),
    "litros": ("ml", 1000),

    "ml": ("ml", 1),
    "cc": ("ml", 1),
    "cm3": ("ml", 1),

    # Unidades
    "u": ("un", 1),
    "un": ("un", 1),
    "unid": ("un", 1),
    "unidad": ("un", 1),
    "unidades": ("un", 1),
}


# Unidades que pueden aparecer solas en nombres de productos.
# Ej.: "Queso Cremoso Noalsa (Kg)" -> 1000 g.
UNIDADES_SIN_CANTIDAD = {
    "kg": ("g", 1000),
    "kgs": ("g", 1000),
    "k": ("g", 1000),
    "kilo": ("g", 1000),
    "kilos": ("g", 1000),
    "kilogramo": ("g", 1000),
    "kilogramos": ("g", 1000),
    "l": ("ml", 1000),
    "lt": ("ml", 1000),
    "lts": ("ml", 1000),
    "litro": ("ml", 1000),
    "litros": ("ml", 1000),
}

PATRON_UNIDAD = (
    r"kg|kgs|k|kilo|kilos|kilogramo|kilogramos|"
    r"g|gr|grs|gramo|gramos|"
    r"l|lt|lts|litro|litros|"
    r"ml|cc|cm3|"
    r"u|un|unid\.?|unidad|unidades"
)


# ---------------------------------------------------------
# QUITAR ACENTOS
# ---------------------------------------------------------

def quitar_acentos(texto):

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    return "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )


# ---------------------------------------------------------
# NORMALIZAR TEXTO
# ---------------------------------------------------------

def normalizar_texto(texto):

    if texto is None:
        return ""

    texto = str(texto).lower()

    # AZÚCAR -> AZUCAR
    texto = quitar_acentos(texto)

    # Multiplicación -> x
    texto = texto.replace("×", "x")

    # Dejamos letras, números y algunos separadores útiles
    texto = re.sub(
        r"[^a-z0-9.,/+x\- ]+",
        " ",
        texto
    )

    # Espacios múltiples -> un solo espacio
    texto = re.sub(
        r"\s+",
        " ",
        texto
    ).strip()

    return texto


# ---------------------------------------------------------
# NORMALIZAR UNIDAD
# ---------------------------------------------------------

def normalizar_unidad(unidad):

    if not unidad:
        return None

    unidad = normalizar_texto(unidad)

    if unidad not in EQUIVALENCIAS_UNIDADES:
        return unidad

    return EQUIVALENCIAS_UNIDADES[unidad][0]


# ---------------------------------------------------------
# CONVERTIR A UNIDAD BASE
# ---------------------------------------------------------

def convertir_a_unidad_base(cantidad, unidad):

    if cantidad is None or unidad is None:
        return None, None

    unidad = normalizar_texto(unidad)

    if unidad not in EQUIVALENCIAS_UNIDADES:
        return cantidad, unidad

    unidad_base, multiplicador = EQUIVALENCIAS_UNIDADES[unidad]

    cantidad_base = float(cantidad) * multiplicador

    return cantidad_base, unidad_base


# ---------------------------------------------------------
# EXTRAER CANTIDAD Y UNIDAD
# ---------------------------------------------------------

def extraer_cantidad_unidad(texto):

    texto = normalizar_texto(texto)

    # Cantidad explícita:
    # 1kg, 1 kg, x1kg, x 1,5L, 1000g, 1500cc, 1500cm3
    patron = re.search(
        r"(?:x\s*)?"
        r"(\d+(?:[.,]\d+)?)"
        r"\s*"
        r"(" + PATRON_UNIDAD + r")"
        r"\b",
        texto,
        re.IGNORECASE
    )

    if patron:

        cantidad = float(
            patron.group(1).replace(",", ".")
        )

        unidad = patron.group(2).lower()

        return convertir_a_unidad_base(
            cantidad,
            unidad
        )

    # Presentación expresada por kg/l sin cantidad:
    # "(Kg)", "x Kg", "por Kg", etc.
    patron_sin_cantidad = re.search(
        r"(?:^|[\s/])"
        r"(kg|kgs|k|kilo|kilos|kilogramo|kilogramos|"
        r"l|lt|lts|litro|litros)"
        r"(?:$|[\s/.,)])",
        texto,
        re.IGNORECASE
    )

    if patron_sin_cantidad:

        unidad = patron_sin_cantidad.group(1).lower()

        unidad_base, multiplicador = (
            UNIDADES_SIN_CANTIDAD[unidad]
        )

        return float(multiplicador), unidad_base

    return None, None


# ---------------------------------------------------------
# NORMALIZAR SOLICITUD DEL USUARIO
# ---------------------------------------------------------

def normalizar_solicitud(texto):

    texto_original = texto.strip()

    texto_limpio = normalizar_texto(
        texto_original
    )

    cantidad, unidad = extraer_cantidad_unidad(
        texto_limpio
    )

    # Eliminamos la presentación del nombre.
    producto = re.sub(
        r"(?:x\s*)?"
        r"\d+(?:[.,]\d+)?"
        r"\s*"
        r"(" + PATRON_UNIDAD + r")"
        r"\b",
        " ",
        texto_limpio,
        flags=re.IGNORECASE
    )

    # También quitamos una unidad que aparezca sola al final,
    # por ejemplo "(Kg)" o "x Kg", ya que ya fue interpretada
    # como 1000 g por extraer_cantidad_unidad().
    producto = re.sub(
        r"(?:^|\s)x?\s*"
        r"(kg|kgs|k|kilo|kilos|kilogramo|kilogramos|"
        r"l|lt|lts|litro|litros)"
        r"(?=$|\s|[.,)])",
        " ",
        producto,
        flags=re.IGNORECASE
    )

    producto = re.sub(
        r"\s+",
        " ",
        producto
    ).strip()

    # Evitamos que quede un punto de la presentación,
    # por ejemplo "1.5 Lt." -> producto "gaseosa".
    producto = producto.rstrip(" .,")

    return {
        "texto_original": texto_original,
        "producto": producto,
        "cantidad": cantidad,
        "unidad": unidad
    }


# ---------------------------------------------------------
# NORMALIZAR PRODUCTO OBTENIDO DEL SUPERMERCADO
# ---------------------------------------------------------

def normalizar_producto(producto):

    resultado = dict(producto)

    nombre = producto.get(
        "nombre",
        ""
    )

    marca = producto.get(
        "marca",
        ""
    )

    # Nombre normalizado
    resultado["nombre_original"] = nombre

    resultado["nombre_normalizado"] = normalizar_texto(
        nombre
    )

    # Marca normalizada
    resultado["marca_normalizada"] = normalizar_texto(
        marca or ""
    )

    # Cantidad y unidad
    cantidad = producto.get(
        "cantidad"
    )

    unidad = producto.get(
        "unidad"
    )

    if cantidad is not None and unidad is not None:

        cantidad_base, unidad_base = convertir_a_unidad_base(
            cantidad,
            unidad
        )

    else:

        cantidad_base, unidad_base = extraer_cantidad_unidad(
            nombre
        )

    resultado["cantidad_base"] = cantidad_base

    resultado["unidad_base"] = unidad_base

    return resultado


# ---------------------------------------------------------
# PRUEBAS
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("PRUEBAS DEL NORMALIZADOR")
    print("=" * 60)

    pruebas = [
        "Azucar 1KG",
        "AZÚCAR 1000g",
        "Yerba 500g",
        "Leche 1L",
        "Leche 1000ml",
        "Gaseosa 1,5L",
        "Gaseosa 1.5 Lt.",
        "Aceite 900ml",
        "Aceite 900cc",
        "Aceite 900cm3",
        "Huevos 12 unidades",
        "Coca Cola x 2L",
        "Coca Cola x2,5L",
        "Queso Cremoso Horma Fraccionada Noalsa (Kg)",
        "Queso Cremoso Horma Fraccionada Barraza x Kg",
    ]

    for texto in pruebas:

        resultado = normalizar_solicitud(
            texto
        )

        print()
        print("Entrada:")
        print(texto)

        print("Resultado:")
        print(resultado)