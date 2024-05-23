# Copyright 2023 Camilo Prado
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import base64
import requests
import certifi
import urllib3


import uuid
from ast import literal_eval
from datetime import date, datetime as dt
from io import BytesIO

import xlrd
import xlwt

from odoo import _, fields, api, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

try:
    from csv import reader
except (ImportError, IOError) as err:
    _logger.error(err)


class CableboxSaleOrderImport(models.TransientModel):
    _name = "cablebox.sale.order.import"
    _description = "Cablebox Sale Order Import"

    import_file = fields.Binary(string="Import File (*.xlsx)")

    def action_import_file(self):
        """ Process the file chosen in the wizard, create bank statement(s) and go to reconciliation. """
        self.ensure_one()
        if self.import_file:
            self._import_record_data(self.import_file)
        else:
            raise ValidationError(_("Please select Excel file to import"))

    def convert_to_float(self, value):
        value = str(value).replace(',', '.')
        try:
            return float(value)
        except ValueError:
            return 0.0

    @api.model
    def _import_record_data(self, import_file):
        # try:
        decoded_data = base64.decodebytes(import_file)
        book = xlrd.open_workbook(file_contents=decoded_data)
        sheet = book.sheet_by_index(0)
        for row in range(1, sheet.nrows):
            order = self.env['sale.order'].create({
                'name': self.get_column_value(sheet, row, 'name'),
                'date_order': self.get_column_value(sheet, row, 'date_order'),
                'note': self.get_column_value(sheet, row, 'note'),
                'client_order_ref': self.get_column_value(sheet, row, 'client_order_ref'),
                'partner_id': self.env['res.partner'].search(
                    [('name', '=', self.get_column_value(sheet, row, 'partner_id'))], limit=1).id,
                'commitment_date': self.get_column_value(sheet, row, 'commitment_date'),
            })
            self.env['sale.order.line'].create({
                'order_id': order.id,
                'product_id': self.env['product.product'].search(
                    [('name', '=', self.get_column_value(sheet, row, 'order_line/product_id'))], limit=1).id,
                'name': self.get_column_value(sheet, row, 'order_line/name'),
                'product_uom_qty': self.get_column_value(sheet, row, 'order_line/product_uom_qty'),
                'price_unit': self.get_column_value(sheet, row, 'order_line/price_unit'),
            })

    def get_column_number(self, sheet, text):
        for col_index in range(sheet.ncols):
            cell_value = sheet.cell(0, col_index).value  # 0 es el índice de la primera fila
            if cell_value == text:
                return col_index
        return None

    def get_column_value(self, sheet, row, text):
        key = self.get_column_number(sheet, text)
        if key:
            return sheet.cell(row, key).value
        return None
