from odoo import models, fields, api
from datetime import datetime, date as date_cls


class SaleOrderLineFix(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('order_id.date_order', 'order_id.commitment_date', 'order_id.picking_ids.scheduled_date')
    def _compute_cablebox_dates(self):
        for line in self:
            # Inicio: Fecha del pedido
            order_date = line.order_id.date_order or fields.Datetime.now()
            # normalize order_date to date
            if isinstance(order_date, datetime):
                line.date_order = order_date.date()
            elif isinstance(order_date, date_cls):
                line.date_order = order_date
            else:
                try:
                    line.date_order = fields.Date.to_date(order_date)
                except Exception:
                    line.date_order = False

            # Fin: 1. Fecha de compromiso (manual)
            #      2. Si no hay, buscar la fecha programada del albarán (expected)
            #      3. Si no hay nada, usar la fecha de inicio
            picking_date = False
            if hasattr(line.order_id, 'picking_ids') and line.order_id.picking_ids:
                pickings = line.order_id.picking_ids.filtered(lambda p: p.scheduled_date)
                if pickings:
                    picking_date = pickings[0].scheduled_date

            end_date = line.order_id.commitment_date or picking_date or order_date
            # normalize end_date to date
            if isinstance(end_date, datetime):
                end_dt = end_date.date()
            elif isinstance(end_date, date_cls):
                end_dt = end_date
            else:
                try:
                    end_dt = fields.Date.to_date(end_date)
                except Exception:
                    end_dt = False

            line.commitment_date_line = end_dt
            line.expected_date_report = end_dt
            if not line.recepcion_entrega:
                line.recepcion_entrega = end_dt

