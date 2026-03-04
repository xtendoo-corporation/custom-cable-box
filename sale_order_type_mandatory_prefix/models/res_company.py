# Copyright 2026 Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_order_type_mandatory_prefix = fields.Boolean(
        string="Mandatory Sequence on Sale Order Type",
        default=False,
        help="If checked, the sequence (prefix) field will be empty by default "
        "and will be required before saving a Sale Order Type.",
    )

