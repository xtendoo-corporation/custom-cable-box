import base64
import tempfile
import os
import re
import json
import difflib
import logging
from datetime import datetime

from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CableboxOrderConfirmationWizard(models.TransientModel):
    _name = 'cablebox.order.confirmation.wizard'
    _description = 'Importar confirmación del pedido (PDF)'

    order_id = fields.Many2one('sale.order', string='Order', required=True)
    pdf_file = fields.Binary(string='PDF file', required=True)

    def _extract_text_from_pdf(self, file_path=None, file_binary=None):
        # Try to extract text using pdfminer if available, else fallback to PyPDF2
        text = ''
        if file_path:
            if not os.path.exists(file_path):
                raise UserError(_('File not found: %s') % file_path)
            try:
                from pdfminer.high_level import extract_text

                text = extract_text(file_path)
                return text
            except Exception:
                pass
            try:
                import PyPDF2

                with open(file_path, 'rb') as fh:
                    reader = PyPDF2.PdfReader(fh)
                    for page in reader.pages:
                        text += page.extract_text() or ''
                return text
            except Exception:
                raise UserError(_('No library available to extract PDF text. Install pdfminer.six or PyPDF2.'))

        if file_binary:
            # write to temp file
            fd, tmp = tempfile.mkstemp(suffix='.pdf')
            os.close(fd)
            try:
                with open(tmp, 'wb') as f:
                    f.write(base64.b64decode(file_binary))
                return self._extract_text_from_pdf(file_path=tmp)
            finally:
                try:
                    os.remove(tmp)
                except Exception:
                    pass

        raise UserError(_('No PDF provided'))

    def _find_date_near(self, text, idx):
        # search within window for date patterns
        window = 400
        start = max(0, idx - window)
        end = min(len(text), idx + window)
        sample = text[start:end]
        # patterns: dd/mm/yyyy, dd-mm-yyyy, yyyy-mm-dd, dd Month yyyy
        patterns = [r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
                    r"(\d{4}[\-]\d{2}[\-]\d{2})",
                    r"(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4})"]
        for p in patterns:
            m = re.search(p, sample)
            if m:
                return m.group(1)
        return False

    def _parse_dates_for_products(self, text, product_codes):
        # product_codes: list of strings to search
        res = {}
        lower_text = text
        for code in product_codes:
            if not code:
                continue
            # try exact code occurrence
            idx = lower_text.find(code)
            if idx >= 0:
                date_str = self._find_date_near(lower_text, idx)
                if date_str:
                    res[code] = date_str
                    continue
            # try with brackets [code]
            idx = lower_text.find('[' + code + ']')
            if idx >= 0:
                date_str = self._find_date_near(lower_text, idx)
                if date_str:
                    res[code] = date_str
                    continue
            # try product name fragments (skip here)
        return res

    def _parse_date_string(self, s):
        s = s.strip()
        # try common formats (including dots)
        for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d %b %Y', '%d %B %Y', '%d/%m/%y', '%d.%m.%Y', '%d.%m.%y'):
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                continue
        # fallback: try to extract numbers
        m = re.search(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", s)
        if m:
            try:
                return datetime.strptime(m.group(1), '%d/%m/%Y').date()
            except Exception:
                try:
                    return datetime.strptime(m.group(1), '%d-%m-%Y').date()
                except Exception:
                    pass
        m = re.search(r"(\d{4}-\d{2}-\d{2})", s)
        if m:
            try:
                return datetime.strptime(m.group(1), '%Y-%m-%d').date()
            except Exception:
                pass
        return False

    def _parse_dates_by_name(self, text, order):
        """Parse text searching for 'DATE OF READINESS' and map found dates to order lines by name matching."""
        res = {}
        lines = [l.strip() for l in text.splitlines()]
        # detect if PDF appears to be in English to decide whether to use ir.translation
        english_pdf = 'DATE OF READINESS' in text.upper()
        # prepare normalized candidate names for each order line
        line_candidates = []
        for line in order.order_line:
            names = set()
            if line.product_id:
                names.add(str(line.product_id.display_name or ''))
                names.add(str(line.product_id.name or ''))
                tmpl = getattr(line.product_id, 'product_tmpl_id', None)
                if tmpl:
                    tname = tmpl.name or ''
                    if isinstance(tname, str) and tname.strip().startswith('{'):
                        try:
                            j = json.loads(tname)
                            for v in j.values():
                                names.add(str(v or ''))
                        except Exception:
                            names.add(str(tname))
                    else:
                        names.add(str(tname))
                    # If the PDF is English, try to read translations from ir.translation
                    if english_pdf:
                        try:
                            # res_id in ir.translation may be stored as string or int depending on DB
                            domain = [
                                ('name', '=', 'product.template,name'),
                                ('res_id', 'in', [str(tmpl.id), tmpl.id]),
                                ('lang', 'ilike', 'en'),
                            ]
                            trans = self.env['ir.translation'].search(domain)
                            for tr in trans:
                                val = (tr.value or tr.src or '').strip()
                                if val and val.lower() not in ('false',):
                                    names.add(str(val))
                            if trans:
                                _logger.debug('Found ir.translation entries for tmpl %s: %s', tmpl.id, [t.id for t in trans])
                        except Exception:
                            # don't fail if translations cannot be read for any reason
                            _logger.debug('ir.translation lookup failed for template %s', getattr(tmpl, 'id', None))
            if line.name:
                names.add(str(line.name))
            norm_names = [self._normalize_text(n) for n in names if n]
            line_candidates.append((line, norm_names))

        for idx, l in enumerate(lines):
            if not l:
                continue
            if 'DATE OF READINESS' in l.upper():
                # find date in same line or next two lines
                m = re.search(r"(\d{1,2}[\.\-/]\d{1,2}[\.\-/]\d{2,4})", l)
                date_str = m.group(1) if m else None
                if not date_str:
                    for j in range(1, 3):
                        if idx + j < len(lines):
                            m2 = re.search(r"(\d{1,2}[\.\-/]\d{1,2}[\.\-/]\d{2,4})", lines[idx + j])
                            if m2:
                                date_str = m2.group(1)
                                break
                if not date_str:
                    continue
                dt = self._parse_date_string(date_str)
                if not dt:
                    continue

                # build context by looking forward up to 6 lines: in the PDF layout the
                # product description follows the "DATE OF READINESS" line, not the other way around
                context = ''
                collected = 0
                j = idx + 1
                while j < len(lines) and collected < 6:
                    piece = lines[j]
                    if not piece:
                        if context:
                            break
                        j += 1
                        continue
                    if 'DATE OF READINESS' in piece.upper():
                        break
                    if piece.upper().startswith('QUANTITY') or piece.upper().startswith('U.M.'):
                        break
                    context = (context + ' ' + piece).strip()
                    collected += 1
                    j += 1
                norm_context = self._normalize_text(context)
                _logger.debug('DATE OF READINESS found: %s ; context=%s', dt, context)

                # match against order lines using token overlap + fuzzy ratio
                best_line = None
                best_score = 0.0
                for oline, names in line_candidates:
                    for cand in names:
                        if not cand:
                            continue
                        a = set(cand.split())
                        b = set(norm_context.split())
                        token_score = len(a & b) if a and b else 0
                        ratio = difflib.SequenceMatcher(None, cand, norm_context).ratio()
                        score = token_score * 2 + ratio
                        if cand in norm_context or norm_context in cand:
                            score += len(cand.split())
                        if score > best_score:
                            best_score = score
                            best_line = oline
                if best_line and best_score >= 1.5:
                    res[best_line] = dt
        return res

    def _normalize_text(self, s):
        s2 = re.sub(r'[^0-9A-Za-z\s]', ' ', (s or ''))
        s2 = re.sub(r'\s+', ' ', s2).strip().lower()
        return s2

    def action_import_confirmation(self):
        self.ensure_one()
        order = self.order_id
        if not order:
            raise UserError(_('No order selected'))

        # create attachment (only binary upload supported)
        if not self.pdf_file:
            raise UserError(_('Debe subir un pdf en el campo "PDF file"'))
        vals = {
            'name': ('order_confirmation_%s.pdf' % order.name),
            'type': 'binary',
            'datas': self.pdf_file,
            'res_model': 'sale.order',
            'res_id': order.id,
            'mimetype': 'application/pdf'
        }
        attachment = self.env['ir.attachment'].create(vals)
        attachment_id = attachment.id

        # extract text from uploaded PDF binary
        text = self._extract_text_from_pdf(file_binary=self.pdf_file)

        # (no attachment created for extracted text per configuration)

        # prepare product codes from order lines
        codes = []
        line_by_code = {}
        for line in order.order_line:
            code = False
            if line.product_id and line.product_id.default_code:
                code = str(line.product_id.default_code)
            else:
                code = False
            if code:
                codes.append(code)
                line_by_code[code] = line
        _logger.info('Product codes extracted from order %s: %s', order.name, codes)
        _logger.info('Line mapping (code -> line id): %s', {c: l.id for c, l in line_by_code.items()})

        # Try to parse dates by product name context (no attachments created)
        parsed_map = self._parse_dates_by_name(text, order)
        _logger.info('Parsed dates by name for order %s: %s', order.name, {l.id: d for l, d in parsed_map.items()})

        updated_lines = []
        for line, dt in parsed_map.items():
            _logger.info('Setting recepcion_entrega=%s on line id=%s (product %s)', dt, line.id, line.product_id and line.product_id.default_code or line.product_id and line.product_id.display_name)
            line.recepcion_entrega = dt
            updated_lines.append(line.id)

        # update commitment date on order
        order._update_commitment_date()
        # return action to show order
        return {'type': 'ir.actions.client', 'tag': 'reload'}



