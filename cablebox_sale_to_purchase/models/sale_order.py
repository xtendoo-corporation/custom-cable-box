from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_purchasable_order_lines(self):
        return self.order_line.filtered(
            lambda line: not line.display_type and line.product_id and line.product_id.purchase_ok
        )

    def action_create_purchase_order(self):
        self.ensure_one()
        lines = self._get_purchasable_order_lines()
        if not lines:
            raise UserError(_("No hay líneas de producto que se puedan comprar en esta venta."))

        vendors = self.env["res.partner"]
        for line in lines:
            seller = line.product_id._select_seller(quantity=line.product_uom_qty)
            if seller:
                vendors |= seller.partner_id

        if len(vendors) == 1:
            purchase = self._create_purchase_order(vendors)
            return purchase._get_records_action(name=_("Compra"))

        return {
            "type": "ir.actions.act_window",
            "name": _("Elegir proveedor"),
            "res_model": "cablebox.sale.create.purchase.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_sale_id": self.id},
        }

    def _create_purchase_order(self, vendor):
        self.ensure_one()
        lines = self._get_purchasable_order_lines()
        purchase = self.env["purchase.order"].create({
            "partner_id": vendor.id,
            "company_id": self.company_id.id,
            "origin": self.name,
        })
        for line in lines:
            self.env["purchase.order.line"].create({
                "order_id": purchase.id,
                "product_id": line.product_id.id,
                "product_qty": line.product_uom_qty,
                "product_uom": (line.product_id.uom_po_id or line.product_id.uom_id).id,
            })
        # taxes_id solo se rellena en el onchange de la UI, no en un compute
        # almacenado, así que hay que calcularlo explícitamente al crear las
        # líneas por ORM.
        purchase.order_line._compute_tax_id()
        return purchase
