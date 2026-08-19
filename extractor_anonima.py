from bs4 import BeautifulSoup
import re


def extraer_productos(html):

    soup = BeautifulSoup(html, "html.parser")

    productos = []

    tarjetas = soup.select("div.producto-item")

    if not tarjetas:
        print("No se encontraron productos en La Anónima.")
        return productos

    for tarjeta in tarjetas:

        # -------------------------------------------------
        # DATOS PRINCIPALES
        # -------------------------------------------------

        elemento_producto = tarjeta.find(
            attrs={"data-nombre": True}
        )

        if not elemento_producto:
            continue

        nombre = elemento_producto.get(
            "data-nombre"
        )

        precio_texto = elemento_producto.get(
            "data-precio"
        )

        marca = elemento_producto.get(
            "data-marca"
        )

        codigo = elemento_producto.get(
            "data-codigo"
        )

        # -------------------------------------------------
        # PRECIO
        # -------------------------------------------------

        precio = None

        if precio_texto:

            try:

                precio = float(
                    precio_texto
                    .replace(".", "")
                    .replace(",", ".")
                )

            except ValueError:

                precio = None

        if precio is None:
            continue

        # -------------------------------------------------
        # PRECIO POR KG
        # -------------------------------------------------

        precio_por_kg = None

        texto_tarjeta = tarjeta.get_text(
            " ",
            strip=True
        )

        patron_kg = re.search(
            r"Precio por\s*1\s*kg\s*:\s*\$\s*([\d.]+(?:,\d+)?)",
            texto_tarjeta,
            re.IGNORECASE
        )

        if patron_kg:

            try:

                precio_por_kg = float(
                    patron_kg.group(1)
                    .replace(".", "")
                    .replace(",", ".")
                )

            except ValueError:

                precio_por_kg = None

        # -------------------------------------------------
        # CANTIDAD Y UNIDAD
        # -------------------------------------------------

        cantidad = None
        unidad = None

        patron_cantidad = re.search(
            r"x\s*(\d+(?:[.,]\d+)?)\s*(kg|g|l|ml|un|u)\b",
            nombre,
            re.IGNORECASE
        )

        if patron_cantidad:

            cantidad = float(
                patron_cantidad.group(1)
                .replace(",", ".")
            )

            unidad = patron_cantidad.group(2).lower()

        else:

            patron_cantidad = re.search(
                r"(\d+(?:[.,]\d+)?)\s*(kg|g|l|ml|un|u)\b",
                nombre,
                re.IGNORECASE
            )

            if patron_cantidad:

                cantidad = float(
                    patron_cantidad.group(1)
                    .replace(",", ".")
                )

                unidad = patron_cantidad.group(2).lower()

        # -------------------------------------------------
        # PRODUCTO
        # -------------------------------------------------

        producto = {
            "nombre": nombre,
            "marca": marca,
            "precio": precio,
            "precio_por_kg": precio_por_kg,
            "cantidad": cantidad,
            "unidad": unidad,
            "codigo": codigo
        }

        productos.append(producto)

    return productos