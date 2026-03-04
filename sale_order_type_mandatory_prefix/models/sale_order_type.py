# Copyright 2026 Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderType(models.Model):
    _inherit = "sale.order.type"

    sequence_id_required = fields.Boolean(
        string="Sequence Required",
        compute="_compute_sequence_id_required",
        help="Technical field: True when the company setting forces a mandatory sequence.",
    )

    @api.depends("company_id")
    def _compute_sequence_id_required(self):
        """Read the company setting to know if sequence_id must be mandatory."""
        for record in self:
            company = record.company_id or self.env.company
            record.sequence_id_required = company.sale_order_type_mandatory_prefix

    @api.constrains("sequence_id")
    def _check_mandatory_prefix(self):
        """Validate that sequence_id is set when the company setting is enabled."""
        for record in self:
            company = record.company_id or self.env.company
            if company.sale_order_type_mandatory_prefix and not record.sequence_id:
                raise ValidationError(
                    _(
                        "The sequence (prefix) is mandatory for the Sale Order Type '%(name)s'. "
                        "Please set a sequence before saving.",
                        name=record.name,
                    )
                )
