from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from users.managers import CustomUserManager
from django.db.models.signals import post_save
import random

# Custom User model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email', unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    unique_id = models.CharField(max_length=50, unique=True, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def generate_unique_id(self):
        """Generate a unique ID in the format: vgs-ss-FL-XXXXXXXXXX"""
        company_name = "VGS"
        product_name = "SS"
        first_initial = self.first_name[0].upper() if self.first_name else 'X'
        last_initial = self.last_name[0].upper() if self.last_name else 'X'
        random_number = random.randint(1000000000, 9999999999)
        unique_id = f"{company_name}-{product_name}-{first_initial}{last_initial}-{random_number}"

        # Ensure uniqueness by checking if the generated ID already exists
        while CustomUser.objects.filter(unique_id=unique_id).exists():
            random_number = random.randint(1000000000, 9999999999)
            unique_id = f"{company_name}-{product_name}-{first_initial}{last_initial}-{random_number}"

        return unique_id

    def save(self, *args, **kwargs):
        """Ensure unique_id is generated before saving"""
        if not self.unique_id:
            self.unique_id = self.generate_unique_id()
        super().save(*args, **kwargs)


# Profile model for the user details
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/products', null=True, blank=True, default='default/pic.png')
    date_modified = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    old_cart = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = 'User Profile'


# Shipping Address model
class ShippingAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Shipping Addresses"  # Adjusted the plural form

    def __str__(self):
        return f'Shipping Address - {str(self.id)}'


# Signal to create or update Profile whenever a CustomUser is created or updated
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Automatically create or update the user profile when a new CustomUser is created."""
    if created:
        # Create profile if it doesn't exist
        Profile.objects.create(user=instance)
    else:
        # Update profile if it already exists
        instance.profile.save()

post_save.connect(create_or_update_user_profile, sender=CustomUser)
