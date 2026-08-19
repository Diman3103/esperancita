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