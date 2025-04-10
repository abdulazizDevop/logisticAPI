from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Telefon raqami kiritilishi shart!")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(
        max_length=13,
        unique=True,
        validators=[RegexValidator(regex=r'^\+998\d{9}$', message="Telefon raqami +998 bilan boshlanishi kerak")]
    )
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name', 'email']

    def __str__(self):
        return self.phone_number
    

# Boshqa modellar (DriverProfile, Cargo, CargoReview)
class DriverProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    vehicle_type = models.CharField(max_length=50, blank=True)
    license_type = models.CharField(max_length=50, blank=True)
    vehicle_capacity = models.FloatField(null=True, blank=True)
    experience = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.name} profili"

class Cargo(models.Model):
    VEHICLE_TYPES = (
        ('Bortli', 'Bortli'),
        ('Tentli', 'Tentli'),
        ('Refrigatorli', 'Refrigatorli'),
        ('Samosval', 'Samosval'),
        ('Shalanda', 'Shalanda'),
        ('Konteyner', 'Konteyner'),
        ('Ploshadka', 'Ploshadka'),
    )
    STATUS_CHOICES = (
        ('Jarayonda', 'Jarayonda'),
        ('Yolda', 'Yolda'),
        ('Yetkazib berilgan', 'Yetkazib berilgan'),
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_cargos')
    driver = models.ForeignKey(DriverProfile, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, default="Noma'lum")
    weight = models.FloatField()
    origin = models.CharField(max_length=100, default="Noma'lum")
    destination = models.CharField(max_length=100, default="Noma'lum")
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default='Bortli')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Jarayonda')
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class CargoReview(models.Model):
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    choose = {
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    }
    stars = models.IntegerField(choices=choose, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} sharhi"
    

# models.py ga qo'shilishi kerak
class ContactMessage(models.Model):
    STATUS_CHOICES = (
        ('Yangi', 'Yangi'),
        ('O\'qilgan', 'O\'qilgan'),
        ('Javob berilgan', 'Javob berilgan'),
    )
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Yangi')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class Advertisement(models.Model):
    STATUS_CHOICES = (
        ('Korib chiqilmoqda', 'Korib chiqilmoqda'),
        ('Tasdiqlangan', 'Tasdiqlangan'),
        ('Rad etilgan', 'Rad etilgan'),
    )
    TYPE_CHOICES = (
        ('Native', 'Native Reklama'),
        ('Boost', 'Boost Reklama'),
        ('SuperTop', 'Super Top Reklama'),
        ('Splash', 'Splash Reklama'),
        ('INterstitial', 'INterstitial Reklama'),
        ('TOP', 'TOP E\'lon'),
        ('E\'lonni ko\'tarish', 'E\'lonni yuqoriga ko\'tarish'),
        ('Maxsus', 'Maxsus Reklama'),
    )
    DURATION_CHOICES = (
        (1, '1 kun'),
        (3, '3 kun'),
        (7, '1 hafta'),
        (14, '2 hafta'),
        (30, '1 oy'),
    )
    
    company_name = models.CharField(max_length=200)
    ad_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Banner')
    duration_days = models.IntegerField(choices=DURATION_CHOICES, default=1)
    phone_number = models.CharField(max_length=20)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Korib chiqilmoqda')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Admin tomonidan to'ldiriladi
    media_file = models.FileField(upload_to='advertisements/', null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.company_name} - {self.ad_type}"