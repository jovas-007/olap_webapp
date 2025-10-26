# OLAP WebApp

Aplicación demostrativa para generar un dataset sintético y explorar operaciones OLAP (slice, dice, roll-up, drill-down, pivotes) sobre un cubo Producto x Región x Tiempo.

## Requisitos

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar script de consola

El punto de entrada original es `usocubos.py`, que imprime en consola los resultados principales.

```bash
python usocubos.py
```

### Iniciar la aplicación web

La aplicación Flask permite visualizar el dataset, las diferentes vistas del cubo y la estructura de funciones.

```bash
python app.py
```

Luego abre <http://127.0.0.1:5000/> en el navegador.
