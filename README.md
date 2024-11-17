# Calculadora con Árbol de Operaciones

Esta es una calculadora web que permite realizar operaciones aritméticas básicas y visualizar el árbol de operaciones correspondiente.

## Características

- Operaciones básicas: suma, resta, multiplicación y división
- Interfaz intuitiva con botones
- Visualización del árbol de operaciones en tiempo real
- Generación de árboles para expresiones matemáticas

## Requisitos

- Python 3.x
- Flask
- Graphviz

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/TU_USUARIO/calculadora_arbol.git
cd calculadora_arbol
```

2. Instala Graphviz (necesario para la generación de árboles):
```bash
# En Fedora
sudo dnf install graphviz graphviz-devel
```

3. Instala las dependencias de Python:
```bash
pip install -r requirements.txt
```

## Uso

1. Ejecuta la aplicación:
```bash
python app.py
```

2. Abre tu navegador y ve a `http://localhost:5000`

3. Usa la calculadora:
   - Ingresa números y operaciones usando los botones
   - Presiona "=" para calcular el resultado
   - Presiona "Tree" para generar el árbol de operaciones
   - Presiona "C" para limpiar

## Estructura del Proyecto

```
calculadora_arbol/
│
├── app.py              # Aplicación Flask principal
├── templates/          # Plantillas HTML
│   └── index.html     # Página principal
├── static/            # Archivos estáticos
│   └── css/          # Archivos CSS
├── trees/            # Directorio para los árboles generados
└── requirements.txt   # Dependencias del proyecto
```

## Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios que te gustaría hacer.

## Licencia

[MIT](https://choosealicense.com/licenses/mit/)
