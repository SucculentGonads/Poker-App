from django.db import models

class Chips(models.Model):  # Class names should be capitalized by convention
    Title = models.CharField(max_length=120)
    Amount = models.DecimalField(max_digits=10, decimal_places=0)
    Price = models.DecimalField(max_digits=10, decimal_places=0)
