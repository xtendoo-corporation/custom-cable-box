# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_proyecto = fields.Char(string="Proyecto")
    x_ref_sap = fields.Char(string="Ref. SAP")
