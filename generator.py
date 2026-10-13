"""Core engine: secrets + string modules, .join(), entropy."""

import math
import secrets
import string

MIN_LENGTH = 8
RECOMMENDED = 15   # NIST SP 800-63-4 high-security minimum
MAX_LENGTH = 64


def generate_password(length, use_lower=True, use_upper=True,
                      use_digits=True, use_symbols=True):
    """Return (password, pool_size). Guarantees one char from each selected pool."""
    pools = []
    if use_lower:
        pools.append(string.ascii_lowercase)
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_digits:
        pools.append(string.digits)
    if use_symbols:
        pools.append(string.punctuation)

    if not pools:
        raise ValueError("Select at least one character type.")
    if not MIN_LENGTH <= length <= MAX_LENGTH:
        raise ValueError(f"Length must be between {MIN_LENGTH} and {MAX_LENGTH}.")

    alphabet = "".join(pools)

    chars = [secrets.choice(p) for p in pools]
    chars += [secrets.choice(alphabet) for _ in range(length - len(chars))]
    secrets.SystemRandom().shuffle(chars)

    return "".join(chars), len(alphabet)


def calculate_entropy(length, pool_size):
    """E = L * log2(R) in bits."""
    return length * math.log2(pool_size)


def rate_entropy(bits):
    """Return (label, color)."""
    if bits < 50:
        return "WEAK", "#d9534f"
    if bits < 70:
        return "MODERATE", "#f0ad4e"
    if bits < 90:
        return "STRONG", "#5cb85c"
    return "VERY STRONG", "#2e8b57"