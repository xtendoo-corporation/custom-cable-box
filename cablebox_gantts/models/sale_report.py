from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    recepcion_entrega = fields.Date(
        string='Recepción de entrega',
        readonly=True
    )
    delivery_reception_date = fields.Date(
        string='Recepción de entrega',
        readonly=True
    )

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['recepcion_entrega'] = 'l.recepcion_entrega'
        res['delivery_reception_date'] = 'l.recepcion_entrega'
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += ',\n            l.recepcion_entrega'
        return res
