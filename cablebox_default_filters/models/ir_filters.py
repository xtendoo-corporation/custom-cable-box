import ast
from odoo import models


class IrFilters(models.Model):
    _inherit = "ir.filters"

    def action_open_target_model(self):
        """
        Action triggered when clicking a row in the "My Default Filters" list view.
        Returns a window action that opens the original model with this filter's domain and context applied.
        """
        self.ensure_one()

        # Odoo stores domain and context as strings in ir.filters,
        # we need to evaluate them to pass as dict/list to the window action.
        domain = []
        if self.domain and self.domain != "[]":
            try:
                domain = ast.literal_eval(self.domain)
            except Exception:
                pass

        context = {}
        if self.context and self.context != "{}":
            try:
                context = ast.literal_eval(self.context)
            except Exception:
                pass

        # Mapeo del modelo a su Acción principal oficial en Odoo
        # Esto es lo que permite que el menú de arriba cambie de color y cargue la App real
        action_xml_id = "base.action_partner_form"  # fallback
        menu_xml_id = ""

        if self.model_id == "sale.order":
            action_xml_id = "sale.action_orders"
            menu_xml_id = "sale.sale_menu_root"
        elif self.model_id == "purchase.order":
            action_xml_id = "purchase.purchase_rfq"
            menu_xml_id = "purchase.menu_purchase_root"
        elif self.model_id == "account.move":
            action_xml_id = "account.action_move_out_invoice_type"
            menu_xml_id = "account.menu_finance"
        elif self.model_id == "stock.picking":
            action_xml_id = "stock.action_picking_tree_all"
            menu_xml_id = "stock.menu_stock_root"

        try:
            action_id = self.env.ref(action_xml_id).id
        except Exception:
            action_id = ""

        try:
            menu_id = self.env.ref(menu_xml_id).id
        except Exception:
            menu_id = ""

        url = f"/web#model={self.model_id}&view_type=list"
        if action_id:
            url += f"&action={action_id}"
        if menu_id:
            url += f"&menu_id={menu_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }
