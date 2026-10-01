from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/orders', methods=['POST'])
def add_order_api():
    data = request.get_json(silent=True) or {}
    try:
        order_tracker.add_order(
            data['order_id'],
            data['item_name'],
            data['quantity'],
            data['customer_id'],
            data.get('status', 'pending'),
        )
        order = order_tracker.get_order_by_id(data['order_id'])
        return jsonify(order), 201
    except KeyError as error:
        return jsonify({"error": f"Missing required field: {error.args[0]}"}), 400
    except ValueError as error:
        status_code = 409 if "already exists" in str(error) else 400
        return jsonify({"error": str(error)}), status_code

@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    try:
        order = order_tracker.get_order_by_id(order_id)
        if order is None:
            return jsonify({"error": f"Order with ID '{order_id}' not found."}), 404
        return jsonify(order), 200
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    data = request.get_json(silent=True) or {}
    try:
        new_status = data['new_status']
        order = order_tracker.update_order_status(order_id, new_status)
        return jsonify(order), 200
    except KeyError as error:
        return jsonify({"error": f"Missing required field: {error.args[0]}"}), 400
    except ValueError as error:
        status_code = 404 if "not found" in str(error) else 400
        return jsonify({"error": str(error)}), status_code

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    try:
        status = request.args.get('status')
        if status is None:
            orders = order_tracker.list_all_orders()
        else:
            orders = order_tracker.list_orders_by_status(status)
        return jsonify(orders), 200
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
