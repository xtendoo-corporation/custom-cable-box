# Copyright (C) 2024 Manuel Calero (<https://xtendoo.es>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def cron_action_quotation_confirm(self):
        orders = self.search([
            ('state', 'in', ['draft', 'sent']),
            ('name', 'ilike', 'PED')
        ])
        for order in orders:
            order.action_confirm()

    def action_quotation_confirm(self):
        orders = self.search([
            ('state', 'in', ['draft', 'sent']),
            ('name', 'ilike', 'PED')
        ])
        for order in orders:
            order.action_confirm()
