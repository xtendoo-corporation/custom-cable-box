from odoo import models, fields


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

    purchase_origin = fields.Char(
        string="Documento origen Compra",
        related="purchase_id.origin",
        store=False,
        readonly=True,
    )
