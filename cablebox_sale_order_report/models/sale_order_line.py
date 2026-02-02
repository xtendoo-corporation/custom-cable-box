# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_sale_delay = fields.Integer(
        string="Plazo de entrega",
        related="product_id.sale_delay",
        readonly=True,
    )
