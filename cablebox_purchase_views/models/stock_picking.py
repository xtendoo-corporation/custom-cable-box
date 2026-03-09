# Copyright 2025 Cablebox
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    custom_purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Documento de Compra",
    )
