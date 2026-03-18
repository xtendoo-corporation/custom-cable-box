# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo import _, fields, models
from odoo.exceptions import UserError


class ImportProductWizard(models.TransientModel):
    _name = "import.product.wizard"
    _description = "Actualizar Costes desde Excel"

    data_file = fields.Binary(string="Archivo Excel", required=True)
    filename = fields.Char(string="Nombre del Archivo")

    def action_import(self):
        """Actualiza los costes de los productos desde un archivo Excel."""
        if not self.data_file:
            raise UserError(_("Por favor, suba un archivo Excel."))

        try:
            import io
            import openpyxl

            # Cargar el archivo Excel
            file_data = base64.b64decode(self.data_file)
            wb = openpyxl.load_workbook(io.BytesIO(file_data), data_only=True)
            sheet = wb.active

            updated_count = 0
            not_found_codes = []

            # Iterar sobre las filas (saltando la cabecera)
            # Columna B (index 2): CÓDIGO DE PRODUCTO
            # Columna J (index 10): PRECIO DE COSTE
            for row in sheet.iter_rows(min_row=2, values_only=True):
                code = row[1]  # CÓDIGO DE PRODUCTO
                cost = row[9]  # PRECIO DE COSTE
                sales_price = row[11]  # PRECIO AL PÚBLICO

                if not code:
                    continue

                # Asegurarse de que el coste y precio de venta sean números
                try:
                    cost = float(cost) if cost is not None else 0.0
                except ValueError:
                    cost = 0.0

                try:
                    sales_price = float(sales_price) if sales_price is not None else 0.0
                except ValueError:
                    sales_price = 0.0

                # Buscar el producto por referencia interna (default_code)
                product = self.env["product.template"].search(
                    [("default_code", "=", str(code).strip())], limit=1
                )

                if product:
                    # Update sales price on the template
                    product.write({"list_price": sales_price})

                    # Update standard price on the variants + revalue existing stock
                    for variant in product.product_variant_ids:
                        old_price = variant.standard_price
                        qty_in_stock = variant.qty_available

                        # If the variant has on-hand stock that was entered at cost 0
                        # (quantity_svl == 0 but qty_available > 0), we need to create
                        # an SVL manually before calling _change_standard_price,
                        # otherwise Odoo skips the revaluation.
                        if qty_in_stock > 0 and variant.quantity_svl == 0:
                            svl_vals = {
                                "company_id": self.env.company.id,
                                "product_id": variant.id,
                                "description": _(
                                    "Valoración inicial del stock existente (coste actualizado a %s)"
                                )
                                % cost,
                                "value": cost * qty_in_stock,
                                "unit_cost": cost,
                                "quantity": qty_in_stock,
                            }
                            self.env["stock.valuation.layer"].sudo().create(svl_vals)

                        # Now write the price (triggers _change_standard_price on write)
                        variant.with_company(self.env.company).write(
                            {"standard_price": cost}
                        )

                    updated_count += 1
                else:
                    not_found_codes.append(str(code))

        except Exception as e:
            raise UserError(_("Error al procesar el archivo Excel: %s") % str(e))

        # Mostrar resultado
        message = (
            _("Actualización completada:\n" "- Productos actualizados: %s")
            % updated_count
        )
        if not_found_codes:
            message += _("\n- Códigos no encontrados: %s") % ", ".join(
                not_found_codes[:10]
            )
            if len(not_found_codes) > 10:
                message += " ..."

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Costes Actualizados"),
                "message": message,
                "type": "success" if updated_count > 0 else "warning",
                "sticky": True,
            },
        }

    def action_reset_to_zero(self):
        """Pone a 0 el coste de todos los productos (funcionalidad original)."""
        try:
            # Buscar todos los productos que no tengan coste 0
            products = self.env["product.template"].search(
                [("standard_price", "!=", 0.0)]
            )
            count = len(products)

            # Poner su coste a 0
            if count > 0:
                products.write({"standard_price": 0.0})

        except Exception as e:
            raise UserError(_("Error al actualizar los productos: %s") % str(e))

        # Mostrar resultado
        message = (
            _("Actualización completada:\n" "- Productos actualizados a coste 0: %s")
            % count
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Costes a 0"),
                "message": message,
                "type": "success",
                "sticky": True,
            },
        }
