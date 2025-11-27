from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class RegisteredUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class registeredUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=100, blank=True, null=True)
    name_of_institution = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    IADVL_membership_number = models.CharField(max_length=50, blank=True, null=True)
    meal_preference = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    master_class = models.BooleanField(default=False)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    food_allergies = models.TextField(blank=True, null=True)
    final_total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = RegisteredUserManager()

    USERNAME_FIELD = "email"      # login by email
    REQUIRED_FIELDS = ["name"]    # required when creating superuser

    def __str__(self):
        return self.email

class accompayingPerson(models.Model):
    registered_user = models.ForeignKey(
        registeredUser, on_delete=models.CASCADE, related_name='accompanying_persons'
    )
    name = models.CharField(max_length=150)
    gender = models.CharField(max_length=20, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    relation_to_delegate = models.CharField(max_length=100, blank=True, null=True)
    meal_preference = models.CharField(max_length=50, blank=True, null=True)

    # New fields for event access and extras
    join_event = models.BooleanField(default=False)
    lunch = models.CharField(max_length=20, default="none")  # '27', '28', 'both', or 'none'
    extra_gala = models.BooleanField(default=False)
    extra_cruise = models.BooleanField(default=False)
    extra_darshan = models.BooleanField(default=False)
    created_at=models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):
        return f"{self.name} (Accompanying {self.registered_user.username})"
    
    

class OTP(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True) 
    created_at=models.DateField(auto_now_add=True) 
    
from django.db import models

class Regno(models.Model):
    user = models.ForeignKey(
        'registeredUser',  # replace with your user model
        on_delete=models.CASCADE,
        related_name='regno'
    )
    reg_no = models.CharField(max_length=10, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reg_no:
            last = Regno.objects.order_by('id').last()
            if last:
                # extract the numeric part and increment
                last_number = int(last.reg_no.replace('RAG', ''))
                new_number = last_number + 1
            else:
                new_number = 1
            self.reg_no = f"RAG{new_number:03d}"  # RAG001, RAG002, etc.
        super().save(*args, **kwargs)

    def __str__(self):
        return self.reg_no
