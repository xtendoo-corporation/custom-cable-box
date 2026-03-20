# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


CANCEL_REASON_SELECTION = [
    ('perdida', 'PERDIDA'),
    ('caducada', 'CADUCADA SIN INFORMACIÓN'),
    ('otro_cliente', 'PEDIDO POR OTRO CLIENTE'),
]


class SaleCancelReasonWizard(models.TransientModel):
    _name = 'sale.cancel.reason.wizard'
    _description = 'Asistente de Motivo de Cancelación de Presupuesto'

    order_ids = fields.Many2many(
        'sale.order',
        string='Pedidos de Venta',
        required=True,
    )
    cancel_reason = fields.Selection(
        selection=CANCEL_REASON_SELECTION,
        string='Motivo de Cancelación',
        required=True,
    )

    def action_confirm_cancel(self):
        """Write the cancel reason and proceed with standard cancellation."""
        self.ensure_one()
        if not self.cancel_reason:
            raise UserError(_("Debe seleccionar un motivo de cancelación."))

        self.order_ids.write({'cancel_reason': self.cancel_reason})

        # Call the internal _action_cancel to perform the actual cancellation
        # (cancel draft invoices + set state to 'cancel')
        return self.order_ids._action_cancel()
