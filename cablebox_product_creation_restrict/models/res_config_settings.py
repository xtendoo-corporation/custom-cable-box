from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    authorized_product_creator_ids = fields.Many2many(
        'res.users',
        'res_config_cablebox_product_creator_rel',
        'config_id',
        'user_id',
        string='Usuarios autorizados para crear productos',
        help="Solo los usuarios seleccionados podrán crear productos."
    )

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'cablebox_product_creation_restrict.authorized_product_creator_ids',
            self.authorized_product_creator_ids.ids
        )

    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env['ir.config_parameter'].sudo()
        authorized_user_params = params.get_param('cablebox_product_creation_restrict.authorized_product_creator_ids')
        if authorized_user_params:
            import ast
            try:
                authorized_user_ids = ast.literal_eval(authorized_user_params)
                res.update(
                    authorized_product_creator_ids=[(6, 0, authorized_user_ids)],
                )
            except Exception:
                pass
        return res
