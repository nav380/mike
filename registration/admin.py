from django.contrib import admin
from .models import registeredUser, accompayingPerson

@admin.register(registeredUser)
class RegisteredUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'designation', 'name_of_institution', 'email', 'phone_number')
    search_fields = ('username', 'email', 'name_of_institution')
    list_filter = ('country', 'meal_preference')
 
@admin.register(accompayingPerson)
class AccompanyingPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'registered_user', 'relation_to_delegate', 'meal_preference')
    search_fields = ('name', 'registered_user__username', 'relation_to_delegate')
    list_filter = ('meal_preference',)      
