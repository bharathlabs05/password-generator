"""Terminal version."""

from generator import (MIN_LENGTH, MAX_LENGTH, RECOMMENDED,
                       generate_password, calculate_entropy, rate_entropy)


def get_length():
    while True:
        raw = input(f"Enter password length ({MIN_LENGTH}-{MAX_LENGTH}, {RECOMMENDED}+ recommended): ").strip()
        try:
            length = int(raw)
        except ValueError:
            print("  [!] Please enter a whole number.")
            continue
        if length < MIN_LENGTH:
            print(f"  [!] Too short. Minimum is {MIN_LENGTH}.")
        elif length > MAX_LENGTH:
            print(f"  [!] Too long. Maximum is {MAX_LENGTH}.")
        else:
            if length < RECOMMENDED:
                print(f"  [i] Below the NIST recommended {RECOMMENDED} characters.")
            return length


def ask_yes_no(question, default=True):
    hint = "Y/n" if default else "y/N"
    while True:
        ans = input(f"{question} [{hint}]: ").strip().lower()
        if ans == "":
            return default
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("  [!] Please answer y or n.")


def run_cli():
    print("=" * 50)
    print("  DecodeLabs - Secure Password Generator")
    print("=" * 50)

    length = get_length()
    symbols = ask_yes_no("Include special characters (@, #, $ ...)?", True)

    while True:
        pwd, pool = generate_password(length, use_symbols=symbols)
        bits = calculate_entropy(length, pool)
        label, _ = rate_entropy(bits)

        print("\n" + "-" * 50)
        print(f"Password : {pwd}")
        print(f"Length   : {length}")
        print(f"Pool size: {pool}")
        print(f"Entropy  : {bits:.1f} bits ({label})")
        print("-" * 50)

        if not ask_yes_no("Generate another?", False):
            break