# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo import _, fields, models
from odoo.exceptions import UserError

from ..script.import_product_script import import_products_to_odoo, parse_xlsx_products


class ImportProductWizard(models.TransientModel):
    _name = "import.product.wizard"
    _description = "Import Product Wizard"

    file = fields.Binary(string="Archivo", required=True)
    filename = fields.Char(string="Nombre del archivo")
    update_existing = fields.Boolean(
        string="Actualizar productos existentes",
        default=True,
        help="Si está marcado, actualiza los productos que ya existen con el mismo código",
    )

    def action_import(self):
        """Procesa la importación de productos desde XLSX."""
        if not self.file:
            raise UserError(_("Por favor, seleccione un archivo XLSX."))

        try:
            # Decodificar el archivo
            file_data = base64.b64decode(self.file)

            # Parsear el archivo XLSX
            products = parse_xlsx_products(file_data)

            # Importar productos a Odoo
            result = import_products_to_odoo(
                self.env, products, update_existing=self.update_existing
            )

        except ImportError as e:
            raise UserError(str(e))
        except ValueError as e:
            raise UserError(str(e))
        except Exception as e:
            raise UserError(_("Error al procesar el archivo: %s") % str(e))

        # Mostrar resultado
        message = _(
            "Importación completada:\n"
            "- Productos creados: %s\n"
            "- Productos actualizados: %s\n"
            "- Productos omitidos: %s"
        ) % (result["created"], result["updated"], result["skipped"])

        if result["errors"]:
            message += _("\n\nErrores encontrados:\n") + "\n".join(
                result["errors"][:10]
            )
            if len(result["errors"]) > 10:
                message += f"\n... y {len(result['errors']) - 10} errores más"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Importación de Productos"),
                "message": message,
                "type": "success" if not result["errors"] else "warning",
                "sticky": True,
            },
        }
