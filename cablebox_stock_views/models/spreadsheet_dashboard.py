# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SpreadsheetDashboard(models.Model):
    _inherit = "spreadsheet.dashboard"

    def get_readonly_dashboard(self):
        result = super().get_readonly_dashboard()
        snapshot = result.get("snapshot", {})
        for gf in snapshot.get("globalFilters", []):
            if gf.get("type") == "date" and gf.get("label") == "Period":
                gf["defaultValue"] = "year_to_date"
        return result
