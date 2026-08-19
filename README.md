# 🛒 Esperancita

## Comparador inteligente de precios

**Esperancita** es una aplicación web desarrollada en Python que permite
ingresar una lista completa de compras y comparar automáticamente los
productos publicados por distintos supermercados.

Actualmente trabaja con:

- 🛒 La Anónima
- 🛒 Pingüino

A diferencia de un buscador tradicional, Esperancita permite trabajar
con una **lista completa de compras**, comparar precios, detectar
productos disponibles en un solo supermercado y ofrecer alternativas
para que el usuario pueda seleccionar personalmente qué producto desea
comprar.

---

## 🎯 El problema

Los supermercados no utilizan una nomenclatura uniforme para sus
productos.

El mismo tipo de producto puede aparecer con nombres diferentes,
presentaciones distintas o incluso distintas modalidades de venta.

Por ejemplo:

```text
Leche 1L
Leche UAT x1L
Leche 1000ml
```
---

pueden representar productos equivalentes aunque sus nombres no
coincidan exactamente.

Además, algunos productos se venden por unidad, otros por peso y otros
por volumen.

Esperancita intenta trabajar con estas diferencias sin asumir que todos
los supermercados presentan sus productos de la misma manera.


## 💡 La solución

El usuario puede ingresar una lista como:
- Leche 1L
- Yerba 500g
- Azúcar 1kg
- Coca Cola 1,5L

Esperancita procesa la lista y:

* Normaliza las consultas.
* Busca los productos en los supermercados disponibles.
* Utiliza una caché para evitar realizar scraping innecesariamente.
* Extrae nombres y precios.
* Compara las alternativas encontradas.
* Determina dónde conviene comprar cada producto.
* Calcula el ahorro posible.
* Muestra alternativas aproximadas cuando no existe una coincidencia exacta.
* Permite al usuario seleccionar manualmente las opciones que prefiere.
* Construye una lista final personalizada de compra.

## 🧠 Arquitectura
```text
                    USUARIO
                       │
                       ▼
                INTERFAZ WEB
                       │
                       ▼
                     Flask
                       │
                       ▼
                 Normalizador
                       │
                       ▼
                     Caché
                  ╱          ╲
                 ▼            ▼
           LA ANÓNIMA       PINGÜINO
                 │            │
                 ▼            ▼
           Selenium + BeautifulSoup
                 │            │
                 └──────┬─────┘
                        ▼
                   Extractores
                        │
                        ▼
                    Comparador
                        │
                        ▼
               Selección del usuario
                        │
                        ▼
                  Compra final
```

## ⚙️ Tecnologías utilizadas
### Backend
* Python
* Flask
* Selenium
* BeautifulSoup
### Procesamiento de datos
* JSON
* CSV
* Normalización de texto
* Sistema de caché
### Frontend
* HTML
* CSS
* JavaScript

## 🚀 Características principales
Lista de compras

El usuario puede ingresar múltiples productos en una única búsqueda.

- Leche 1L
- Yerba 500g
- Azúcar 1kg
- Coca Cola 1,5L

### Comparación automática

Cuando un producto está disponible en ambos supermercados,
Esperancita compara sus precios y muestra cuál resulta más conveniente.

### Productos disponibles en un solo supermercado

Cuando el producto solamente aparece en uno de los supermercados,
Esperancita lo informa sin inventar un precio comparable.

### Resultados aproximados

Cuando no existe una coincidencia exacta, el sistema puede mostrar
productos similares para que el usuario pueda decidir.

### Selección manual

El usuario puede cambiar la recomendación automática y elegir otra
alternativa encontrada.

### Caché

Los resultados obtenidos mediante scraping se almacenan temporalmente
para evitar realizar búsquedas innecesarias sobre los sitios web.

Actualmente la caché está pensada para actualizar los precios cada
24 horas.

### Lista final

Después de seleccionar los productos, Esperancita genera una sección
con la compra final y calcula el total.

## 📊 Ejemplo

-     Una búsqueda puede producir un resultado como:
      Harina 1kg

-     La Anónima
      Harina de Trigo 000 Chacabuco x 1 Kg.
      $800

-     Pingüino
-     harina trigo morixe 000x1kg
-     $850

-     🏆 Conviene La Anónima
-     💰 Ahorrás $50

Y el usuario puede cambiar manualmente la opción seleccionada antes de
armar su compra final.

## 🗂️ Estructura del proyecto
```text
esperancita/
│
├── app.py
├── main.py
│
├── buscador.py
├── buscar_aproximaciones.py
├── cache.py
├── comparador.py
├── exportador.py
├── lista_compras.py
├── normalizador.py
├── preferencias.py
│
├── extractor_anonima.py
├── extractor_pinguino.py
│
├── la_anonima.py
├── pinguino.py
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
├── tests/
│
├── requirements.txt
├── .gitignore
└── README.md
```
## 🔧 Instalación
- Clonar el repositorio

      git clone https://github.com/Diman3103/esperancita.git

- Entrar al proyecto

      cd esperancita

- Instalar las dependencias

      pip install -r requirements.txt

- Ejecutar la aplicación

      python app.py

- Abrir en el navegador

      http://127.0.0.1:5000

## 🧪 Estado del proyecto

### Versión 1.0
 Scraping de La Anónima
 Scraping de Pingüino
 Extracción de productos
 Normalización de consultas
 Sistema de caché
 Comparación de precios
 Detección de productos disponibles en un solo supermercado
 Búsqueda de alternativas aproximadas
 Interfaz web
 Selección manual de productos
 Lista final personalizada
 Cálculo del total
 Cálculo del ahorro

## ⚠️ Limitaciones

La precisión del sistema depende de la información publicada por cada
supermercado.

Cada sitio puede utilizar:

* nombres diferentes;
* presentaciones diferentes;
* unidades diferentes;
* productos vendidos por peso, volumen o unidad;
* estructuras HTML diferentes.

Por este motivo, cuando no existe una coincidencia inequívoca,
Esperancita prioriza mostrar alternativas para que el usuario pueda
seleccionar manualmente el producto correcto.

El sistema no intenta inventar equivalencias comerciales que no estén
respaldadas por la información disponible en los supermercados.

## 🔮 Próximas mejoras

Algunas mejoras posibles para futuras versiones:

* Enlaces directos a los productos originales.
* Incorporación de nuevos supermercados.
* Mayor cobertura de equivalencias entre productos.
* Tests automatizados.
* Mejoras en la extracción de datos.
* Despliegue online.
* Mejoras de interfaz y experiencia de usuario.

## 📌 Objetivo del proyecto

Esperancita fue desarrollado como un proyecto práctico para explorar
scraping web, automatización, procesamiento y normalización de datos,
caché, comparación de información y desarrollo de interfaces web con
Python.

## 👨‍💻 Autor

### Diman Paredes

Proyecto personal / portfolio.