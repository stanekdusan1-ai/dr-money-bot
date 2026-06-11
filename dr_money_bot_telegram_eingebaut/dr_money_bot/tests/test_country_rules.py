from app.core.country_rules import detect_country_and_language


def test_country_detection():
    assert detect_country_and_language('hotels spanien')[0] == 'Spanien'
