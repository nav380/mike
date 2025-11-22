from django.shortcuts import render, redirect
from django.contrib import messages
from .models import registeredUser, accompayingPerson


def register_user(request):
    user_id = request.session.get("user_id")
    user = None

    # If logged in, fetch existing user
    if user_id:
        try:
            user = registeredUser.objects.get(id=user_id)
        except registeredUser.DoesNotExist:
            user = None

    if request.method == "POST":
        # If user exists → Update
        if user:
            pass  # No need to create new user
        else:
            # Create new user → Allow registration without login
            user = registeredUser()
            if registeredUser.objects.filter(email=request.POST.get("email")).exists():
                messages.error(request, "Email already registered. Please login.")
                return redirect("login")

        user.username = request.POST.get("username")
        user.designation = request.POST.get("designation")
        user.name_of_institution = request.POST.get("name_of_institution")
        user.address = request.POST.get("address")
        user.city = request.POST.get("city")
        user.state = request.POST.get("state")
        user.country = request.POST.get("country")
        user.pincode = request.POST.get("pincode")
        user.phone_number = request.POST.get("phone_number")
        user.email = request.POST.get("email")
        user.IADVL_membership_number = request.POST.get("IADVL_membership_number")
        user.meal_preference = request.POST.get("meal_preference")
    
        user.save()

        # Save id in session (auto login after registration)
        request.session["user_id"] = user.id

        # Remove old accompanying persons if updating
        accompayingPerson.objects.filter(registered_user=user).delete()

        names = request.POST.getlist("ac_name[]")
        genders = request.POST.getlist("ac_gender[]")
        ages = request.POST.getlist("ac_age[]")
        relations = request.POST.getlist("ac_relation[]")
        meals = request.POST.getlist("ac_meal[]")

        for i in range(len(names)):
            if names[i].strip():
                accompayingPerson.objects.create(
                    registered_user=user,
                    name=names[i],
                    gender=genders[i],
                    age=ages[i],
                    relation_to_delegate=relations[i],
                    meal_preference=meals[i]
                )

        messages.success(request, "Registration updated! Continue to Payment")
        return redirect("register_user")  # Blogin/etter redirect

    accomp_list = accompayingPerson.objects.filter(registered_user=user) if user else []

    return render(request, "register_form.html", {
        "user": user,
        "accompanying": accomp_list
    })

def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = registeredUser.objects.get(email=email)
            request.session["user_id"] = user.id  # Store session
            request.session["username"] = user.username
            
            messages.success(request, "Login Successful!")
            return redirect("register_user")
        
        except registeredUser.DoesNotExist:
            messages.error(request, "Invalid email. Please try again.")
            return redirect("login")

    return render(request, "login.html")


def logout_user(request):
    request.session.flush()  # Clear session
    messages.success(request, "Logged out successfully.")
    return redirect("login")
