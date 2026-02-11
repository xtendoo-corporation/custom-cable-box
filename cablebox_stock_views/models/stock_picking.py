# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    x_proyecto = fields.Char(
        string="Proyecto",
        related="sale_id.x_proyecto",
        readonly=True,
        store=True,
    )
    x_ref_sap = fields.Char(
        string="Ref. SAP",
        related="sale_id.x_ref_sap",
        readonly=True,
        store=True,
    )
