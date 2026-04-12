#task_refactor.py
LEGACY_CODE_SAMPLES = [
    {
        "id": "refactor_001",
        "description": "Monolithic order processing god function",
        "code": '''
import re
from datetime import datetime

def process_order(order_data, db_connection, email_client, inventory_system, logger):
    if not order_data:
        return {"success": False, "error": "Empty order"}

    required_fields = ["customer_id", "items", "shipping_address", "payment_info"]
    for field in required_fields:
        if field not in order_data:
            return {"success": False, "error": f"Missing: {field}"}

    email = order_data.get("customer_email", "")
    if not re.match(r"[^@]+@[^@]+\\.[^@]+", email):
        return {"success": False, "error": "Invalid email"}

    items = order_data["items"]
    for item in items:
        available = inventory_system.get_stock(item["product_id"])
        if available < item["quantity"]:
            return {"success": False, "error": f"Out of stock: {item[\'product_id\']}"}

    subtotal = 0
    for item in items:
        price = inventory_system.get_price(item["product_id"])
        subtotal += price * item["quantity"]

    discount = 0
    if order_data.get("coupon_code"):
        coupon = db_connection.query(
            "SELECT discount FROM coupons WHERE code = ?",
            [order_data["coupon_code"]]
        )
        if coupon:
            discount = coupon[0]["discount"]

    tax_rate = 0.08
    subtotal_after_discount = subtotal * (1 - discount / 100)
    tax = subtotal_after_discount * tax_rate
    total = subtotal_after_discount + tax

    address = order_data["shipping_address"]
    if address.get("country") != "US":
        shipping_cost = 25.0
    elif address.get("state") in ["AK", "HI"]:
        shipping_cost = 15.0
    else:
        shipping_cost = 5.99 if total < 50 else 0
    total += shipping_cost

    payment = order_data["payment_info"]
    if payment["type"] == "credit_card":
        card_number = payment["card_number"].replace(" ", "")
        if len(card_number) != 16:
            return {"success": False, "error": "Invalid card"}

    order_id = f"ORD-{datetime.now().strftime(\'%Y%m%d%H%M%S\')}"
    db_connection.execute(
        "INSERT INTO orders (id, customer_id, total, status) VALUES (?, ?, ?, ?)",
        [order_id, order_data["customer_id"], total, "confirmed"]
    )

    for item in items:
        inventory_system.decrement_stock(item["product_id"], item["quantity"])

    email_client.send(
        to=email,
        subject=f"Order Confirmed: {order_id}",
        body=f"Your order {order_id} total is ${total:.2f}"
    )

    return {"success": True, "order_id": order_id, "total": total,
            "subtotal": subtotal, "discount": discount, "tax": tax, "shipping": shipping_cost}
'''
    }
]