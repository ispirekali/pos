from django.db import models
from django.utils import timezone
from datetime import datetime
from customers.models import Customer
from products.models import Product



class Sale(models.Model):
    date = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sub_total = models.FloatField(default=0)
    grand_total = models.FloatField(default=0)
    tax_amount = models.FloatField(default=0)
    tax_percentage = models.FloatField(default=0)
    amount_payed = models.FloatField(default=0)
    amount_change = models.FloatField(default=0)
    profit = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    


    class Meta:
        db_table = 'Sales'


    def __str__(self):
        return f"Sale ID: {self.id} | Grand Total: {self.grand_total} | Date: {self.date_added}"


    def update_totals(self):
        details = self.saledetail_set.all()
        self.sub_total = details.aggregate(total=models.Sum(models.F('total_detail')))['total']
        self.grand_total = self.sub_total + self.tax_amount
        self.profit = details.aggregate(total=models.Sum(models.F('profit')))['total']
        self.save()


class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.IntegerField()
    total_detail = models.FloatField()
    buying_price = models.FloatField(null=True)  # Nullable field
    profit = models.FloatField(default=0)  # Set default value


    class Meta:
        db_table = 'SaleDetails'


    
    def save(self, *args, **kwargs):
        self.total_detail = self.price * self.quantity
        self.profit = self.total_detail - (self.buying_price * self.quantity)
        super().save(*args, **kwargs)
        self.sale.update_totals()


    def __str__(self):
        return f"Detail ID: {self.id} | Sale ID: {self.sale.id} | Quantity: {self.quantity}"

