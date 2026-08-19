import csv
from pathlib import Path


# =========================================================
# ARCHIVO CSV
# =========================================================

ARCHIVO_CSV = Path(__file__).with_name(
    "productos.csv"
)


# =========================================================
# COLUMNAS DEL CSV
# =========================================================

CAMPOS = [
    "supermercado",
    "nombre",
    "marca",
    "precio",
    "precio_por_kg",
    "cantidad",
    "unidad",
    "codigo",
]


# =========================================================
# CREAR / LIMPIAR CSV
# =========================================================

def limpiar_csv():

    with ARCHIVO_CSV.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as archivo:

        escritor = csv.DictWriter(
            archivo,
            fieldnames=CAMPOS
        )

        escritor.writeheader()


# =========================================================
# GUARDAR PRODUCTOS
# =========================================================

def guardar_productos_csv(
    productos,
    supermercado
):

    filas = []

    for producto in productos:

        fila = {

            "supermercado":
                supermercado,

            "nombre":
                producto.get(
                    "nombre",
                    ""
                ),

            "marca":
                producto.get(
                    "marca",
                    ""
                ),

            "precio":
                producto.get(
                    "precio",
                    ""
                ),

            "precio_por_kg":
                producto.get(
                    "precio_por_kg",
                    ""
                ),

            "cantidad":
                producto.get(
                    "cantidad",
                    ""
                ),

            "unidad":
                producto.get(
                    "unidad",
                    ""
                ),

            "codigo":
                producto.get(
                    "codigo",
                    ""
                ),
        }

        filas.append(
            fila
        )

    # -----------------------------------------------------
    # AGREGAR AL CSV
    # -----------------------------------------------------

    archivo_existe = ARCHIVO_CSV.exists()

    with ARCHIVO_CSV.open(
        "a",
        newline="",
        encoding="utf-8-sig"
    ) as archivo:

        escritor = csv.DictWriter(
            archivo,
            fieldnames=CAMPOS
        )

        # Si el archivo no existía,
        # agregamos los encabezados.

        if not archivo_existe:

            escritor.writeheader()

        escritor.writerows(
            filas
        )


# =========================================================
# CARGAR PRODUCTOS DESDE CSV
# =========================================================

def cargar_productos_csv():

    if not ARCHIVO_CSV.exists():

        return []

    productos = []

    with ARCHIVO_CSV.open(
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as archivo:

        lector = csv.DictReader(
            archivo
        )

        for fila in lector:

            # -------------------------------------------------
            # CONVERTIR NÚMEROS
            # -------------------------------------------------

            for campo in [
                "precio",
                "precio_por_kg",
                "cantidad"
            ]:

                valor = fila.get(
                    campo
                )

                if valor in (
                    "",
                    None
                ):

                    fila[campo] = None

                    continue

                try:

                    fila[campo] = float(
                        valor
                    )

                except ValueError:

                    fila[campo] = None

            productos.append(
                fila
            )

    return productos


# =========================================================
# PRUEBA DEL MÓDULO
# =========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("PRUEBA DEL EXPORTADOR")
    print("=" * 70)

    productos_prueba = [

        {
            "nombre":
                "AZUCAR CHANGO X1KG",

            "marca":
                "Chango",

            "precio":
                1590,

            "precio_por_kg":
                1590,

            "cantidad":
                1,

            "unidad":
                "kg",

            "codigo":
                "123456",
        },

        {
            "nombre":
                "AZUCAR MYRIAM X1KG",

            "marca":
                "Myriam",

            "precio":
                1390,

            "precio_por_kg":
                1390,

            "cantidad":
                1,

            "unidad":
                "kg",

            "codigo":
                "789012",
        },

    ]

    # Primero limpiamos el archivo para
    # que la prueba empiece desde cero.

    limpiar_csv()

    # Guardamos productos simulando
    # los dos supermercados.

    guardar_productos_csv(
        productos_prueba[:1],
        "La Anónima"
    )

    guardar_productos_csv(
        productos_prueba[1:],
        "Pingüino"
    )

    print()
    print(
        f"CSV generado en:"
    )

    print(
        ARCHIVO_CSV
    )

    print()
    print("Productos cargados desde CSV:")
    print()

    productos = cargar_productos_csv()

    for producto in productos:

        print(
            producto
        )