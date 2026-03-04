# Copyright 2026 Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("partner_id", "company_id")
    @api.depends_context("partner_id", "company_id", "company")
    def _compute_sale_type_id(self):
        """Override: if 'sale_order_type_mandatory_prefix' is enabled on the company,
        do NOT auto-assign a default type — leave it empty so the user must choose one.
        Only pre-fill if the partner has an explicit sale_type configured."""
        for record in self:
            company = record.company_id or self.env.company
            setting_enabled = company.sale_order_type_mandatory_prefix

            if setting_enabled:
                partner = record.partner_id
                if partner:
                    sale_type = partner.with_company(record.company_id).sale_type
                    if not sale_type:
                        commercial = partner.commercial_partner_id
                        sale_type = commercial.with_company(record.company_id).sale_type
                else:
                    sale_type = False

                record.type_id = sale_type or False
            else:
                super(SaleOrder, record)._compute_sale_type_id()
