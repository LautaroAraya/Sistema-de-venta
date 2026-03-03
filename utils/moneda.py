import re


def parsear_monto(valor):
    if valor is None:
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip()
    if not texto:
        return 0.0

    texto = texto.replace('$', '').replace(' ', '')

    if '.' in texto and ',' in texto:
        if texto.rfind(',') > texto.rfind('.'):
            texto = texto.replace('.', '').replace(',', '.')
        else:
            texto = texto.replace(',', '')
    elif ',' in texto:
        texto = texto.replace(',', '.')
    elif '.' in texto and re.match(r'^\d{1,3}(\.\d{3})+$', texto):
        texto = texto.replace('.', '')

    return float(texto)


def formatear_moneda(valor):
    try:
        monto = int(round(float(valor or 0)))
    except (TypeError, ValueError):
        monto = 0

    signo = '-' if monto < 0 else ''
    return f"{signo}${abs(monto):,}".replace(',', '.')


def formatear_moneda_con_signo(valor):
    try:
        monto = int(round(float(valor or 0)))
    except (TypeError, ValueError):
        monto = 0

    signo = '+' if monto >= 0 else '-'
    return f"{signo}${abs(monto):,}".replace(',', '.')
