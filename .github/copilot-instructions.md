## Instrucciones rápidas para asistentes de código (proyecto OLAP WebApp)

Propósito: ayudar a un agente a comprender rápidamente la arquitectura, convenciones y puntos de integración de este repositorio para que las contribuciones sean seguras y productivas.

1) Resumen de alto nivel
- Este es un proyecto demonstration/educativo que genera un dataset sintético y expone visualizaciones OLAP (cubos, slice, dice, roll-up, drill-down) mediante una pequeña app Flask.
- Punto de entrada web: `app.py` (Flask). Punto de entrada de consola: `usocubos.py`.

2) Estructura y componentes clave (leer antes de editar)
- `funciones/generarDatos.py`: función principal `generar_dataset(seed=42)` que devuelve un pandas.DataFrame con columnas esperadas: `Año, Trimestre, Mes, Región, Canal, Producto, Cantidad, Ventas`.
- `funciones/crearCubo.py`: funciones que producen pivotes sobre DataFrames: `cubo_base(df)` y `pivot_multimedidas(df)`.
- `funciones/operacionesCubo.py`: operaciones OLAP reutilizables (por ejemplo `slice_por_anio`, `dice_subset`, `rollup_por_anio`, `drilldown_producto_region`, `pivot_anio_region`). Todas devuelven pandas.DataFrame.
- `app.py`: orquesta la generación de datos, crea vistas (tables) y renderiza `templates/index.html`. Usa `_collect_functions(...)` para mostrar firmas y docstrings de funciones en la UI — no romper esa convención.
- `templates/index.html` y `static/styles.css`: UI estática. `index.html` espera objetos `TableView` (dataclass definida en `app.py`) con `title`, `description`, `headers`, `rows`.

3) Contrato de las funciones en `funciones/`
- Entrada: la mayoría acepta y espera un `pd.DataFrame` con las columnas listadas arriba. No cambiar nombres de columna sin actualizar `app.py` y plantillas.
- Salida: siempre `pd.DataFrame` (preferible `copy()` al filtrar/transformar). Evitar mutar el DataFrame de entrada in-place.
- Errores: las funciones actuales no lanzan errores personalizados; seguir la tendencia de devolver DataFrames vacíos o con `fillna(0)` cuando sea apropiado.

4) Flujo de datos principal
- `generar_dataset()` → DataFrame transaccional
- funciones de `operacionesCubo.py` aplican filtros/groupby/pivot sobre ese DataFrame
- `crearCubo.py` produce pivotes multidimensionales (uso de `pd.pivot_table(..., margins=True)` para totales)
- `app.py` transforma DataFrames a `TableView` para renderizar en la plantilla

5) Convenciones y patrones específicos del proyecto
- Idioma: documentación y docstrings en español — mantén este idioma en nuevas funciones y descripciones.
- Nombres de columnas y jerarquías de tiempo están en español (`Año`, `Trimestre`, `Mes`). Mantén la capitalización exacta.
- Funciones públicas en `funciones/` son simples, pequeñas y unitarias. Añade nuevas funciones siguiendo ese patrón.
- `app.py` usa `inspect.getmembers(..., inspect.isfunction)` para coletar funciones por módulo. Si añades nuevas funciones que deben mostrarse en la UI, colócalas en `funciones.*` y exporta (import) si cambias la ruta de importación.
- Pivotes usan `margins=True` con `margins_name="Total"` en `crearCubo.py` — respeta esto si replicando lógica de totales.

6) Dependencias y comandos de desarrollo
- Instalar dependencias: `pip install -r requirements.txt` (ver `requirements.txt`).
- Ejecutar app web en desarrollo: `python app.py` (por defecto `debug=True` en `app.py`).
- Ejecutar script de consola: `python usocubos.py`.

7) Sugerencias concretas para cambios por un asistente AI
- No renombres columnas globalmente sin actualizar `app.py` y las plantillas (buscar referencias a `Año`, `Trimestre`, `Producto`, `Región`, `Ventas`, `Cantidad`).
- Preferir operaciones que devuelvan copias (`df.loc[...] .copy()`) — las funciones existentes ya lo usan en varios lugares.
- Para exponer nuevas vistas en la UI: 1) añadir la función en `funciones/`, 2) importar o asegurarte que `_collect_functions` la vea (módulo `funciones.nombreModulo`), 3) añadir llamada en `app.py` si quieres que aparezca como tabla en `tables`.
- Evitar modificaciones pesadas de `app.py` a menos que agregues rutas nuevas; la UI ya lista las funciones automáticamente.

8) Ejemplos específicos (referencias de código)
- Generar dataset: `from funciones.generarDatos import generar_dataset` (ver `app.py`).
- Crear cubo base: `cubo = cubo_base(df)` (ver `funciones/crearCubo.py`).
- Dice (subconjunto): `dice_subset(df, anios=[2024,2025], regiones=["Norte","Sur"], productos=["A","B"])` (ver `app.py` uso ad hoc).

9) Qué evitar
- No eliminar el uso de `inspect` en `app.py` sin proveer una alternativa que siga mostrando firmas/docstrings en la UI.
- No cambiar el formato de `TableView` (dataclass en `app.py`) sin actualizar la plantilla `templates/index.html`.

10) Si necesitas añadir tests o ejemplos
- No hay tests hoy. Si añades pruebas unitarias, usa `pytest` y crea una carpeta `tests/` con pruebas pequeñas: 1) `generar_dataset()` devuelve DataFrame con columnas esperadas; 2) `dice_subset` filtra correctamente; 3) `cubo_base` produce pivot con `Total` en columnas/índices.

Si algo en estas instrucciones no queda claro o quieres que añada ejemplos de cambios (por ejemplo: añadir una nueva vista, o una prueba concreta), dime cuál y lo adapto.
