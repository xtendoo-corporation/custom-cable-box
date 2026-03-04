# Copyright 2026 Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("partner_id", "company_id")
    @api.depends_context("partner_id", "company_id", "company")
    def _compute_sale_type_id(self):
        """Override: if 'sale_order_type_mandatory_prefix' is enabled on the company,
        do NOT auto-assign a default type — leave it empty so the user must choose one.
        Only pre-fill if the partner has an explicit sale_type configured."""
        print("\n" + "="*80)
        print("🔴 [DEBUG] _compute_sale_type_id CALLED")
        print(f"🔴 [DEBUG] self: {self}")
        print(f"🔴 [DEBUG] self.ids: {self.ids}")
        print("="*80)

        for record in self:
            print(f"\n🟡 [DEBUG] --- Processing record ---")
            print(f"🟡 [DEBUG] record.id: {record.id}")
            print(f"🟡 [DEBUG] record.name: {record.name}")

            company = record.company_id or self.env.company
            print(f"🟡 [DEBUG] company: {company.name} (id={company.id})")

            # Check if setting is enabled
            setting_enabled = company.sale_order_type_mandatory_prefix
            print(f"🟡 [DEBUG] sale_order_type_mandatory_prefix enabled: {setting_enabled}")

            if setting_enabled:
                print(f"\n🟢 [DEBUG] ✓ ENTERING IF BLOCK (setting is ENABLED)")
                partner = record.partner_id
                print(f"🟢 [DEBUG] partner: {partner.name if partner else 'NONE'}")

                if partner:
                    sale_type = partner.with_company(record.company_id).sale_type
                    print(f"🟢 [DEBUG] partner.sale_type: {sale_type}")

                    if not sale_type:
                        print(f"🟢 [DEBUG] partner.sale_type is empty, checking commercial_partner")
                        commercial = partner.commercial_partner_id
                        print(f"🟢 [DEBUG] commercial_partner: {commercial.name if commercial else 'NONE'}")
                        sale_type = commercial.with_company(record.company_id).sale_type
                        print(f"🟢 [DEBUG] commercial_partner.sale_type: {sale_type}")
                else:
                    sale_type = False
                    print(f"🟢 [DEBUG] No partner, sale_type = False")

                final_type = sale_type or False
                print(f"🟢 [DEBUG] ➜ Setting record.type_id = {final_type}")
                record.type_id = final_type
                print(f"🟢 [DEBUG] ✓ record.type_id assigned: {record.type_id}")

            else:
                print(f"\n🔵 [DEBUG] ✓ ENTERING ELSE BLOCK (setting is DISABLED)")
                print(f"🔵 [DEBUG] Calling super()._compute_sale_type_id()")
                try:
                    super(SaleOrder, record)._compute_sale_type_id()
                    print(f"🔵 [DEBUG] ✓ super() executed successfully")
                    print(f"🔵 [DEBUG] record.type_id after super: {record.type_id}")
                except Exception as e:
                    print(f"🔵 [DEBUG] ❌ ERROR in super(): {str(e)}")
                    import traceback
                    traceback.print_exc()
                    raise

        print("\n" + "="*80)
        print("🔴 [DEBUG] _compute_sale_type_id FINISHED")
        print("="*80 + "\n")
