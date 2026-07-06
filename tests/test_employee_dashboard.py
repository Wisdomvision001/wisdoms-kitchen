import unittest

from kitchen import summarize_orders_for_day


class EmployeeDashboardTests(unittest.TestCase):
    def test_summarize_orders_for_day_counts_items_and_revenue(self):
        orders = [
            {
                "id": 1,
                "created_at": "2026-07-06T12:00:00",
                "status": "New",
                "items": [
                    {"qty": 2, "subtotal": 22000},
                    {"qty": 1, "subtotal": 18000},
                ],
                "total": 40000,
            },
            {
                "id": 2,
                "created_at": "2026-07-05T15:00:00",
                "status": "Completed",
                "items": [{"qty": 1, "subtotal": 15000}],
                "total": 15000,
            },
            {
                "id": 3,
                "created_at": "2026-07-06T17:00:00",
                "status": "Ready",
                "items": [{"qty": 3, "subtotal": 30000}],
                "total": 30000,
            },
        ]

        summary = summarize_orders_for_day(orders, "2026-07-06")

        self.assertEqual(summary["order_count"], 2)
        self.assertEqual(summary["item_count"], 6)
        self.assertEqual(summary["revenue"], 70000)


if __name__ == "__main__":
    unittest.main()
