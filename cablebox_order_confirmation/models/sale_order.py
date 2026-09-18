from odoo import api, models, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # add field if not present; if present, this will use same name
    commitment_date = fields.Date(string='Commitment Date', copy=False)
    pedido_number = fields.Char(string='Nº Pedido', copy=False, readonly=True, index=True)

    @api.onchange('commitment_date', 'expected_date')
    def _onchange_commitment_date(self):
        # commitment_date is a Date here (overridden above) while core's
        # expected_date is a Datetime; normalize before comparing to avoid
        # "can't compare datetime.datetime to datetime.date".
        if self.commitment_date and self.expected_date:
            commitment_date = fields.Datetime.to_datetime(self.commitment_date)
            expected_date = fields.Datetime.to_datetime(self.expected_date)
            if commitment_date < expected_date:
                return {
                    'warning': {
                        'title': _('Requested date is too soon.'),
                        'message': _(
                            "The delivery date is sooner than the expected date."
                            " You may be unable to honor the delivery date."
                        ),
                    }
                }

    def action_open_import_confirmation_wizard(self):
        self.ensure_one()
        return {
            'name': _('Importar confirmación del pedido'),
            'type': 'ir.actions.act_window',
            'res_model': 'cablebox.order.confirmation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    def _update_commitment_date(self):
        for order in self:
            # use existing field 'recepcion_entrega' on sale.order.line
            dates = order.order_line.mapped('recepcion_entrega')
            # filter non empty
            real_dates = [d for d in dates if d]
            if real_dates:
                # take max
                max_date = max(real_dates)
                order.commitment_date = max_date
            else:
                order.commitment_date = False

    def action_confirm(self):
        """Override confirmation to assign a configurable sequence number to 'pedido_number'
        when a quotation becomes a confirmed order. The sequence is editable from
        Settings -> Technical -> Sequences and should have code 'sale.order.pedido'."""
        res = super(SaleOrder, self).action_confirm()
        seq_code = 'sale.order.pedido'
        for order in self:
            # assign only if not already set
            if not order.pedido_number:
                try:
                    seq = self.env['ir.sequence'].next_by_code(seq_code)
                    if seq:
                        order.pedido_number = seq
                except Exception:
                    # don't fail confirmation if sequence missing; just ignore
                    _logger = None
        return res



