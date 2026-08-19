from buscador import buscar_productos
from normalizador import normalizar_solicitud


# =========================================================
# COMPARAR UN PRODUCTO ENTRE LOS DOS SUPERMERCADOS
# =========================================================

def comparar_productos(
    productos_anonima,
    productos_pinguino,
    consulta
):

    # -----------------------------------------------------
    # NORMALIZAR LA CONSULTA
    # -----------------------------------------------------

    if isinstance(
        consulta,
        dict
    ):
        solicitud = consulta

    else:
        solicitud = normalizar_solicitud(
            consulta
        )

    # -----------------------------------------------------
    # BUSCAR COINCIDENCIAS
    # -----------------------------------------------------

    resultados_anonima = buscar_productos(
        productos_anonima,
        solicitud,
        limite=10
    )

    resultados_pinguino = buscar_productos(
        productos_pinguino,
        solicitud,
        limite=10
    )

    # -----------------------------------------------------
    # MEJOR PRODUCTO DE CADA SUPERMERCADO
    # -----------------------------------------------------

    mejor_anonima = (
        resultados_anonima[0]
        if resultados_anonima
        else None
    )

    mejor_pinguino = (
        resultados_pinguino[0]
        if resultados_pinguino
        else None
    )

    # -----------------------------------------------------
    # DETERMINAR GANADOR
    # -----------------------------------------------------

    ganador = None
    supermercado_ganador = None

    if (
        mejor_anonima
        and mejor_pinguino
    ):

        precio_anonima = (
            mejor_anonima["precio"]
        )

        precio_pinguino = (
            mejor_pinguino["precio"]
        )

        if precio_anonima < precio_pinguino:

            ganador = mejor_anonima

            supermercado_ganador = (
                "La Anónima"
            )

        elif precio_pinguino < precio_anonima:

            ganador = mejor_pinguino

            supermercado_ganador = (
                "Pingüino"
            )

        else:

            # Mismo precio
            ganador = mejor_anonima

            supermercado_ganador = (
                "Empate"
            )

    elif mejor_anonima:

        ganador = mejor_anonima

        supermercado_ganador = (
            "La Anónima"
        )

    elif mejor_pinguino:

        ganador = mejor_pinguino

        supermercado_ganador = (
            "Pingüino"
        )

    # -----------------------------------------------------
    # CALCULAR AHORRO
    # -----------------------------------------------------

    ahorro = 0

    if (
        mejor_anonima
        and mejor_pinguino
    ):

        ahorro = abs(
            mejor_anonima["precio"]
            -
            mejor_pinguino["precio"]
        )

    # -----------------------------------------------------
    # DEVOLVER TODO
    # -----------------------------------------------------

    return {

        "solicitud":
            solicitud,

        "anonima":
            resultados_anonima,

        "pinguino":
            resultados_pinguino,

        "mejor_anonima":
            mejor_anonima,

        "mejor_pinguino":
            mejor_pinguino,

        "ganador":
            ganador,

        "supermercado_ganador":
            supermercado_ganador,

        "ahorro":
            ahorro,
    }


# =========================================================
# MOSTRAR RESULTADO
# =========================================================

def imprimir_comparacion(
    resultado
):

    solicitud = resultado[
        "solicitud"
    ]

    print()
    print("=" * 70)

    print(
        f"RESULTADO: "
        f"{solicitud['texto_original']}"
    )

    print("=" * 70)

    # -----------------------------------------------------
    # PINGÜINO
    # -----------------------------------------------------

    print()
    print("PINGÜINO")
    print("-" * 70)

    productos_pinguino = resultado[
        "pinguino"
    ]

    if not productos_pinguino:

        print(
            "No se encontró una opción compatible."
        )

    else:

        for producto in productos_pinguino[:5]:

            print(
                f"{producto['nombre_original']}"
            )

            print(
                f"Precio: "
                f"${producto['precio']:.2f}"
            )

            print(
                f"Score: "
                f"{producto['puntuacion']}"
            )

            print()

    # -----------------------------------------------------
    # LA ANÓNIMA
    # -----------------------------------------------------

    print()
    print("LA ANÓNIMA")
    print("-" * 70)

    productos_anonima = resultado[
        "anonima"
    ]

    if not productos_anonima:

        print(
            "No se encontró una opción compatible."
        )

    else:

        for producto in productos_anonima[:5]:

            print(
                f"{producto['nombre_original']}"
            )

            print(
                f"Precio: "
                f"${producto['precio']:.2f}"
            )

            print(
                f"Score: "
                f"{producto['puntuacion']}"
            )

            print()

    # -----------------------------------------------------
    # RESULTADO FINAL
    # -----------------------------------------------------

    print()
    print("-" * 70)

    ganador = resultado[
        "ganador"
    ]

    supermercado = resultado[
        "supermercado_ganador"
    ]

    if ganador is None:

        print(
            "No se pudo determinar "
            "dónde conviene comprar."
        )

        return

    if supermercado == "Empate":

        print(
            "RESULTADO: EMPATE DE PRECIOS."
        )

    else:

        print(
            f"🏆 CONVIENE COMPRAR "
            f"EN {supermercado.upper()}."
        )

    print()

    print(
        f"Producto: "
        f"{ganador['nombre_original']}"
    )

    print(
        f"Precio: "
        f"${ganador['precio']:.2f}"
    )

    if resultado["ahorro"] > 0:

        print(
            f"Ahorro posible: "
            f"${resultado['ahorro']:.2f}"
        )


# =========================================================
# PRUEBA
# =========================================================

if __name__ == "__main__":

    productos_anonima = [

        {
            "nombre":
                "AZUCAR CHANGO X1KG",

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
                "AZUCAR COMUN X1KG",

            "marca":
                None,

            "precio":
                1690,

            "cantidad":
                1,

            "unidad":
                "kg",
        },
    ]

    productos_pinguino = [

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
                "AZUCAR CHANGO X1KG",

            "marca":
                "Chango",

            "precio":
                1590,

            "cantidad":
                1,

            "unidad":
                "kg",
        },
    ]

    resultado = comparar_productos(

        productos_anonima,

        productos_pinguino,

        "azucar 1kg"
    )

    imprimir_comparacion(
        resultado
    )