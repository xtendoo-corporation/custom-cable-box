# -*- coding: utf-8 -*-
from odoo import fields, models
from .sale_order import CANCEL_REASON_SELECTION


class SaleReport(models.Model):
    _inherit = "sale.report"

    cancel_reason = fields.Selection(
        selection=CANCEL_REASON_SELECTION,
        string='Motivo de Cancelación',
        readonly=True,
    )

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['cancel_reason'] = "s.cancel_reason"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += ",\n            s.cancel_reason"
        return res
