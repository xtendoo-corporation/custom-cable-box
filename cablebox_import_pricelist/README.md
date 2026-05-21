# cablebox_import_pricelist

Importador de tarifas para Odoo 18 basado en Excel.

## Qué hace

- Lee solo la primera hoja del Excel.
- Crea o actualiza una lista de precios a partir de esa hoja.
- Usa el nombre de la primera hoja como nombre de la tarifa.
- Permite importar el `PRECIO AL DISTRIBUIDOR` o el `PRECIO AL PÚBLICO`.
- Busca productos por `CÓDIGO DE PRODUCTO` y, como respaldo, por `CÓDIGO EAN`.
- Lee columnas fijas por posición para acelerar el proceso.

## Posiciones fijas que usa el importador

- Columna `B` → `CÓDIGO DE PRODUCTO`
- Columna `C` → `CÓDIGO EAN`
- Columna `D` → `DESCRIPCIÓN DEL PRODUCTO`
- Columna `J` → `PRECIO AL DISTRIBUIDOR`
- Columna `K` → `PRECIO AL PÚBLICO`
- Columna `M` → `CÓDIGO DE MONEDA`

> El importador asume que el Excel mantiene este layout y que la fila 1 es la cabecera.

## Campos del Excel que realmente se usan

### Imprescindibles

- `CÓDIGO DE PRODUCTO`: identificador principal para localizar el producto.
- `PRECIO AL DISTRIBUIDOR` o `PRECIO AL PÚBLICO`: precio fijo a cargar en la tarifa.
- Nombre de la primera hoja: nombre de la tarifa en Odoo.

### Útiles pero opcionales

- `CÓDIGO EAN`: respaldo para localizar el producto si no aparece por referencia interna.
- `CÓDIGO DE MONEDA`: si aparece, se usa para asignar la moneda de la tarifa.
- `DESCRIPCIÓN DEL PRODUCTO`: solo informativa para trazabilidad.

### Campos ignorados

- `SIGLA MARCA`
- `CANTIDAD DE CARTÓN`
- `CANTIDAD MÚLTIPLE`
- `CANTIDAD MÍNIMA`
- `CANTIDAD MÁXIMA`
- `PLAZOS DE ENTREGA`
- `MULTIPLICADOR PRECIO`
- `UNIDAD DE MEDIDA`
- `PRODUCTO COMPUESTO`
- `ESTADO PRODUCTO`
- `ÚLTIMA VARIACIÓN`
- `FAMILIA DE CESIÓN`
- `FAMILIA DE PRODUCTO`
- `CÓDIGO ETIM`
- `PESO BRUTO (KG)`

## Uso

1. Ir a **Ventas > Configuración > Importar tarifas**.
2. Subir el Excel.
3. Elegir qué columna de precio importar.
4. Ejecutar la importación.

## Comportamiento

- Si la tarifa ya existe, se actualiza y se reemplazan sus líneas con la información de la primera hoja del Excel.
- Si la hoja no informa moneda, se usa la moneda de la compañía actual.
- Las líneas sin producto identificable o sin precio válido se omiten y se reportan al finalizar.

