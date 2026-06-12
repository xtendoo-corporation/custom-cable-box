from odoo import models, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model_create_multi
    def create(self, vals_list):
        authorized_user_params = self.env['ir.config_parameter'].sudo().get_param('cablebox_product_creation_restrict.authorized_product_creator_ids')

        if authorized_user_params:
            # Los Many2many en config_parameter se guardan como una lista de IDs en formato string "[1, 2]" o "1,2"
            try:
                import ast
                authorized_user_ids = ast.literal_eval(authorized_user_params)
                if isinstance(authorized_user_ids, int):
                    authorized_user_ids = [authorized_user_ids]
            except (ValueError, SyntaxError):
                authorized_user_ids = [int(id) for id in authorized_user_params.split(',') if id.strip()]

            if self.env.uid not in authorized_user_ids:
                raise UserError(_("Solo los usuarios autorizados pueden crear productos."))

        return super(ProductTemplate, self).create(vals_list)



