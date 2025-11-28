from django.shortcuts import render, redirect
from django.contrib import messages
from .models import registeredUser, accompayingPerson,Regno
from payment.models import Transaction


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import registeredUser, accompayingPerson ,OTP
from django.contrib.auth import login,logout
from django.core.mail import send_mail
import random



# Fees configuration
DELEGATE_FEES = {
    'VAI Members': 20000,
    'Non VAI Members': 25000,
    'Delegates from Egypt / Sri Lanka / Nepal / Bangladesh': 15000,
    'Post Graduates (with letter from HOD)': 15000
}
MASTER_CLASS_FEE = 5000
LUNCH_FEES = {'27': 750, '28': 750, 'both': 1500}
EXTRAS_FEES = {'gala': 2000, 'cruise': 2000, 'darshan': 1500}

def new_registration(request):
    if request.user:
        logout(request)  # pass the request, not the user
    return redirect("register_user")

def register_user(request):
    user = None

    # If user is logged in, get user object
    if request.user.is_authenticated:
        user = request.user

    if request.method == "POST":
        # If not logged in, check if email already exists
        email = request.POST.get("email")
        if not user:
            if registeredUser.objects.filter(email=email).exists():
                messages.error(request, "Email already registered. Please login.")
                return redirect("register_user")
            user = registeredUser()
        if user:
            messages.success(request, f"Registration updated! ")
        else:
            messages.success(request, f"Registerd! ")   
            
        if Transaction.objects.filter(user=user):
            messages.error(request,"You cant change please ask are team for any changes")
            return redirect("register_user")
        # --- Update user fields ---
        user.name = request.POST.get("name")
        user.designation = request.POST.get("designation")
        user.name_of_institution = request.POST.get("name_of_institution")
        user.address = request.POST.get("address")
        user.city = request.POST.get("city")
        user.state = request.POST.get("state")
        user.country = request.POST.get("country")
        user.pincode = request.POST.get("pincode")
        user.phone_code=request.POST.get("phone_code")
        user.phone_number = request.POST.get("phone_number")
        user.email = email
        user.IADVL_membership_number = request.POST.get("IADVL_membership_number")
        user.meal_preference = request.POST.get("meal_preference")
        user.category = request.POST.get("category")
        user.master_class = request.POST.get("master_class") == "on"
        user.gst_number = request.POST.get("gst_number")
        user.food_allergies = request.POST.get("food_allergies")
        user.save()
        Regno.objects.create(user=user)
        send_register_mail(email=user.email)

        

        # --- Remove old accompanying persons ---
        accompayingPerson.objects.filter(registered_user=user).delete()

        # --- Save new accompanying persons ---
        names = request.POST.getlist("ac_name[]")
        genders = request.POST.getlist("ac_gender[]")
        ages = request.POST.getlist("ac_age[]")
        relations = request.POST.getlist("ac_relation[]")
        meals = request.POST.getlist("ac_meal[]")
        join_events = request.POST.getlist("ac_join_event[]")
        lunches = request.POST.getlist("ac_lunch[]")
        gala = request.POST.getlist("ac_extra_gala[]")
        cruise = request.POST.getlist("ac_extra_cruise[]")
        darshan = request.POST.getlist("ac_extra_darshan[]")

        for i in range(len(names)):
            if names[i].strip():
                accompayingPerson.objects.create(
                    registered_user=user,
                    name=names[i].strip(),
                    gender=genders[i],
                    age=ages[i],
                    relation_to_delegate=relations[i],
                    meal_preference=meals[i],
                    join_event=(i < len(join_events) and join_events[i] == "on"),
                    lunch=lunches[i] if i < len(lunches) else "none",
                    extra_gala=(i < len(gala) and gala[i] == "on"),
                    extra_cruise=(i < len(cruise) and cruise[i] == "on"),
                    extra_darshan=(i < len(darshan) and darshan[i] == "on"),
                )

        # --- Backend Total Calculation ---
        delegate_fee = DELEGATE_FEES.get(user.category, 0)
        master_fee = MASTER_CLASS_FEE if user.master_class else 0
        accomp_fee = 0
        extras_total = 0

        accomp_list = accompayingPerson.objects.filter(registered_user=user)
        for ac in accomp_list:
            if ac.join_event:
                accomp_fee += delegate_fee
            extras_total += LUNCH_FEES.get(ac.lunch, 0)
            if ac.extra_gala:
                extras_total += EXTRAS_FEES['gala']
            if ac.extra_cruise:
                extras_total += EXTRAS_FEES['cruise']
            if ac.extra_darshan:
                extras_total += EXTRAS_FEES['darshan']

        subtotal = delegate_fee + master_fee + accomp_fee + extras_total
        final_total = round(subtotal * 1.03)  # 3% bank charges
        user.final_total = final_total
        user.save()

        
        return redirect("login")  # redirect to logged-in dashboard

    # GET request
    accomp_list = accompayingPerson.objects.filter(registered_user=user) if user else []
    return render(request, "register_form.html", {
        "user": user,
        "accomp_list": accomp_list,
    })

def logout_user(request):
    request.session.flush()  # Clear session
    messages.success(request, "Logged out successfully.")
    return redirect("login")

def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not registeredUser.objects.filter(email=email).exists:
            messages.error(request,"Please register first")
            return render(request,"login.html")

        otp = str(random.randint(100000, 999999))

        OTP.objects.update_or_create(email=email, defaults={"code": otp})

        send_mail(
            "Your OTP Code",
            f"Your OTP is {otp}",
            None,
            [email]
        )

        messages.success(request, "OTP Sent to your email")
        return redirect("verify", email=email)

    return render(request, "login.html")

def verify_otp_view(request, email):
    if request.method == "POST":
        input_otp = request.POST.get("otp")

        try:
            otp_obj = OTP.objects.get(email=email)

            if otp_obj.code == input_otp:
                user= registeredUser.objects.get(email=email)

                login(request, user)  # <--- Django built-in login auth
                otp_obj.delete()

                messages.success(request, "Logged in Successfully!")
                return redirect("register_user")
            else:
                messages.error(request, "Invalid OTP")
                return redirect("verify", email=email)

        except OTP.DoesNotExist:
            messages.error(request, "OTP not found, request again")
            return redirect("login")

    return render(request, "verify.html", {"email": email})






    
    
def send_register_mail(email):
    user=registeredUser.objects.get(email=email)
    name=user.name
    email=user.email
    link="http://127.0.0.1:8000/registration/login/"
    mailmessages=f"""Dear Dr. {name},

Thank you for submitting the VAICON 2026 registration form.

To complete your registration, kindly proceed with the payment at your earliest convenience {link}. If you have already made the payment, please ignore this message.

You will receive all updates and communication regarding the event on your registered email ID.

For any queries or assistance, feel free to contact us at Vaicon2026@gmail.com

Looking forward to welcome you at 'VAICON 2026', GOA.

With regards,
VAICON 2026"""
    send_mail(
        subject="VAICON 2026 Registration",
        message=mailmessages,
        from_email="info@vaicon2026.com",
        recipient_list=[email],
        fail_silently=False,
    )
def send_payment_mail(email):
    user=registeredUser.objects.get(email=email)
    name=user.name
    email=user.email
    link="http://127.0.0.1:8000/registration/login/"
    ragno=Regno.objects.filter(user=user).reg_no
    mailmessages=f"""
    Dear Dr. {name},

Greetings from VAICON 2026, GOA!

Thank you for registering for the 'VAICON 2026' to be held from 26th-28th March, 2026 at Alila Diwa, Goa.

Your unique conference registration number is {ragno} . (Please quote this conference registration number in all future correspondences.)

For any amendment in the recorded details, please send an email to the conference secretariat at (Vaicon2026@gmail.com) mentioning desired changes along with your unique registration number and mobile number.

Please ensure to update the conference secretariat of any changes in your contact details to enable periodic conference updates.

Looking forward to welcome you at 'VAICON 2026', GOA.


With regards,
VAICON 2026"""
    send_mail(
        subject="VAICON 2026 Registration",
        message=mailmessages,
        from_email="info@vaicon2026.com",
        recipient_list=[email],
        fail_silently=False,
    )
    