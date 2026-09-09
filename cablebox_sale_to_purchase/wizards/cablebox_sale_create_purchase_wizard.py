from odoo import _, fields, models


class CableboxSaleCreatePurchaseWizard(models.TransientModel):
    _name = "cablebox.sale.create.purchase.wizard"
    _description = "Elegir proveedor para crear una compra desde una venta"

    sale_id = fields.Many2one("sale.order", string="Venta", required=True, readonly=True)
    vendor_id = fields.Many2one("res.partner", string="Proveedor", required=True)

    def action_confirm(self):
        self.ensure_one()
        purchase = self.sale_id._create_purchase_order(self.vendor_id)
        return purchase._get_records_action(name=_("Compra"))
