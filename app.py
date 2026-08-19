from flask import Flask, render_template, request

from normalizador import normalizar_solicitud

from main import (
    obtener_productos_anonima,
    obtener_productos_pinguino,
    comparar_productos,
    buscar_aproximaciones,
    registrar_busqueda,
    limpiar_csv,
    guardar_productos_csv,
    dinero
)


app = Flask(__name__)


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@app.route("/")
def inicio():

    return render_template(
        "index.html"
    )


# =========================================================
# COMPARAR LISTA
# =========================================================

@app.route(
    "/comparar",
    methods=["POST"]
)
def comparar():

    texto_lista = request.form.get(
        "lista",
        ""
    ).strip()

    # -----------------------------------------------------
    # VALIDAR
    # -----------------------------------------------------

    if not texto_lista:

        return render_template(
            "index.html",
            error=(
                "Escribí al menos un "
                "producto en tu lista."
            )
        )

    # -----------------------------------------------------
    # NORMALIZAR LISTA
    # -----------------------------------------------------

    lista = []

    for linea in texto_lista.splitlines():

        linea = linea.strip()

        if not linea:
            continue

        producto = normalizar_solicitud(
            linea
        )

        lista.append(
            producto
        )

    if not lista:

        return render_template(
            "index.html",
            error=(
                "No encontramos productos "
                "en la lista."
            )
        )

    # -----------------------------------------------------
    # TÉRMINOS
    # -----------------------------------------------------

    terminos = []

    for producto in lista:

        termino = producto[
            "producto"
        ].strip()

        if (
            termino
            and termino not in terminos
        ):

            terminos.append(
                termino
            )

    # -----------------------------------------------------
    # LIMPIAR CSV
    # -----------------------------------------------------

    limpiar_csv()

    # -----------------------------------------------------
    # OBTENER LA ANÓNIMA
    # -----------------------------------------------------

    productos_anonima = (
        obtener_productos_anonima(
            terminos
        )
    )

    # -----------------------------------------------------
    # OBTENER PINGÜINO
    # -----------------------------------------------------

    productos_pinguino = (
        obtener_productos_pinguino(
            terminos
        )
    )

    # -----------------------------------------------------
    # GUARDAR CSV
    # -----------------------------------------------------

    for productos in (
        productos_anonima.values()
    ):

        guardar_productos_csv(
            productos,
            "La Anónima"
        )

    for productos in (
        productos_pinguino.values()
    ):

        guardar_productos_csv(
            productos,
            "Pingüino"
        )

    # -----------------------------------------------------
    # RESULTADOS
    # -----------------------------------------------------

    resultados = []

    ahorro_total = 0

    for producto in lista:

        nombre = producto[
            "producto"
        ]

        consulta = (
            producto.get(
                "texto_original"
            )
            or nombre
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

        # -------------------------------------------------
        # PRODUCTOS ENCONTRADOS
        # -------------------------------------------------

        mejor_anonima = resultado.get(
            "mejor_anonima"
        )

        mejor_pinguino = resultado.get(
            "mejor_pinguino"
        )

        # -------------------------------------------------
        # APROXIMACIONES
        # -------------------------------------------------

        aproximaciones_a = (
            buscar_aproximaciones(
                productos_a,
                consulta,
                limite=5
            )
        )

        aproximaciones_p = (
            buscar_aproximaciones(
                productos_p,
                consulta,
                limite=5
            )
        )

        aproximaciones = (
            aproximaciones_a
            +
            aproximaciones_p
        )

        aproximaciones.sort(

            key=lambda producto:
                -producto.get(
                    "puntuacion_aproximada",
                    0
                )

        )

        # -------------------------------------------------
        # CONSTRUIR OPCIONES
        # -------------------------------------------------

        opciones = []

        # -------------------------------------------------
        # OPCIONES DIRECTAS
        # -------------------------------------------------

        if mejor_anonima:

            opciones.append({

                "id":
                    f"la_{len(resultados)}",

                "supermercado":
                    "La Anónima",

                "producto":
                    mejor_anonima,

                "recomendado":
                    (
                        resultado.get(
                            "supermercado_ganador"
                        )
                        == "La Anónima"
                    )

            })

        if mejor_pinguino:

            opciones.append({

                "id":
                    f"pi_{len(resultados)}",

                "supermercado":
                    "Pingüino",

                "producto":
                    mejor_pinguino,

                "recomendado":
                    (
                        resultado.get(
                            "supermercado_ganador"
                        )
                        == "Pingüino"
                    )

            })

        # -------------------------------------------------
        # SI NO HAY OPCIONES DIRECTAS,
        # MOSTRAMOS APROXIMACIONES
        # -------------------------------------------------

        if not opciones:

            for indice, aproximacion in enumerate(
                aproximaciones[:5]
            ):

                supermercado = (
                    aproximacion.get(
                        "supermercado"
                    )
                    or
                    aproximacion.get(
                        "supermercado_nombre"
                    )
                    or
                    "Supermercado"
                )

                opciones.append({

                    "id":
                        f"aprox_{len(resultados)}_{indice}",

                    "supermercado":
                        supermercado,

                    "producto":
                        aproximacion,

                    "recomendado":
                        False

                })

        # -------------------------------------------------
        # DETERMINAR SELECCIÓN INICIAL
        # -------------------------------------------------

        seleccionado_id = None

        for opcion in opciones:

            if opcion["recomendado"]:

                seleccionado_id = opcion[
                    "id"
                ]

                break

        # Si no hay recomendado pero hay
        # una sola opción, la seleccionamos.

        if (
            seleccionado_id is None
            and len(opciones) == 1
        ):

            seleccionado_id = opciones[0][
                "id"
            ]

        # -------------------------------------------------
        # AHORRO DE COMPARACIÓN DIRECTA
        # -------------------------------------------------

        ahorro = 0

        if (
            mejor_anonima
            and mejor_pinguino
        ):

            precio_a = mejor_anonima.get(
                "precio"
            )

            precio_p = mejor_pinguino.get(
                "precio"
            )

            if (
                precio_a is not None
                and precio_p is not None
            ):

                ahorro = abs(
                    precio_a
                    -
                    precio_p
                )

                ahorro_total += ahorro

        # -------------------------------------------------
        # REGISTRAR MEMORIA
        # -------------------------------------------------

        ganador = resultado.get(
            "ganador"
        )

        registrar_busqueda(

            solicitud=consulta,

            ganador=(
                ganador.get(
                    "nombre_original"
                )
                if ganador
                else None
            ),

            supermercado_ganador=
                resultado.get(
                    "supermercado_ganador"
                )

        )

        # -------------------------------------------------
        # GUARDAR RESULTADO
        # -------------------------------------------------

        resultados.append({

            "id":
                len(resultados),

            "solicitud":
                consulta,

            "opciones":
                opciones,

            "seleccionado":
                seleccionado_id,

            "ahorro":
                ahorro

        })

    # -----------------------------------------------------
    # MOSTRAR
    # -----------------------------------------------------

    return render_template(

        "index.html",

        lista_original=
            texto_lista,

        resultados=
            resultados,

        dinero=
            dinero,

        ahorro_total=
            ahorro_total

    )


# =========================================================
# EJECUTAR
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )