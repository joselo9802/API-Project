from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    itemprice = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('user','item')
    def __str__(self):
        return self.user

class OrderItem(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)

    class Meta:
        unique_together = ('customer', 'item')
    def __str__(self):
            return f"{self.customer} - {self.item} - {self.quantity}"


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer")
    deliver_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True)
    items = models.ManyToManyField(OrderItem)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, default=0)

    def __str__(self):
        return f"Order {self.id} by {self.customer}"



