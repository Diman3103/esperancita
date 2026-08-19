import json
from pathlib import Path
from datetime import datetime, timedelta


# =========================================================
# CONFIGURACIÓN
# =========================================================

HORAS_VALIDEZ = 24

ARCHIVO_CACHE_ANONIMA = Path(__file__).with_name(
    "cache_anonima.json"
)

ARCHIVO_CACHE_PINGUINO = Path(__file__).with_name(
    "cache_pinguino.json"
)


# =========================================================
# OBTENER ARCHIVO
# =========================================================

def obtener_archivo_cache(supermercado):

    supermercado = supermercado.lower().strip()

    if supermercado in (
        "la anonima",
        "la anónima"
    ):
        return ARCHIVO_CACHE_ANONIMA

    if supermercado in (
        "pinguino",
        "pingüino"
    ):
        return ARCHIVO_CACHE_PINGUINO

    raise ValueError(
        f"Supermercado desconocido: {supermercado}"
    )

# =========================================================
# CARGAR CACHE
# =========================================================

def cargar_cache(supermercado):

    archivo = obtener_archivo_cache(
        supermercado
    )

    if not archivo.exists():

        return {
            "version": 1,
            "ultima_actualizacion": None,
            "busquedas": {}
        }

    try:

        with archivo.open(
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except (
        json.JSONDecodeError,
        OSError
    ):

        return {
            "version": 1,
            "ultima_actualizacion": None,
            "busquedas": {}
        }


# =========================================================
# GUARDAR CACHE
# =========================================================

def guardar_cache(
    supermercado,
    datos
):

    archivo = obtener_archivo_cache(
        supermercado
    )

    with archivo.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            datos,
            f,
            ensure_ascii=False,
            indent=4
        )


# =========================================================
# ¿LA BÚSQUEDA ESTÁ VIGENTE?
# =========================================================

def cache_valida(
    supermercado,
    termino
):

    datos = cargar_cache(
        supermercado
    )

    busquedas = datos.get(
        "busquedas",
        {}
    )

    termino = termino.lower().strip()

    if termino not in busquedas:

        return False

    fecha_texto = busquedas[
        termino
    ].get(
        "fecha"
    )

    if not fecha_texto:

        return False

    try:

        fecha = datetime.fromisoformat(
            fecha_texto
        )

    except ValueError:

        return False

    ahora = datetime.now()

    vencimiento = (
        fecha
        +
        timedelta(
            hours=HORAS_VALIDEZ
        )
    )

    return ahora < vencimiento


# =========================================================
# OBTENER PRODUCTOS DE CACHE
# =========================================================

def obtener_de_cache(
    supermercado,
    termino
):

    datos = cargar_cache(
        supermercado
    )

    termino = termino.lower().strip()

    busqueda = datos.get(
        "busquedas",
        {}
    ).get(
        termino
    )

    if not busqueda:

        return None

    if not cache_valida(
        supermercado,
        termino
    ):

        return None

    return busqueda.get(
        "productos",
        []
    )


# =========================================================
# GUARDAR PRODUCTOS EN CACHE
# =========================================================

def guardar_en_cache(
    supermercado,
    termino,
    productos
):

    datos = cargar_cache(
        supermercado
    )

    termino = termino.lower().strip()

    datos.setdefault(
        "busquedas",
        {}
    )

    datos["busquedas"][termino] = {

        "fecha":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "productos":
            productos
    }

    datos[
        "ultima_actualizacion"
    ] = datetime.now().isoformat(
        timespec="seconds"
    )

    guardar_cache(
        supermercado,
        datos
    )


# =========================================================
# ELIMINAR CACHE VENCIDA
# =========================================================

def limpiar_cache_vencida(
    supermercado
):

    datos = cargar_cache(
        supermercado
    )

    busquedas = datos.get(
        "busquedas",
        {}
    )

    vigentes = {}

    for termino, informacion in busquedas.items():

        fecha_texto = informacion.get(
            "fecha"
        )

        if not fecha_texto:
            continue

        try:

            fecha = datetime.fromisoformat(
                fecha_texto
            )

        except ValueError:

            continue

        vencimiento = (
            fecha
            +
            timedelta(
                hours=HORAS_VALIDEZ
            )
        )

        if datetime.now() < vencimiento:

            vigentes[
                termino
            ] = informacion

    datos["busquedas"] = vigentes

    guardar_cache(
        supermercado,
        datos
    )