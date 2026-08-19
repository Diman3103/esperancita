import re
from bs4 import BeautifulSoup


# =========================================================
# CONFIGURACIÓN
# =========================================================

DEBUG = False


# =========================================================
# LIMPIAR TEXTO
# =========================================================

def limpiar_texto(texto):

    return " ".join(
        texto.split()
    )


# =========================================================
# CONVERTIR PRECIO
# =========================================================

def convertir_precio(valor):

    valor = valor.strip()

    # Formato argentino:
    # 6.299,99
    if "," in valor:

        valor = valor.replace(
            ".",
            ""
        )

        valor = valor.replace(
            ",",
            "."
        )

    else:

        # Ejemplo:
        # 1.890 -> 1890

        partes = valor.split(".")

        if (
            len(partes) == 2
            and len(partes[1]) == 3
        ):

            valor = valor.replace(
                ".",
                ""
            )

    try:

        return float(valor)

    except ValueError:

        return None


# =========================================================
# EXTRAER PRECIO PRINCIPAL
# =========================================================

def extraer_precio_principal(texto):

    coincidencia = re.search(
        r"\$\s*([\d\.,]+)",
        texto
    )

    if not coincidencia:

        return None

    return convertir_precio(
        coincidencia.group(1)
    )


# =========================================================
# EXTRAER PRECIO POR KG
# =========================================================

def extraer_precio_kilo(texto):

    patrones = [

        r"x\s*Kg\s*,\s*\$\s*([\d\.,]+)",

        r"x\s*kg\s*,\s*\$\s*([\d\.,]+)",

    ]

    for patron in patrones:

        coincidencia = re.search(
            patron,
            texto,
            re.IGNORECASE
        )

        if coincidencia:

            return convertir_precio(
                coincidencia.group(1)
            )

    return None


# =========================================================
# SABER SI UN TEXTO ES PRECIO
# =========================================================

def es_precio(texto):

    return bool(
        re.fullmatch(
            r"\$\s*[\d\.,]+",
            texto.strip()
        )
    )


# =========================================================
# DESCARTAR TEXTOS QUE NO SON PRODUCTOS
# =========================================================

def es_texto_descartable(texto):

    texto_lower = texto.lower().strip()

    descartables = [

        "agregar",

        "agregado",

        "oferta",

        "ver más",

        "ver mas",

        "precio sin impuestos",

        "+",

        "-",

    ]

    if texto_lower in descartables:

        return True

    if texto_lower.startswith(
        "aprox:"
    ):

        return True

    if texto_lower.startswith(
        "x kg"
    ):

        return True

    if texto_lower.startswith(
        "xkg"
    ):

        return True

    if "$" in texto:

        return True

    return False


# =========================================================
# PARECE NOMBRE DE PRODUCTO
# =========================================================

def parece_nombre_producto(texto):

    texto = limpiar_texto(
        texto
    )

    if not texto:

        return False

    if es_texto_descartable(
        texto
    ):

        return False

    if re.fullmatch(
        r"[\d\s\.,]+",
        texto
    ):

        return False

    if len(texto) < 3:

        return False

    if len(texto) > 150:

        return False

    return True


# =========================================================
# OBTENER NOMBRE
# =========================================================

def obtener_nombre(tarjeta):

    # -----------------------------------------------------
    # PRIMERA OPCIÓN
    # -----------------------------------------------------
    # Aprovechamos la clase que vimos en el HTML real:
    # r-ubezar
    # -----------------------------------------------------

    candidatos = tarjeta.find_all(
        "div",
        class_=lambda clases:
            clases
            and "r-ubezar" in clases
    )

    for elemento in candidatos:

        texto = limpiar_texto(
            elemento.get_text(
                " ",
                strip=True
            )
        )

        if parece_nombre_producto(
            texto
        ):

            return texto

    # -----------------------------------------------------
    # SEGUNDA OPCIÓN
    # -----------------------------------------------------

    for elemento in tarjeta.find_all(
        "div"
    ):

        texto = limpiar_texto(
            elemento.get_text(
                " ",
                strip=True
            )
        )

        if parece_nombre_producto(
            texto
        ):

            return texto

    return None


# =========================================================
# EXTRAER CANTIDAD Y UNIDAD
# =========================================================

def extraer_cantidad_unidad(
    nombre
):

    cantidad = None

    unidad = None

    # -----------------------------------------------------
    # x1kg
    # x 1 kg
    # x1,5l
    # -----------------------------------------------------

    patron = re.search(

        r"x\s*"
        r"(\d+(?:[.,]\d+)?)"
        r"\s*"
        r"(kg|g|l|ml|un|u)"
        r"\b",

        nombre,

        re.IGNORECASE

    )

    if not patron:

        # -------------------------------------------------
        # 1kg
        # 500g
        # 2l
        # -------------------------------------------------

        patron = re.search(

            r"(\d+(?:[.,]\d+)?)"
            r"\s*"
            r"(kg|g|l|ml|un|u)"
            r"\b",

            nombre,

            re.IGNORECASE

        )

    if patron:

        cantidad = float(
            patron.group(1).replace(
                ",",
                "."
            )
        )

        unidad = (
            patron.group(2)
            .lower()
        )

    return cantidad, unidad


# =========================================================
# EXTRAER MARCA
# =========================================================

def extraer_marca(nombre):

    marcas = [

        "La Serenísima",
        "Manfrey",
        "Ilolay",

        "Taragüi",
        "Taragui",

        "Mañanita",
        "Mananita",

        "Playadito",
        "Amanda",
        "Rosamonte",

        "Sinceridad",

        "Chango",

        "Dos Anclas",

        "Molto",

        "Arcor",

    ]

    for marca in marcas:

        if marca.lower() in nombre.lower():

            return marca

    return None


# =========================================================
# EXTRAER PRODUCTO DESDE UNA TARJETA
# =========================================================

def extraer_producto_desde_tarjeta(
    tarjeta
):

    texto_completo = limpiar_texto(
        tarjeta.get_text(
            " ",
            strip=True
        )
    )

    if not texto_completo:

        return None

    # -----------------------------------------------------
    # PRECIO
    # -----------------------------------------------------

    precio = extraer_precio_principal(
        texto_completo
    )

    if precio is None:

        return None

    # -----------------------------------------------------
    # NOMBRE
    # -----------------------------------------------------

    nombre = obtener_nombre(
        tarjeta
    )

    if not nombre:

        if DEBUG:

            print(
                "[EXTRACTOR] "
                "Encontré precio pero "
                "NO encontré nombre:"
            )

            print(
                texto_completo[:300]
            )

        return None

    # -----------------------------------------------------
    # PRECIO POR KG
    # -----------------------------------------------------

    precio_por_kg = (
        extraer_precio_kilo(
            texto_completo
        )
    )

    # -----------------------------------------------------
    # CANTIDAD / UNIDAD
    # -----------------------------------------------------

    cantidad, unidad = (
        extraer_cantidad_unidad(
            nombre
        )
    )

    # -----------------------------------------------------
    # MARCA
    # -----------------------------------------------------

    marca = extraer_marca(
        nombre
    )

    # -----------------------------------------------------
    # APROXIMACIÓN
    # -----------------------------------------------------

    aproximacion = None

    for texto in tarjeta.stripped_strings:

        texto = limpiar_texto(
            texto
        )

        if texto.lower().startswith(
            "aprox:"
        ):

            aproximacion = texto

            break

    # -----------------------------------------------------
    # PRODUCTO FINAL
    # -----------------------------------------------------

    producto = {

        "nombre": nombre,

        "marca": marca,

        "precio": precio,

        "precio_por_kg": precio_por_kg,

        "cantidad": cantidad,

        "unidad": unidad,

    }

    if aproximacion:

        producto[
            "aproximacion"
        ] = aproximacion

    # -----------------------------------------------------
    # DEBUG
    # -----------------------------------------------------

    if DEBUG:

        print(
            f"[EXTRACTOR] ✓ "
            f"{nombre} → ${precio}"
        )

        print(
            f"              "
            f"cantidad={cantidad} "
            f"unidad={unidad} "
            f"precio_kg={precio_por_kg}"
        )

    return producto


# =========================================================
# EXTRAER TODOS LOS PRODUCTOS
# =========================================================

def extraer_productos(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    productos = []

    vistos = set()

    # -----------------------------------------------------
    # ENCONTRAR PRECIOS
    # -----------------------------------------------------

    elementos_precio = soup.find_all(
        string=re.compile(
            r"\$\s*[\d\.,]+"
        )
    )

    if DEBUG:

        print(
            "\n[EXTRACTOR] "
            f"Elementos con precio encontrados: "
            f"{len(elementos_precio)}"
        )

    # -----------------------------------------------------
    # RECORRER CADA PRECIO
    # -----------------------------------------------------

    for texto_precio in elementos_precio:

        elemento = texto_precio.parent

        if elemento is None:

            continue

        padre = elemento

        # Subimos por la estructura.
        for _ in range(10):

            if padre is None:

                break

            producto = (
                extraer_producto_desde_tarjeta(
                    padre
                )
            )

            if producto:

                nombre = producto[
                    "nombre"
                ]

                precio = producto[
                    "precio"
                ]

                clave = (
                    nombre.lower(),
                    precio
                )

                if clave not in vistos:

                    vistos.add(
                        clave
                    )

                    productos.append(
                        producto
                    )

                break

            padre = padre.parent

    if DEBUG:

        print(
            "\n[EXTRACTOR] "
            f"Productos extraídos: "
            f"{len(productos)}"
        )

    return productos


# =========================================================
# PRUEBA DIRECTA
# =========================================================

if __name__ == "__main__":

    print(
        "Extractor de Pingüino "
        "cargado correctamente."
    )