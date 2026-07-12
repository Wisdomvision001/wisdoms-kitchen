import unittest

from kitchen import adjust_cart_quantity


class CartQuantityTests(unittest.TestCase):
    def test_reduce_quantity_removes_item_when_it_hits_zero(self):
        cart = {"1": 2, "2": 1}
        updated_cart = adjust_cart_quantity(cart, "1", -1)
        self.assertEqual(updated_cart, {"1": 1, "2": 1})

    def test_reduce_quantity_removes_item_when_quantity_is_one(self):
        cart = {"1": 1}
        updated_cart = adjust_cart_quantity(cart, "1", -1)
        self.assertEqual(updated_cart, {})


if __name__ == "__main__":
    unittest.main()
