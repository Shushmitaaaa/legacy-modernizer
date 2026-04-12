#task_coverage.py
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
    },
    {
        "id": "coverage_002",
        "description": "String processing utilities with zero tests",
        "code": '''
def reverse_words(sentence):
    if not sentence or not isinstance(sentence, str):
        raise ValueError("Input must be a non-empty string")
    return " ".join(sentence.strip().split()[::-1])

def count_vowels(text):
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    return sum(1 for ch in text.lower() if ch in "aeiou")

def truncate_text(text, max_length, suffix="..."):
    if max_length < 0:
        raise ValueError("max_length must be non-negative")
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def is_palindrome(text):
    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    return cleaned == cleaned[::-1]

def capitalize_words(sentence):
    if not sentence:
        return ""
    return " ".join(word.capitalize() for word in sentence.split())
'''
    },
    {
        "id": "coverage_003",
        "description": "Data validation utilities with zero tests",
        "code": '''
def validate_email(email):
    import re
    if not email or not isinstance(email, str):
        raise ValueError("Email must be a non-empty string")
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def validate_phone(phone):
    import re
    cleaned = re.sub(r"[\\s\\-\\(\\)]", "", phone)
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15

def clamp(value, min_val, max_val):
    if min_val > max_val:
        raise ValueError("min_val cannot exceed max_val")
    return max(min_val, min(value, max_val))

def safe_divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

def flatten_list(nested):
    if not isinstance(nested, list):
        raise TypeError("Input must be a list")
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result
'''
    }
]