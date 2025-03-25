from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.utils.timezone import now


class Order(models.Model):
    STATUS_CHOICES = [
        ('cancelled', 'Cancelled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    offer_detail_id = models.ForeignKey('offers.OfferDetail', on_delete=models.CASCADE, verbose_name=_('Offer Detail'))
    customer_user = models.IntegerField(default=0)
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Business User"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title= models.CharField(max_length=255, null=True, blank=True)
    delivery_time_in_days = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    features = models.JSONField(null=True, blank=True)
    offer_type = models.CharField(max_length=50, blank=True)
    revisions = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.business_user_id and self.offer_detail_id:
            self.business_user = self.offer_detail_id.offer.user
        
        if not self.title and self.offer_detail_id:
            self.title = self.offer_detail_id.title
        if self.offer_detail_id:
            detail = self.offer_detail_id
            self.revisions = self.revisions or detail.revisions
            self.delivery_time_in_days = self.delivery_time_in_days or detail.delivery_time_in_days
            self.price = self.price or detail.price
            self.features = self.features or detail.features
            self.offer_type = self.offer_type or detail.offer_type
        super().save(*args, **kwargs)
    
    def update(self, *args, **kwargs):
        self.updated_at = now()
        super().save(*args, **kwargs)