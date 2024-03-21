# Copyright (C) 2024 Manuel Calero (<https://xtendoo.es>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

  #  @api.model
    #  def autoconfirm_sale(self):
    #     for record in self:
    #          if record.state == "draft":
    #             super().action_confirm()

    def action_quotation_confirm(self):
        print("*"*80)
        print("action_quotation_caonfirm")
        print("*"*80)

        for order in self.filtered(lambda so: so.state == 'draft'):
            order.action_confirm()
