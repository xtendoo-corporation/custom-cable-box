from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    x_sale_origin = fields.Char(
        related='sale_id.origin',
        string='Documento origen',
        store=True,
        readonly=True,
    )
# Copyright 2025 Cablebox
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    custom_purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Documento de Compra",
    )
