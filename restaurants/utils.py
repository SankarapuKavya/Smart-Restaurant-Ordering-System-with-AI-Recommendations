# restaurants/utils.py
import hashlib
import hmac
import base64

# -------------------------
# Generate Checksum
# -------------------------
def generate_checksum(params: dict, merchant_key: str) -> str:
    """
    Generate checksum hash for Paytm parameters
    """
    keys = sorted(params.keys())
    data = "|".join(str(params[k]) for k in keys)
    return base64.b64encode(hmac.new(merchant_key.encode(), data.encode(), hashlib.sha256).digest()).decode()


# -------------------------
# Verify Checksum
# -------------------------
def verify_checksum(params: dict, merchant_key: str, checksum: str) -> bool:
    """
    Verify checksum hash received from Paytm
    """
    generated_checksum = generate_checksum(params, merchant_key)
    return generated_checksum == checksum