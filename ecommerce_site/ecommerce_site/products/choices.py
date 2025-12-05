from django.db import models


class SizeChoices(models.TextChoices):
    XS = "XS", "Extra Small"
    S = "S", "Small"
    M = "M", "Medium"
    L = "L", "Large"
    XL = "XL", "Extra Large"


class RatingChoices(models.IntegerChoices):
    ONE = 1, "⭐"
    TWO = 2, "⭐⭐"
    THREE = 3, "⭐⭐⭐"
    FOUR = 4, "⭐⭐⭐⭐"
    FIVE = 5, "⭐⭐⭐⭐⭐"

DEFAULT_RATING_CHOICE = RatingChoices.ONE
