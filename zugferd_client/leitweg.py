"""
Leitweg-ID Validierung & Berechnung nach DIN EN 16931-1 & ISO/IEC 7064 MOD 97-10.
"""

from typing import Dict, Any

LEITWEG_REGIONS: Dict[str, str] = {
    "01": "Schleswig-Holstein",
    "02": "Freie und Hansestadt Hamburg",
    "03": "Niedersachsen",
    "04": "Freie Hansestadt Bremen",
    "05": "Nordrhein-Westfalen",
    "06": "Hessen",
    "07": "Rheinland-Pfalz",
    "08": "Baden-Württemberg",
    "09": "Freistaat Bayern",
    "10": "Saarland",
    "11": "Berlin",
    "12": "Brandenburg",
    "13": "Mecklenburg-Vorpommern",
    "14": "Freistaat Sachsen",
    "15": "Sachsen-Anhalt",
    "16": "Freistaat Thüringen",
    "99": "Bund / Bundesverwaltung",
}


def _calc_check_digit(base_clean: str) -> str:
    num_str = ""
    for char in base_clean.upper():
        if "0" <= char <= "9":
            num_str += char
        elif "A" <= char <= "Z":
            num_str += str(ord(char) - 65 + 10)
    if not num_str:
        return "00"
    remainder = int(num_str + "00") % 97
    check = (98 - remainder) % 97
    return f"{check:02d}"


def calculate_leitweg_id(raw_id: str) -> Dict[str, Any]:
    """
    Validiert eine bestehende Leitweg-ID oder berechnet die 2-stellige Prüfziffer
    nach ISO/IEC 7064 MOD 97-10.
    """
    trimmed = raw_id.strip()
    parts = trimmed.split("-")
    clean = "".join(c for c in trimmed if c.isalnum()).upper()

    if len(clean) < 4:
        return {
            "is_valid": False,
            "region": "Unbekannt",
            "grob": trimmed,
            "fein": "-",
            "check": "",
            "message": "Zu kurz (mindestens 4 Zeichen erforderlich)",
        }

    region_code = clean[:2]
    region_name = LEITWEG_REGIONS.get(region_code, f"Sonstige Körperschaft ({region_code})")

    grob = ""
    fein = ""
    check_digit = ""
    is_full = False

    if len(parts) >= 3:
        grob = parts[0]
        fein = "-".join(parts[1:-1])
        check_digit = parts[-1]
        is_full = len(check_digit) == 2 and check_digit.isdigit()
    elif len(parts) == 2:
        grob = parts[0]
        if len(parts[1]) == 2 and parts[1].isdigit():
            check_digit = parts[1]
            is_full = True
        else:
            fein = parts[1]
    else:
        grob = trimmed

    if is_full:
        num_str = ""
        for char in clean:
            if "0" <= char <= "9":
                num_str += char
            elif "A" <= char <= "Z":
                num_str += str(ord(char) - 65 + 10)
        is_valid = int(num_str) % 97 == 1 if num_str else False
        base_for_calc = clean[:-2]
        expected_check = _calc_check_digit(base_for_calc)

        return {
            "is_valid": is_valid,
            "region": f"{region_name} ({region_code})",
            "grob": grob,
            "fein": fein or "-",
            "check": check_digit,
            "expected_check": expected_check,
            "message": "Gültige Leitweg-ID nach DIN EN 16931-1 & KoSIT"
            if is_valid
            else f"Ungültige Prüfziffer! Erwartet: {expected_check}, Gefunden: {check_digit}",
        }
    else:
        calculated = _calc_check_digit(clean)
        return {
            "is_valid": True,
            "region": f"{region_name} ({region_code})",
            "grob": grob,
            "fein": fein or "-",
            "check": calculated,
            "expected_check": calculated,
            "message": f"Prüfziffer {calculated} erfolgreich nach ISO 7064 MOD 97-10 berechnet",
        }
