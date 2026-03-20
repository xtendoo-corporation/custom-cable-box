# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    total_offers_count = fields.Integer(
        string='Nº Ofertas Totales',
        compute='_compute_offer_counters',
        readonly=True,
    )
    won_offers_count = fields.Integer(
        string='Nº Ofertas Ganadas',
        compute='_compute_offer_counters',
        readonly=True,
    )
    lost_offers_count = fields.Integer(
        string='Nº Ofertas Canceladas (Perdidas)',
        compute='_compute_offer_counters',
        readonly=True,
    )
    conversion_ratio = fields.Float(
        string='Ratio de Conversión (%)',
        compute='_compute_offer_counters',
        readonly=True,
    )

    def _compute_offer_counters(self):
        SaleOrder = self.env['sale.order']

        # Total offers: all orders in any state
        total_data = SaleOrder._read_group(
            [('team_id', 'in', self.ids)],
            ['team_id'],
            ['__count'],
        )
        total_map = {team.id: count for team, count in total_data}

        # Won offers: confirmed orders (state = 'sale')
        won_data = SaleOrder._read_group(
            [('team_id', 'in', self.ids), ('state', '=', 'sale')],
            ['team_id'],
            ['__count'],
        )
        won_map = {team.id: count for team, count in won_data}

        # Lost offers: cancelled with reason 'perdida'
        lost_data = SaleOrder._read_group(
            [('team_id', 'in', self.ids), ('state', '=', 'cancel'), ('cancel_reason', '=', 'perdida')],
            ['team_id'],
            ['__count'],
        )
        lost_map = {team.id: count for team, count in lost_data}

        for team in self:
            total = total_map.get(team.id, 0)
            won = won_map.get(team.id, 0)
            lost = lost_map.get(team.id, 0)
            team.total_offers_count = total
            team.won_offers_count = won
            team.lost_offers_count = lost
            denominator = won + lost
            team.conversion_ratio = (won / denominator * 100) if denominator else 0.0
