from django.db import models

class registeredUser(models.Model):
    username = models.CharField(max_length=150)
    designation = models.CharField(max_length=100)
    name_of_institution = models.CharField(max_length=255)
    address=models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    IADVL_membership_number = models.CharField(max_length=50, blank=True, null=True)
    meal_preference = models.CharField(max_length=50)
    
    

    def __str__(self):
        return self.username
    
class accompayingPerson(models.Model):
    registered_user = models.ForeignKey(registeredUser, on_delete=models.CASCADE, related_name='accompanying_persons')
    name = models.CharField(max_length=150)
    gender=models.CharField(max_length=20)
    age = models.PositiveIntegerField()
    relation_to_delegate = models.CharField(max_length=100)
    meal_preference = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} (Accompanying {self.registered_user.username})"    
    