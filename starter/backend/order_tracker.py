# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

VALID_STATUSES = ("pending", "processing", "shipped", "delivered", "cancelled")

class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    @staticmethod
    def _validate_order_id(order_id: str):
        if not isinstance(order_id, str) or not order_id.strip():
            raise ValueError("Order ID must be a non-empty string.")

    @staticmethod
    def _validate_status(status: str):
        if status not in VALID_STATUSES:
            raise ValueError("Status must be one of: pending, processing, shipped, delivered, cancelled.")

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        self._validate_order_id(order_id)
        if not isinstance(item_name, str) or not item_name.strip():
            raise ValueError("Item name must be a non-empty string.")
        if not isinstance(customer_id, str) or not customer_id.strip():
            raise ValueError("Customer ID must be a non-empty string.")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        self._validate_status(status)

        if self.storage.get_order(order_id) is not None:
            raise ValueError(f"Order with ID '{order_id}' already exists.")

        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status,
        }
        self.storage.save_order(order)

    def get_order_by_id(self, order_id: str):
        self._validate_order_id(order_id)
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        self._validate_status(new_status)
        self._validate_order_id(order_id)

        order = self.storage.get_order(order_id)
        if order is None:
            raise ValueError(f"Order with ID '{order_id}' not found.")

        updated_order = order.copy()
        updated_order["status"] = new_status
        self.storage.save_order(updated_order)
        return updated_order

    def list_all_orders(self):
        return list(self.storage.get_all_orders().values())

    def list_orders_by_status(self, status: str):
        self._validate_status(status)
        orders = self.storage.get_all_orders().values()
        return [order for order in orders if order.get("status") == status]
