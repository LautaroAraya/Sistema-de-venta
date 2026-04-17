"""
Genera un hash de password para usar en TECNICO_PASS_HASH.
Uso:
    python tecnico_generar_hash.py
"""

from getpass import getpass
from werkzeug.security import generate_password_hash


def main():
    password = getpass("Ingresa la password del tecnico: ").strip()
    if not password:
        print("Error: password vacia")
        return

    confirm = getpass("Repite la password: ").strip()
    if password != confirm:
        print("Error: las passwords no coinciden")
        return

    print("\nTECNICO_PASS_HASH=")
    print(generate_password_hash(password))


if __name__ == "__main__":
    main()
