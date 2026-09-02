from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

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
        string='Días de retraso',
        compute='_compute_delivery_kpis',
        store=True,
    )
    pending_delivery_value = fields.Monetary(
        string='Valor pendiente de entrega',
        compute='_compute_delivery_kpis',
        store=True,
        currency_field='currency_id',
    )

    @api.depends('qty_to_deliver', 'recepcion_entrega', 'order_id.state', 'price_unit', 'discount')
    def _compute_delivery_kpis(self):
        today = fields.Date.context_today(self)
        for line in self:
            is_pending = bool(line.order_id.state == 'sale' and line.qty_to_deliver > 0)
            line.is_delivery_pending = is_pending
            line.is_delivery_delayed = bool(
                is_pending and line.recepcion_entrega and line.recepcion_entrega < today
            )
            line.delivery_delay_days = (today - line.recepcion_entrega).days if line.is_delivery_delayed else 0
            if is_pending:
                price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                line.pending_delivery_value = price_reduce * line.qty_to_deliver
            else:
                line.pending_delivery_value = 0.0

    def _cron_refresh_delivery_kpis(self):
        """Recompute delay-based KPI fields, called daily since they depend on the current date."""
        lines = self.search([('order_id.state', '=', 'sale'), ('qty_to_deliver', '>', 0)])
        lines._compute_delivery_kpis()
