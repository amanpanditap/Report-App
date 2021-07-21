from django.db import models
from django.db.models.fields import CharField, FloatField
from django.db.models.fields.files import ImageField

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to ='products', default = 'no_picture.png')
    price = models.FloatField(help_text='In Indian Rupees ₹')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}-{self.created.strftime('%d/%m/%Y')}"