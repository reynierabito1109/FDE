import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

# --- add_order tests ---

def test_add_order_saves_order_with_default_pending_status(order_tracker, mock_storage):
    order_tracker.add_order("ORD001", "Laptop", 2, "CUST001")

    mock_storage.save_order.assert_called_once_with({
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 2,
        "customer_id": "CUST001",
        "status": "pending",
    })

def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

def test_add_order_with_explicit_status(order_tracker, mock_storage):
    order_tracker.add_order("ORD002", "Phone", 1, "CUST002", status="shipped")

    mock_storage.save_order.assert_called_once_with({
        "order_id": "ORD002",
        "item_name": "Phone",
        "quantity": 1,
        "customer_id": "CUST002",
        "status": "shipped",
    })

def test_add_order_raises_error_for_invalid_quantity(order_tracker):
    with pytest.raises(ValueError, match="Quantity must be a positive integer."):
        order_tracker.add_order("ORD003", "Tablet", 0, "CUST003")

def test_add_order_raises_error_for_negative_quantity(order_tracker):
    with pytest.raises(ValueError, match="Quantity must be a positive integer."):
        order_tracker.add_order("ORD004", "Tablet", -1, "CUST004")

def test_add_order_raises_error_for_empty_order_id(order_tracker):
    with pytest.raises(ValueError, match="Order ID must be a non-empty string."):
        order_tracker.add_order("", "Tablet", 1, "CUST005")

def test_add_order_raises_error_for_empty_item_name(order_tracker):
    with pytest.raises(ValueError, match="Item name must be a non-empty string."):
        order_tracker.add_order("ORD005", "", 1, "CUST006")

def test_add_order_raises_error_for_empty_customer_id(order_tracker):
    with pytest.raises(ValueError, match="Customer ID must be a non-empty string."):
        order_tracker.add_order("ORD006", "Tablet", 1, "")

def test_add_order_raises_error_for_invalid_status(order_tracker):
    with pytest.raises(ValueError, match="Status must be one of: pending, processing, shipped, delivered, cancelled."):
        order_tracker.add_order("ORD007", "Tablet", 1, "CUST007", status="unknown")

def test_get_order_by_id_returns_existing_order(order_tracker, mock_storage):
    order = {
        "order_id": "ORD008",
        "item_name": "Monitor",
        "quantity": 1,
        "customer_id": "CUST008",
        "status": "pending",
    }
    mock_storage.get_order.return_value = order

    result = order_tracker.get_order_by_id("ORD008")

    assert result == order
    mock_storage.get_order.assert_called_once_with("ORD008")

def test_get_order_by_id_returns_none_if_not_found(order_tracker, mock_storage):
    mock_storage.get_order.return_value = None

    assert order_tracker.get_order_by_id("ORD009") is None

def test_get_order_by_id_raises_error_for_empty_id(order_tracker, mock_storage):
    with pytest.raises(ValueError, match="Order ID must be a non-empty string."):
        order_tracker.get_order_by_id("")

    mock_storage.get_order.assert_not_called()

def test_update_order_status_successfully(order_tracker, mock_storage):
    original_order = {
        "order_id": "ORD010",
        "item_name": "Keyboard",
        "quantity": 1,
        "customer_id": "CUST010",
        "status": "pending",
    }
    mock_storage.get_order.return_value = original_order

    order_tracker.update_order_status("ORD010", "shipped")

    assert original_order["status"] == "pending"
    mock_storage.save_order.assert_called_once_with({
        "order_id": "ORD010",
        "item_name": "Keyboard",
        "quantity": 1,
        "customer_id": "CUST010",
        "status": "shipped",
    })

def test_update_order_status_raises_error_for_invalid_status(order_tracker, mock_storage):
    with pytest.raises(ValueError, match="Status must be one of: pending, processing, shipped, delivered, cancelled."):
        order_tracker.update_order_status("ORD011", "unknown")

    mock_storage.get_order.assert_not_called()

def test_update_order_status_raises_error_if_order_not_found(order_tracker, mock_storage):
    mock_storage.get_order.return_value = None

    with pytest.raises(ValueError, match="Order with ID 'ORD012' not found."):
        order_tracker.update_order_status("ORD012", "shipped")

    mock_storage.save_order.assert_not_called()

def test_update_order_status_raises_error_for_empty_id(order_tracker, mock_storage):
    with pytest.raises(ValueError, match="Order ID must be a non-empty string."):
        order_tracker.update_order_status("", "shipped")

    mock_storage.get_order.assert_not_called()

def test_list_all_orders_returns_empty_list_when_no_orders(order_tracker, mock_storage):
    mock_storage.get_all_orders.return_value = {}

    assert order_tracker.list_all_orders() == []

def test_list_all_orders_returns_all_orders(order_tracker, mock_storage):
    orders = {
        "ORD013": {"order_id": "ORD013", "status": "pending"},
        "ORD014": {"order_id": "ORD014", "status": "shipped"},
    }
    mock_storage.get_all_orders.return_value = orders

    result = order_tracker.list_all_orders()

    assert {order["order_id"] for order in result} == {"ORD013", "ORD014"}
    assert all(isinstance(order, dict) for order in result)

def test_list_orders_by_status_returns_matching_orders(order_tracker, mock_storage):
    mock_storage.get_all_orders.return_value = {
        "ORD015": {"order_id": "ORD015", "status": "pending"},
        "ORD016": {"order_id": "ORD016", "status": "shipped"},
        "ORD017": {"order_id": "ORD017", "status": "pending"},
    }

    result = order_tracker.list_orders_by_status("pending")

    assert {order["order_id"] for order in result} == {"ORD015", "ORD017"}

def test_list_orders_by_status_returns_empty_list_when_none_match(order_tracker, mock_storage):
    mock_storage.get_all_orders.return_value = {
        "ORD018": {"order_id": "ORD018", "status": "pending"},
    }

    assert order_tracker.list_orders_by_status("shipped") == []

def test_list_orders_by_status_returns_empty_list_when_storage_empty(order_tracker, mock_storage):
    mock_storage.get_all_orders.return_value = {}

    assert order_tracker.list_orders_by_status("pending") == []

def test_list_orders_by_status_raises_error_for_empty_status(order_tracker, mock_storage):
    with pytest.raises(ValueError, match="Status must be one of: pending, processing, shipped, delivered, cancelled."):
        order_tracker.list_orders_by_status("")

    mock_storage.get_all_orders.assert_not_called()

def test_list_orders_by_status_raises_error_for_invalid_status(order_tracker, mock_storage):
    with pytest.raises(ValueError, match="Status must be one of: pending, processing, shipped, delivered, cancelled."):
        order_tracker.list_orders_by_status("unknown")

    mock_storage.get_all_orders.assert_not_called()

#
# --- TODO: add test functions below this line ---
#
