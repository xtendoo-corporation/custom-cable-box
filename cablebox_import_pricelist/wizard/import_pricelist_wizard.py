# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import base64

from odoo import _, fields, models
from odoo.exceptions import UserError

from .pricelist_parser import PricelistWorkbookParser


class CableboxImportPricelistWizard(models.TransientModel):
    _name = "cablebox.import.pricelist.wizard"
    _description = "Importar tarifas desde Excel"

    data_file = fields.Binary(string="Archivo Excel", required=True)
    filename = fields.Char(string="Nombre del archivo")
    price_source = fields.Selection(
        selection=[
            ("distributor_price", "Precio al distribuidor"),
            ("public_price", "Precio al público"),
        ],
        string="Columna de precio a importar",
        required=True,
        default="distributor_price",
    )
    replace_existing_items = fields.Boolean(
        string="Reemplazar líneas existentes",
        default=True,
        help="Si la tarifa ya existe, se eliminarán sus líneas actuales antes de crear las nuevas.",
    )

    def action_import(self):
        self.ensure_one()
        if not self.data_file:
            raise UserError(_("Por favor, suba un archivo Excel."))

        parser = PricelistWorkbookParser(price_field=self.price_source)
        try:
            file_content = base64.b64decode(self.data_file)
            sheets_data = parser.parse_workbook(file_content)
        except ValueError as error:
            raise UserError(str(error)) from error
        except Exception as error:
            raise UserError(_("Error al procesar el Excel: %s") % error) from error

        summary = self._import_sheets(sheets_data)
        return self._build_notification(summary)

    def _import_sheets(self, sheets_data):
        summary = {
            "pricelists_created": 0,
            "pricelists_updated": 0,
            "items_created": 0,
            "missing_products": [],
            "missing_prices": [],
        }

        for sheet_data in sheets_data:
            pricelist, created = self._get_or_create_pricelist(sheet_data)
            if created:
                summary["pricelists_created"] += 1
            else:
                summary["pricelists_updated"] += 1

            if self.replace_existing_items:
                pricelist.item_ids.unlink()

            item_values_by_product = {}
            for row in sheet_data["rows"]:
                if row["price"] is None:
                    summary["missing_prices"].append(
                        "%s (fila %s)" % (sheet_data["name"], row["excel_row"])
                    )
                    continue

                target = self._find_product_target(row)
                if not target:
                    identifier = row["product_code"] or row["ean"] or _("sin referencia")
                    summary["missing_products"].append(
                        "%s [%s]" % (sheet_data["name"], identifier)
                    )
                    continue

                item_key = (target["applied_on"], target.get("product_id") or target.get("product_tmpl_id"))
                item_values_by_product[item_key] = {
                    "pricelist_id": pricelist.id,
                    "compute_price": "fixed",
                    "fixed_price": row["price"],
                    **target,
                }

            if item_values_by_product:
                self.env["product.pricelist.item"].create(list(item_values_by_product.values()))
                summary["items_created"] += len(item_values_by_product)

        return summary

    def _get_or_create_pricelist(self, sheet_data):
        pricelist = self.env["product.pricelist"].search(
            [
                ("name", "=", sheet_data["name"]),
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )
        if not pricelist:
            pricelist = self.env["product.pricelist"].search(
                [
                    ("name", "=", sheet_data["name"]),
                    ("company_id", "=", False),
                ],
                limit=1,
            )

        currency = self._get_currency(sheet_data.get("currency_code"))
        values = {
            "name": sheet_data["name"],
            "currency_id": currency.id,
            "company_id": self.env.company.id,
        }

        if pricelist:
            pricelist.write(values)
            return pricelist, False

        pricelist = self.env["product.pricelist"].create(values)
        return pricelist, True

    def _get_currency(self, currency_code):
        currency = self.env.company.currency_id
        if currency_code:
            found_currency = self.env["res.currency"].search(
                [("name", "=", currency_code)],
                limit=1,
            )
            if found_currency:
                currency = found_currency
        return currency

    def _find_product_target(self, row):
        ProductProduct = self.env["product.product"].with_context(active_test=False)
        ProductTemplate = self.env["product.template"].with_context(active_test=False)

        if row["product_code"]:
            product = ProductProduct.search(
                [("default_code", "=", row["product_code"])],
                limit=1,
            )
            if product:
                return {
                    "applied_on": "0_product_variant",
                    "product_id": product.id,
                }

            template = ProductTemplate.search(
                [("default_code", "=", row["product_code"])],
                limit=1,
            )
            if template:
                return {
                    "applied_on": "1_product",
                    "product_tmpl_id": template.id,
                }

        if row["ean"]:
            product = ProductProduct.search(
                [("barcode", "=", row["ean"])],
                limit=1,
            )
            if product:
                return {
                    "applied_on": "0_product_variant",
                    "product_id": product.id,
                }

        return False

    def _build_notification(self, summary):
        message_lines = [
            _("Tarifas creadas: %s") % summary["pricelists_created"],
            _("Tarifas actualizadas: %s") % summary["pricelists_updated"],
            _("Líneas importadas: %s") % summary["items_created"],
        ]

        if summary["missing_prices"]:
            message_lines.append(
                _("Filas sin precio válido: %s")
                % ", ".join(summary["missing_prices"][:5])
            )
        if summary["missing_products"]:
            message_lines.append(
                _("Productos no encontrados: %s")
                % ", ".join(summary["missing_products"][:5])
            )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Importación de tarifas completada"),
                "message": "\n".join(message_lines),
                "type": "success" if summary["items_created"] else "warning",
                "sticky": True,
            },
        }

