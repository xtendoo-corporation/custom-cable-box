from datetime import datetime as _datetime

from odoo import models, fields, api


def _as_date(value):
    """Normalize a Date/Datetime field value to a plain date for safe comparison."""
    if not value:
        return False
    return value.date() if isinstance(value, _datetime) else value


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
    is_order_ever_delayed = fields.Boolean(
        string='Pedido retrasado (total)',
        compute='_compute_is_order_ever_delayed',
        store=True,
        help="Se marca si algún albarán del pedido se entregó después de la fecha de entrega "
             "comprometida, o si el pedido todavía no se ha entregado por completo habiendo "
             "pasado ya dicha fecha.",
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

    @api.depends('state', 'commitment_date', 'delivery_status', 'picking_ids.state', 'picking_ids.date_done')
    def _compute_is_order_ever_delayed(self):
        today = fields.Date.context_today(self)
        for order in self:
            commitment_date = _as_date(order.commitment_date)
            if order.state != 'sale' or not commitment_date:
                order.is_order_ever_delayed = False
                continue
            pickings = order.picking_ids.filtered(lambda p: p.state != 'cancel')
            delivered_late = any(
                _as_date(picking.date_done) and _as_date(picking.date_done) > commitment_date
                for picking in pickings.filtered(lambda p: p.state == 'done')
            )
            pending_late = order.delivery_status != 'full' and today > commitment_date
            order.is_order_ever_delayed = bool(delivered_late or pending_late)

    def _cron_refresh_order_delay_kpis(self):
        """Recompute is_order_ever_delayed for orders still pending delivery.

        Needed because the "not delivered after commitment date" branch depends on
        today's date, not just on stored field changes.
        """
        orders = self.search([
            ('state', '=', 'sale'),
            ('delivery_status', '!=', 'full'),
            ('commitment_date', '!=', False),
        ])
        orders._compute_is_order_ever_delayed()
