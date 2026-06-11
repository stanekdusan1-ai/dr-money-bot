from app.core.classifier import classify_category
from app.core.models import Category


def test_hotel_classification():
    assert classify_category('suche hotels deutschland') == Category.hotels
