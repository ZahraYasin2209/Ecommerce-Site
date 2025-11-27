from django.db import models


class RatingChoices(models.IntegerChoices):
    ONE = 1, "1 Star"
    TWO = 2, "2 Stars"
    THREE = 3, "3 Stars"
    FOUR = 4, "4 Stars"
    FIVE = 5, "5 Stars"


class SizeChoices(models.TextChoices):
    XS = "XS", "Extra Small"
    S = "S", "Small"
    M = "M", "Medium"
    L = "L", "Large"
    XL = "XL", "Extra Large"
