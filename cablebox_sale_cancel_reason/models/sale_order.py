# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


CANCEL_REASON_SELECTION = [
    ('perdida', 'PERDIDA'),
    ('caducada', 'CADUCADA SIN INFORMACIÓN'),
    ('otro_cliente', 'PEDIDO POR OTRO CLIENTE'),
]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cancel_reason = fields.Selection(
        selection=CANCEL_REASON_SELECTION,
        string='Motivo de Cancelación',
        copy=False,
        tracking=True,
    )

    def action_cancel(self):
        """Override to always show our cancellation reason wizard."""
        if any(order.locked for order in self):
            from odoo.exceptions import UserError
            raise UserError(_("You cannot cancel a locked order. Please unlock it first."))

        return {
            'name': _('Motivo de Cancelación'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.cancel.reason.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_ids': self.ids,
            },
        }
