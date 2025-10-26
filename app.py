from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Dict, List

import pandas as pd
from flask import Flask, render_template

from funciones.crearCubo import cubo_base, pivot_multimedidas
from funciones.generarDatos import generar_dataset
from funciones.operacionesCubo import (
    dice_subset,
    drilldown_producto_region,
    pivot_anio_region,
    rollup_por_anio,
    rollup_por_anio_trimestre,
    slice_por_anio,
)

app = Flask(__name__)


@dataclass
class TableView:
    title: str
    description: str
    headers: List[str]
    rows: List[Dict[str, Any]]


def _flatten_column(col: Any) -> str:
    if isinstance(col, tuple):
        return " / ".join(str(part) for part in col if part not in ("", None))
    return str(col)


def _frame_to_table(df: pd.DataFrame) -> TableView:
    normalized = df.copy()
    if isinstance(normalized.index, pd.MultiIndex) or normalized.index.name is not None:
        normalized = normalized.reset_index()
    else:
        normalized = normalized.reset_index(drop=True)

    normalized = normalized.fillna(0)
    headers = [_flatten_column(col) for col in normalized.columns]
    normalized.columns = headers
    rows = normalized.to_dict(orient="records")
    return TableView("", "", headers, rows)


def _table_with_metadata(title: str, description: str, df: pd.DataFrame) -> TableView:
    table = _frame_to_table(df)
    table.title = title
    table.description = description
    return table


def _collect_functions(module) -> List[Dict[str, str]]:
    items = []
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if func.__module__ != module.__name__:
            continue
        signature = str(inspect.signature(func))
        doc = inspect.getdoc(func) or "Sin descripción"
        items.append({
            "name": name,
            "signature": signature,
            "doc": doc,
        })
    return sorted(items, key=lambda item: item["name"])


@app.route("/")
def index():
    df = generar_dataset()

    cubo = cubo_base(df)
    cara_2024 = cubo.xs(2024, level=0, axis=1)
    seccion_dice = dice_subset(
        df,
        anios=[2024, 2025],
        regiones=["Norte", "Sur"],
        productos=["A", "B"],
    )
    slice_2024 = slice_por_anio(df, 2024)
    drilldown_a_norte = drilldown_producto_region(df, producto="A", region="Norte")

    cubo_completo = cubo
    pivot_regiones = pivot_anio_region(df)
    totales_anio = rollup_por_anio(df)
    totales_anio_trimestre = rollup_por_anio_trimestre(df)
    multimedidas = pivot_multimedidas(df)

    cara_table = _table_with_metadata(
        "Cara del cubo: Ventas 2024 por trimestre",
        "Vista bidimensional del cubo fijando el año 2024 y mostrando las ventas por producto y región.",
        cara_2024,
    )

    seccion_table = _table_with_metadata(
        "Sección (dice) del cubo",
        "Filtro combinado por años 2024-2025, regiones Norte/Sur y productos A/B.",
        seccion_dice,
    )

    cubo_table = _table_with_metadata(
        "Cubo completo",
        "Tabla OLAP Producto x Región x Año/Trimestre con totales incluidos.",
        cubo_completo,
    )

    multimedidas_table = _table_with_metadata(
        "Pivot con múltiples medidas",
        "Sumatoria de Ventas y Cantidad por Producto, Región y Año.",
        multimedidas,
    )

    celda_df = seccion_dice[
        (seccion_dice["Año"] == 2024)
        & (seccion_dice["Trimestre"] == 1)
        & (seccion_dice["Producto"] == "A")
        & (seccion_dice["Región"] == "Norte")
    ]
    celda_table = _table_with_metadata(
        "Detalle de celda",
        "Registros transaccionales que soportan la celda (Producto A, Región Norte, Año 2024, Trimestre 1).",
        celda_df,
    )

    slice_table = _table_with_metadata(
        "Slice 2024",
        "Registros originales filtrados al año 2024.",
        slice_2024,
    )

    drilldown_table = _table_with_metadata(
        "Drill-down Producto A / Región Norte",
        "Detalle jerárquico por Año, Trimestre y Mes para el Producto A en la Región Norte.",
        drilldown_a_norte,
    )

    funciones_generacion = _collect_functions(__import__("funciones.generarDatos", fromlist=["generar_dataset"]))
    funciones_creacion = _collect_functions(__import__("funciones.crearCubo", fromlist=["cubo_base"]))
    funciones_operaciones = _collect_functions(__import__("funciones.operacionesCubo", fromlist=["slice_por_anio"]))

    tables = [
        cara_table,
        seccion_table,
        cubo_table,
        multimedidas_table,
        slice_table,
        drilldown_table,
        _table_with_metadata(
            "Roll-up por año",
            "Agregación anual de ventas.",
            totales_anio,
        ),
        _table_with_metadata(
            "Roll-up año x trimestre",
            "Distribución de ventas por año y trimestre.",
            totales_anio_trimestre,
        ),
        _table_with_metadata(
            "Pivot Año x Región",
            "Matriz de ventas con regiones como columnas.",
            pivot_regiones,
        ),
        celda_table,
    ]

    return render_template(
        "index.html",
        dataset_table=_table_with_metadata(
            "Datos crudos",
            "Dataset generado con medidas de ventas y cantidad por producto, región, canal y tiempo.",
            df,
        ),
        tables=tables,
        funciones={
            "Generación de datos": funciones_generacion,
            "Creación de cubos": funciones_creacion,
            "Operaciones OLAP": funciones_operaciones,
        },
    )


if __name__ == "__main__":
    app.run(debug=True)
