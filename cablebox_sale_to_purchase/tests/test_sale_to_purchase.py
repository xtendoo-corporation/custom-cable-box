from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSaleToPurchase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor_a = cls.env['res.partner'].create({'name': 'Proveedor A'})
        cls.vendor_b = cls.env['res.partner'].create({'name': 'Proveedor B'})
        cls.customer = cls.env['res.partner'].create({'name': 'Cliente Test'})

        cls.product_a1 = cls.env['product.product'].create({
            'name': 'Producto A1',
            'purchase_ok': True,
            'seller_ids': [(0, 0, {'partner_id': cls.vendor_a.id, 'min_qty': 0})],
        })
        cls.product_a2 = cls.env['product.product'].create({
            'name': 'Producto A2',
            'purchase_ok': True,
            'seller_ids': [(0, 0, {'partner_id': cls.vendor_a.id, 'min_qty': 0})],
        })
        cls.product_b1 = cls.env['product.product'].create({
            'name': 'Producto B1',
            'purchase_ok': True,
            'seller_ids': [(0, 0, {'partner_id': cls.vendor_b.id, 'min_qty': 0})],
        })
        cls.product_no_vendor = cls.env['product.product'].create({
            'name': 'Producto Sin Proveedor',
            'purchase_ok': True,
        })
        cls.product_not_purchasable = cls.env['product.product'].create({
            'name': 'Producto No Comprable',
            'purchase_ok': False,
        })

    def _create_sale_order(self, product_lines):
        order_lines = [
            (0, 0, {'product_id': product.id, 'product_uom_qty': qty})
            for product, qty in product_lines
        ]
        return self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'order_line': order_lines,
        })

    def test_single_vendor_creates_purchase_directly(self):
        """Si todos los productos comparten proveedor, la compra se crea sin preguntar."""
        order = self._create_sale_order([(self.product_a1, 2), (self.product_a2, 5)])
        action = order.action_create_purchase_order()

        self.assertEqual(action['res_model'], 'purchase.order')
        purchase = self.env['purchase.order'].browse(action['res_id'])
        self.assertEqual(purchase.partner_id, self.vendor_a)
        self.assertEqual(purchase.origin, order.name)
        self.assertEqual(set(purchase.order_line.mapped('product_id')), {self.product_a1, self.product_a2})
        line_a1 = purchase.order_line.filtered(lambda l: l.product_id == self.product_a1)
        self.assertEqual(line_a1.product_qty, 2)
        line_a2 = purchase.order_line.filtered(lambda l: l.product_id == self.product_a2)
        self.assertEqual(line_a2.product_qty, 5)

    def test_multiple_vendors_opens_wizard(self):
        """Si hay más de un proveedor entre los productos, se debe preguntar."""
        order = self._create_sale_order([(self.product_a1, 1), (self.product_b1, 3)])
        action = order.action_create_purchase_order()

        self.assertEqual(action['res_model'], 'cablebox.sale.create.purchase.wizard')
        self.assertEqual(action['context']['default_sale_id'], order.id)

        wizard = self.env['cablebox.sale.create.purchase.wizard'].create({
            'sale_id': order.id,
            'vendor_id': self.vendor_b.id,
        })
        confirm_action = wizard.action_confirm()
        purchase = self.env['purchase.order'].browse(confirm_action['res_id'])
        self.assertEqual(purchase.partner_id, self.vendor_b)
        self.assertEqual(set(purchase.order_line.mapped('product_id')), {self.product_a1, self.product_b1})

    def test_product_without_vendor_does_not_block_detection(self):
        """Un producto sin proveedor no impide detectar el único proveedor conocido
        entre el resto de líneas: esa línea se añade igualmente a la compra."""
        order = self._create_sale_order([(self.product_a1, 1), (self.product_no_vendor, 1)])
        action = order.action_create_purchase_order()

        self.assertEqual(action['res_model'], 'purchase.order')
        purchase = self.env['purchase.order'].browse(action['res_id'])
        self.assertEqual(purchase.partner_id, self.vendor_a)
        self.assertEqual(
            set(purchase.order_line.mapped('product_id')),
            {self.product_a1, self.product_no_vendor},
        )

    def test_no_known_vendor_at_all_opens_wizard(self):
        """Si ningún producto tiene proveedor definido, no hay nada que detectar
        y se debe preguntar."""
        order = self._create_sale_order([(self.product_no_vendor, 1)])
        action = order.action_create_purchase_order()
        self.assertEqual(action['res_model'], 'cablebox.sale.create.purchase.wizard')

    def test_non_purchasable_and_section_lines_are_excluded(self):
        """Las líneas de producto no comprable o de sección/nota no van a la compra."""
        order = self._create_sale_order([(self.product_a1, 1), (self.product_not_purchasable, 1)])
        order.order_line = [(0, 0, {'display_type': 'line_section', 'name': 'Sección'})]

        action = order.action_create_purchase_order()
        purchase = self.env['purchase.order'].browse(action['res_id'])
        self.assertEqual(purchase.order_line.mapped('product_id'), self.product_a1)

    def test_no_purchasable_lines_raises_error(self):
        order = self._create_sale_order([(self.product_not_purchasable, 1)])
        with self.assertRaises(UserError):
            order.action_create_purchase_order()
