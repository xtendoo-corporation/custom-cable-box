from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    x_sale_origin = fields.Char(
        related="sale_id.origin",
        string="Documento origen",
        store=True,
        readonly=True,
    )


class StockPicking(models.Model):
    _inherit = "stock.picking"

    purchase_origin = fields.Many2one(
        "purchase.order",
        string="Pedido Compra",
        compute="_compute_order_refs",
        store=False,
    )

    sale_origin = fields.Many2one(
        "sale.order",
        string="Pedido Venta",
        compute="_compute_order_refs",
        store=False,
    )
    purchase_document_origin = fields.Char(
        string="Documento origen Compra",
        related="purchase_id.origin",
        store=False,
        readonly=False,
    )

    @api.depends("picking_type_code", "sale_id", "purchase_id")
    def _compute_order_refs(self):
        for rec in self:  # ✅ ambas líneas dentro del for
            rec.purchase_origin = (
                rec.purchase_id if rec.picking_type_code == "incoming" else False
            )
            rec.sale_origin = (
                rec.sale_id if rec.picking_type_code == "outgoing" else False
            )
