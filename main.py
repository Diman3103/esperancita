import os
import platform

from lista_compras import cargar_lista

from la_anonima import buscar_lista as buscar_lista_anonima
from pinguino import buscar_lista as buscar_lista_pinguino

from extractor_anonima import extraer_productos as extraer_anonima
from extractor_pinguino import extraer_productos as extraer_pinguino

from buscador import buscar_aproximaciones

from comparador import comparar_productos

from exportador import (
    limpiar_csv,
    guardar_productos_csv
)

from preferencias import registrar_busqueda

from cache import (
    obtener_de_cache,
    guardar_en_cache
)


# =========================================================
# CONFIGURACIÓN
# =========================================================

LIMPIAR_CONSOLA_AL_FINAL = False


# =========================================================
# LIMPIAR CONSOLA
# =========================================================

def limpiar_consola():

    sistema = platform.system()

    if sistema == "Windows":

        os.system("cls")

    else:

        os.system("clear")


# =========================================================
# MOSTRAR LISTA
# =========================================================

# =========================================================
# OBTENER DATOS DE LA ANÓNIMA USANDO CACHE
# =========================================================

def obtener_productos_anonima(
    terminos
):

    productos_por_busqueda = {}

    terminos_para_scrapear = []

    # -----------------------------------------------------
    # REVISAR CACHE
    # -----------------------------------------------------

    for termino in terminos:

        productos_cache = obtener_de_cache(
            "La Anónima",
            termino
        )

        if productos_cache is not None:

            print(
                f"[CACHE] La Anónima → {termino}"
            )

            productos_por_busqueda[
                termino
            ] = productos_cache

        else:

            print(
                f"[CACHE VENCIDA/NUEVA] "
                f"La Anónima → {termino}"
            )

            terminos_para_scrapear.append(
                termino
            )

    # -----------------------------------------------------
    # SCRAPEAR SOLO LO QUE FALTA
    # -----------------------------------------------------

    if terminos_para_scrapear:

        resultados_html = buscar_lista_anonima(
            terminos_para_scrapear
        )

        for termino, html in resultados_html.items():

            productos = extraer_anonima(
                html
            )

            productos_por_busqueda[
                termino
            ] = productos

            guardar_en_cache(

                "La Anónima",

                termino,

                productos
            )

            print(
                f"[CACHE GUARDADA] "
                f"La Anónima → {termino}"
            )

    return productos_por_busqueda


# =========================================================
# OBTENER DATOS DE PINGÜINO USANDO CACHE
# =========================================================

def obtener_productos_pinguino(
    terminos
):

    productos_por_busqueda = {}

    terminos_para_scrapear = []

    # -----------------------------------------------------
    # REVISAR CACHE
    # -----------------------------------------------------

    for termino in terminos:

        productos_cache = obtener_de_cache(
            "Pingüino",
            termino
        )

        if productos_cache is not None:

            print(
                f"[CACHE] Pingüino → {termino}"
            )

            productos_por_busqueda[
                termino
            ] = productos_cache

        else:

            print(
                f"[CACHE VENCIDA/NUEVA] "
                f"Pingüino → {termino}"
            )

            terminos_para_scrapear.append(
                termino
            )

    # -----------------------------------------------------
    # SCRAPEAR SOLO LO QUE FALTA
    # -----------------------------------------------------

    if terminos_para_scrapear:

        resultados_html = buscar_lista_pinguino(
            terminos_para_scrapear
        )

        for termino, html in resultados_html.items():

            productos = extraer_pinguino(
                html
            )

            productos_por_busqueda[
                termino
            ] = productos

            guardar_en_cache(

                "Pingüino",

                termino,

                productos
            )

            print(
                f"[CACHE GUARDADA] "
                f"Pingüino → {termino}"
            )

    return productos_por_busqueda

def mostrar_lista(lista):

    print()
    print("=" * 70)
    print("LISTA DE COMPRAS")
    print("=" * 70)

    for producto in lista:

        cantidad = producto["cantidad"]

        if cantidad == int(cantidad):
            cantidad = int(cantidad)

        print(
            f"- {producto['nombre']} "
            f"{cantidad}"
            f"{producto['unidad']}"
        )

# =========================================================
# FORMATEAR DINERO
# =========================================================

def dinero(valor):

    return f"${valor:,.2f}".replace(
        ",",
        "X"
    ).replace(
        ".",
        ","
    ).replace(
        "X",
        "."
    )


# =========================================================
# MOSTRAR RESULTADO FINAL
# =========================================================

# =========================================================
# MOSTRAR RESULTADO FINAL
# =========================================================

def mostrar_resultado_final(
    resultados,
    lista
):

    ahorro_total = 0

    productos_comparados = []
    productos_un_solo_supermercado = []
    productos_sin_resultado = []

    # -----------------------------------------------------
    # ANALIZAR CADA PRODUCTO
    # -----------------------------------------------------

    for resultado in resultados:

        solicitud = resultado["solicitud"]

        mejor_anonima = resultado.get(
            "mejor_anonima"
        )

        mejor_pinguino = resultado.get(
            "mejor_pinguino"
        )

        # -------------------------------------------------
        # ENCONTRADO EN AMBOS
        # -------------------------------------------------

        if (
            mejor_anonima is not None
            and mejor_pinguino is not None
        ):

            precio_anonima = mejor_anonima[
                "precio"
            ]

            precio_pinguino = mejor_pinguino[
                "precio"
            ]

            diferencia = abs(
                precio_anonima
                -
                precio_pinguino
            )

            if precio_anonima < precio_pinguino:

                ganador = "La Anónima"

                ahorro = (
                    precio_pinguino
                    -
                    precio_anonima
                )

            elif precio_pinguino < precio_anonima:

                ganador = "Pingüino"

                ahorro = (
                    precio_anonima
                    -
                    precio_pinguino
                )

            else:

                ganador = "Empate"

                ahorro = 0

            ahorro_total += ahorro

            productos_comparados.append({

                "solicitud":
                    solicitud["texto_original"],

                "anonima":
                    mejor_anonima,

                "pinguino":
                    mejor_pinguino,

                "ganador":
                    ganador,

                "ahorro":
                    ahorro
            })

        # -------------------------------------------------
        # ENCONTRADO SOLO EN UN SUPERMERCADO
        # -------------------------------------------------

        elif (
            mejor_anonima is not None
            or mejor_pinguino is not None
        ):

            if mejor_anonima is not None:

                supermercado = "La Anónima"

                producto = mejor_anonima

            else:

                supermercado = "Pingüino"

                producto = mejor_pinguino

            productos_un_solo_supermercado.append({

                "solicitud":
                    solicitud["texto_original"],

                "supermercado":
                    supermercado,

                "producto":
                    producto
            })

        # -------------------------------------------------
        # NO ENCONTRADO
        # -------------------------------------------------

        else:

            productos_sin_resultado.append({

                "solicitud":
                    solicitud["texto_original"],

                "aproximaciones":
                    resultado.get(
                        "aproximaciones",
                        []
                    )
            })

    # =====================================================
    # MOSTRAR RESULTADOS
    # =====================================================

    print("=" * 70)
    print("RESULTADO DE TU COMPRA")
    print("=" * 70)

    # -----------------------------------------------------
    # PRODUCTOS COMPARADOS
    # -----------------------------------------------------

    if productos_comparados:

        print()
        print("🟢 PRODUCTOS COMPARADOS")
        print("-" * 70)

        for item in productos_comparados:

            print()
            print(
                f"✓ {item['solicitud']}"
            )

            producto_a = item[
                "anonima"
            ]

            producto_p = item[
                "pinguino"
            ]

            print(
                f"  La Anónima: "
                f"{producto_a['nombre_original']}"
            )

            print(
                f"  Precio: "
                f"{dinero(producto_a['precio'])}"
            )

            print()

            print(
                f"  Pingüino: "
                f"{producto_p['nombre_original']}"
            )

            print(
                f"  Precio: "
                f"{dinero(producto_p['precio'])}"
            )

            print()

            if item["ganador"] == "Empate":

                print(
                    "  ⚖ Mismo precio en ambos."
                )

            else:

                print(
                    f"  🏆 Conviene "
                    f"{item['ganador']}"
                )

                print(
                    f"  💰 Ahorrás "
                    f"{dinero(item['ahorro'])}"
                )

    # -----------------------------------------------------
    # SOLO UN SUPERMERCADO
    # -----------------------------------------------------

    if productos_un_solo_supermercado:

        print()
        print()
        print("🟡 DISPONIBLE EN UN SOLO SUPERMERCADO")
        print("-" * 70)

        for item in productos_un_solo_supermercado:

            producto = item[
                "producto"
            ]

            print()
            print(
                f"• {item['solicitud']}"
            )

            print(
                f"  Disponible en "
                f"{item['supermercado']}"
            )

            print(
                f"  {producto['nombre_original']}"
            )

            print(
                f"  {dinero(producto['precio'])}"
            )

            print(
                "  No se calcula ahorro "
                "porque no hay precio comparable."
            )

    # -----------------------------------------------------
    # SIN RESULTADO EXACTO
    # -----------------------------------------------------

    if productos_sin_resultado:

        print()
        print()
        print("⚠ SIN RESULTADO EXACTO")
        print("-" * 70)

        for item in productos_sin_resultado:

            print()
            print(
                f"• {item['solicitud']}"
            )

            aproximaciones = item[
                "aproximaciones"
            ]

            if not aproximaciones:

                print(
                    "  No encontramos "
                    "productos similares."
                )

                continue

            print(
                "  Opciones similares:"
            )

            for producto in aproximaciones:

                precio = producto.get(
                    "precio"
                )

                if precio is not None:

                    precio_texto = dinero(
                        precio
                    )

                else:

                    precio_texto = (
                        "precio desconocido"
                    )

                print(
                    f"  → "
                    f"{producto['nombre_original']} "
                    f"{precio_texto}"
                )

    # =====================================================
    # RESUMEN
    # =====================================================

    print()
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)

    print()

    print(
        f"🟢 Productos comparados: "
        f"{len(productos_comparados)}"
    )

    print(
        f"🟡 Disponibles en un solo supermercado: "
        f"{len(productos_un_solo_supermercado)}"
    )

    print(
        f"⚠ Sin resultado exacto: "
        f"{len(productos_sin_resultado)}"
    )

    print()

    if ahorro_total > 0:

        print(
            f"💰 AHORRO TOTAL COMPARANDO "
            f"LOS PRODUCTOS: "
            f"{dinero(ahorro_total)}"
        )

    else:

        print(
            "💰 No hubo ahorro calculable."
        )

    print("=" * 70)

# =========================================================
# PROGRAMA PRINCIPAL
# =========================================================

def main():

    print()
    print("=" * 70)
    print("COMPARADOR DE PRECIOS")
    print("=" * 70)

    # -----------------------------------------------------
    # 1. LISTA DEL USUARIO
    # -----------------------------------------------------

    lista = cargar_lista()

    if not lista:

        print(
            "No se ingresaron productos."
        )

        return

    mostrar_lista(lista)

    # -----------------------------------------------------
    # 2. TÉRMINOS
    # -----------------------------------------------------

    terminos = []

    for producto in lista:

        termino = producto[
            "nombre"
        ].strip()

        if termino and termino not in terminos:

            terminos.append(
                termino
            )

    # -----------------------------------------------------
    # 3. LIMPIAR CSV
    # -----------------------------------------------------

    limpiar_csv()

    # -----------------------------------------------------
    # 4. OBTENER LA ANÓNIMA
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("LA ANÓNIMA")
    print("=" * 70)

    productos_anonima = obtener_productos_anonima(
        terminos
    )


    # -----------------------------------------------------
    # 5. OBTENER PINGÜINO
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("PINGÜINO")
    print("=" * 70)

    productos_pinguino = obtener_productos_pinguino(
        terminos
    )

    # -----------------------------------------------------
    # GUARDAR PRODUCTOS EN CSV
    # -----------------------------------------------------

    for productos in productos_anonima.values():

        guardar_productos_csv(
            productos,
            "La Anónima"
        )


    for productos in productos_pinguino.values():

        guardar_productos_csv(
            productos,
            "Pingüino"
        )

    # -----------------------------------------------------
    # 6. COMPARAR
    # -----------------------------------------------------

    resultados = []

    for producto in lista:

        nombre = producto[
            "nombre"
        ]

        cantidad = producto[
            "cantidad"
        ]

        unidad = producto[
            "unidad"
        ]

        consulta = (
            producto.get(
                "texto_original"
            )
            or
            f"{nombre} {cantidad:g}{unidad}"
        )

        productos_a = (
            productos_anonima.get(
                nombre,
                []
            )
        )

        productos_p = (
            productos_pinguino.get(
                nombre,
                []
            )
        )

        resultado = comparar_productos(

            productos_a,

            productos_p,

            consulta
        )
        if resultado["ganador"] is None:

            aproximaciones_a = buscar_aproximaciones(
                productos_a,
                consulta,
                limite=5
            )

            aproximaciones_p = buscar_aproximaciones(
                productos_p,
                consulta,
                limite=5
            )

            aproximaciones = (
                aproximaciones_a
                +
                aproximaciones_p
            )

            aproximaciones.sort(
                key=lambda producto: (
                    -producto[
                        "puntuacion_aproximada"
                    ]
                )
            )

            resultado[
                "aproximaciones"
            ] = aproximaciones[:5]

        else:

            resultado[
                "aproximaciones"
            ] = []

        resultados.append(
            resultado
        )

        # -------------------------------------------------
        # MEMORIA
        # -------------------------------------------------

        ganador = resultado[
            "ganador"
        ]

        registrar_busqueda(

            solicitud=consulta,

            ganador=(
                ganador["nombre_original"]
                if ganador
                else None
            ),

            supermercado_ganador=(
                resultado[
                    "supermercado_ganador"
                ]
            )
        )

    # -----------------------------------------------------
    # 7. LIMPIAR CONSOLA
    # -----------------------------------------------------

    if LIMPIAR_CONSOLA_AL_FINAL:

        limpiar_consola()

    # -----------------------------------------------------
    # 8. MOSTRAR SOLO RESULTADO
    # -----------------------------------------------------

    mostrar_resultado_final(
        resultados,
        lista
    )


# =========================================================
# EJECUTAR
# =========================================================

if __name__ == "__main__":

    main()