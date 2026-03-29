LEGACY_CODE_SAMPLES = [
    {
        "id": "coverage_001",
        "description": "E-commerce utility functions with zero tests",
        "code": '''
def calculate_discount(price, discount_percent):
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    return round(price * (1 - discount_percent / 100), 2)

def apply_tax(price, tax_rate):
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")
    return round(price * (1 + tax_rate / 100), 2)

def calculate_shipping(weight_kg, distance_km, express=False):
    base_rate = 0.05
    cost = weight_kg * distance_km * base_rate
    if express:
        cost *= 1.5
    return round(cost, 2)

def validate_coupon(coupon_code, valid_coupons):
    if not coupon_code or not isinstance(coupon_code, str):
        return False
    return coupon_code.strip().upper() in [c.upper() for c in valid_coupons]

def parse_address(address_string):
    parts = [p.strip() for p in address_string.split(",")]
    if len(parts) != 3:
        raise ValueError("Invalid address format. Expected: Street, City, State ZIP")
    street = parts[0]
    city = parts[1]
    state_zip = parts[2].split()
    if len(state_zip) != 2:
        raise ValueError("Invalid State ZIP format")
    return {"street": street, "city": city, "state": state_zip[0], "zip": state_zip[1]}
'''
    }
]