# Copyright 2023 Camilo Prado
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import base64
import requests
import certifi
import urllib3


import uuid
from ast import literal_eval
from datetime import datetime
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
            partner_id = self._search_or_create_partner(self.get_column_value(book, sheet, row, 'partner_id'))
            product_id = self._search_or_create_product(self.get_column_value(book, sheet, row, 'order_line/name'))
            date_order = self.get_column_value(book, sheet, row, 'date_order')
            commitment_date = self.get_column_value(book, sheet, row, 'commitment_date')

            if partner_id and product_id:
                sale_order = {
                    'name': self.get_column_value(book, sheet, row, 'name'),
                    'date_order': date_order,
                    'partner_id': partner_id.id,
                    'note': self.get_column_value(book, sheet, row, 'note'),
                    'client_order_ref': self.get_column_value(book, sheet, row, 'client_order_ref'),
                }
                if commitment_date != "":
                    sale_order.update({'commitment_date': commitment_date})

                order = self.env['sale.order'].create(sale_order)
                if order:
                    self.env['sale.order.line'].create({
                        'order_id': order.id,
                        'product_id': product_id.id,
                        'name': self.get_column_value(book, sheet, row, 'order_line/name'),
                        'product_uom_qty': self.get_column_value(book, sheet, row, 'order_line/product_uom_qty'),
                        'price_unit': self.get_column_value(book, sheet, row, 'order_line/price_unit'),
                    })

                    if "PED" in order.name:
                        order.action_confirm()

                    order.update({
                        'date_order': date_order,
                    })

    def get_column_number(self, sheet, text):
        for col_index in range(sheet.ncols):
            cell_value = sheet.cell(0, col_index).value  # 0 es el índice de la primera fila
            if cell_value == text:
                return col_index
        return None

    def get_column_value(self, book, sheet, row, text):
        # print('text', text)
        key = self.get_column_number(sheet, text)
        # print('key', key)
        if key is not None:
            val = sheet.cell_value(row, key)
            # print('val', val)

            cell_type = sheet.cell_type(row, key)
            # print('cell_type', cell_type)

            if cell_type == xlrd.XL_CELL_DATE:  # pragma: no cover
                # print('date', val)
                return datetime(*xlrd.xldate_as_tuple(val, book.datemode))
            elif cell_type == xlrd.XL_CELL_BOOLEAN:  # pragma: no cover
                # print('bool', val)
                return bool(val)
            else:
                # print('val', val)
                return val
        return None

    def _search_or_create_partner(self, name):
        partner_id = self.env['res.partner'].search([('name', '=', name)], limit=1)
        if not partner_id:
            partner_id = self.env['res.partner'].create({'name': name})
        return partner_id

    def _search_or_create_product(self, name):
        product_id = self.env['product.product'].search([('name', '=', name)], limit=1)
        if not product_id:
            product_id = self.env['product.product'].create({'name': name, 'type': 'product'})
        return product_id
