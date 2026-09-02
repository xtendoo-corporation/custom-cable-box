from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_delivery_pending = fields.Boolean(
        string='Pendiente de entrega',
        compute='_compute_delivery_kpis',
        store=True,
    )
    is_delivery_delayed = fields.Boolean(
        string='Entrega retrasada',
        compute='_compute_delivery_kpis',
        store=True,
    )
    delivery_delay_days = fields.Integer(
        string='Días de retraso (máx. línea)',
        compute='_compute_delivery_kpis',
        store=True,
    )
    pending_delivery_value = fields.Monetary(
        string='Valor pendiente de entrega',
        compute='_compute_delivery_kpis',
        store=True,
    )

    @api.depends(
        'order_line.is_delivery_pending',
        'order_line.is_delivery_delayed',
        'order_line.delivery_delay_days',
        'order_line.pending_delivery_value',
    )
    def _compute_delivery_kpis(self):
        for order in self:
            lines = order.order_line
            pending_lines = lines.filtered('is_delivery_pending')
            delayed_lines = lines.filtered('is_delivery_delayed')
            order.is_delivery_pending = bool(pending_lines)
            order.is_delivery_delayed = bool(delayed_lines)
            order.delivery_delay_days = max(delayed_lines.mapped('delivery_delay_days'), default=0)
            order.pending_delivery_value = sum(pending_lines.mapped('pending_delivery_value'))
