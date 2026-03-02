# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo import _, fields, models
from odoo.exceptions import UserError


class ImportProductWizard(models.TransientModel):
    _name = "import.product.wizard"
    _description = "Poner Costes a 0"

    def action_import(self):
        """Pone a 0 el coste de todos los productos."""
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
                "title": _("Costes Actualizados"),
                "message": message,
                "type": "success",
                "sticky": True,
            },
        }
