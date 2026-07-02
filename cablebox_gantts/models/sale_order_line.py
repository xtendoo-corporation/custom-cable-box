from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    date_order = fields.Date(
        string='Fecha del Pedido',
        compute='_compute_cablebox_dates',
        store=True,
        readonly=True
    )
    commitment_date_line = fields.Date(
        string='Fecha Estimada de Entrega',
        compute='_compute_cablebox_dates',
        store=True,
        readonly=True
    )
    expected_date_report = fields.Date(
        string='Fecha Esperada (Albarán)',
        compute='_compute_cablebox_dates',
        store=True
    )
    recepcion_entrega = fields.Date(
        string='Recepción de entrega',
        store=True,
        readonly=False
    )
    delivery_reception_date = fields.Date(
        string='Recepción de entrega',
        related='recepcion_entrega',
        store=True,
        readonly=True
    )
    display_group = fields.Char(
        string='Grupo Visual',
        compute='_compute_display_group',
        store=True,
        readonly=True
    )
    client_order_ref_line = fields.Char(
        related='order_id.client_order_ref',
        string='Pedido de Compra SAP',
        store=True,
        readonly=True
    )
    delivery_status_percentage = fields.Float(
        compute='_compute_delivery_status_percentage',
        string='Estado de Entrega (%)',
        store=True
    )
    qty_to_deliver = fields.Float(
        compute='_compute_qty_to_deliver',
        string='Cantidad por Entregar',
        store=True
    )
    x_ref_sap = fields.Char(
        related='order_id.x_ref_sap',
        string='Ref. SAP',
        store=True,
        readonly=True
    )
    tag_ids = fields.Many2many(
        comodel_name='crm.tag',
        related='order_id.tag_ids',
        string='Etiquetas',
        readonly=True
    )
    tags_string = fields.Char(
        string='Etiquetas (Texto)',
        compute='_compute_tags_string',
        store=True
    )

    @api.depends('order_id.tag_ids', 'order_id.tag_ids.name')
    def _compute_tags_string(self):
        for line in self:
            tags = line.order_id.tag_ids.mapped('name')
            line.tags_string = f"[{', '.join(tags)}]" if tags else ""

    @api.depends('order_id.name', 'order_id.x_ref_sap', 'order_id.client_order_ref', 'order_id.tag_ids', 'order_id.tag_ids.name')
    def _compute_display_group(self):
        for line in self:
            order = line.order_id
            if not order:
                line.display_group = ""
                continue

            # Para agrupar por pedido pero mostrar solo SAP y Tags,
            # mantenemos el nombre del pedido al principio para asegurar unicidad
            # pero el renderer JS se encargará de ocultarlo en la etiqueta visual.
            parts = [order.name]

            if order.x_ref_sap:
                parts.append(f"REF: {order.x_ref_sap}")
            elif order.client_order_ref:
                parts.append(f"SAP: {order.client_order_ref}")

            # Añadir etiquetas
            tags = order.tag_ids.mapped('name')
            if tags:
                parts.append(f"[{', '.join(tags)}]")

            # Resultado final
            res = " - ".join(parts) if parts else "Sin Referencia"
            line.display_group = res

    @api.depends('order_id.date_order', 'order_id.commitment_date', 'order_id.picking_ids.scheduled_date')
    def _compute_cablebox_dates(self):
        for line in self:
            # Inicio: Fecha del pedido
            order_date = line.order_id.date_order or fields.Datetime.now()
            line.date_order = order_date.date()

            # Fin: 1. Fecha de compromiso (manual)
            #      2. Si no hay, buscar la fecha programada del albarán (expected)
            #      3. Si no hay nada, usar la fecha de inicio
            picking_date = False
            if hasattr(line.order_id, 'picking_ids') and line.order_id.picking_ids:
                # Buscamos el primer albarán que tenga fecha programada
                pickings = line.order_id.picking_ids.filtered(lambda p: p.scheduled_date)
                if pickings:
                    picking_date = pickings[0].scheduled_date

            end_date = line.order_id.commitment_date or picking_date or order_date
            line.commitment_date_line = end_date.date()
            line.expected_date_report = end_date.date()
            if not line.recepcion_entrega:
                line.recepcion_entrega = end_date.date()

    @api.depends('product_uom_qty', 'qty_delivered')
    def _compute_delivery_status_percentage(self):
        for line in self:
            if line.product_uom_qty:
                line.delivery_status_percentage = (line.qty_delivered / line.product_uom_qty) * 100
            else:
                line.delivery_status_percentage = 0.0

    @api.depends('product_uom_qty', 'qty_delivered')
    def _compute_qty_to_deliver(self):
        super(SaleOrderLine, self)._compute_qty_to_deliver()
        for line in self:
            line.qty_to_deliver = line.product_uom_qty - line.qty_delivered
