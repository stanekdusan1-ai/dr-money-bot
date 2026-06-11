COUNTRY_ALIASES = {
    'deutschland': ('Deutschland', 'de'), 'germany': ('Deutschland', 'de'),
    'schweiz': ('Schweiz', 'de'), 'switzerland': ('Schweiz', 'de'),
    'österreich': ('Österreich', 'de'), 'oesterreich': ('Österreich', 'de'), 'austria': ('Österreich', 'de'),
    'spanien': ('Spanien', 'es'), 'spain': ('Spanien', 'es'), 'españa': ('Spanien', 'es'),
    'italien': ('Italien', 'it'), 'italy': ('Italien', 'it'),
    'frankreich': ('Frankreich', 'fr'), 'france': ('Frankreich', 'fr'),
    'niederlande': ('Niederlande', 'nl'), 'netherlands': ('Niederlande', 'nl'),
    'weltweit': ('Weltweit', 'de'), 'global': ('Weltweit', 'de'),
}


def detect_country_and_language(text: str) -> tuple[str, str]:
    lower = text.lower()
    for key, value in COUNTRY_ALIASES.items():
        if key in lower:
            return value
    return 'unbekannt', 'de'
