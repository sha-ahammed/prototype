from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class HsnCode(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    description = models.TextField(max_length=1500, blank=True, null=True)
    gst_percent = models.FloatField(validators=[MaxValueValidator(100), MinValueValidator(0)], blank=True, null=True)


class BillingProduct(models.Model):
    title = models.CharField(max_length=255)
    product_hsn = models.ForeignKey(HsnCode, on_delete=models.SET_NULL, blank=True, null=True)
    code = models.CharField(max_length=8)
    price = models.FloatField()
    stock = models.IntegerField()
    discount = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    price2 = models.FloatField(default=0)
    price3 = models.FloatField(default=0)
    gst_percent = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
