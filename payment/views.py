from django.shortcuts import render

import hashlib, random
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import registeredUser, Transaction ,MasterClassPayment
from django.views.decorators.csrf import csrf_exempt
import hashlib
import uuid
from django.urls import reverse
from django.shortcuts import redirect
from registration.views import send_payment_mail

def generate_hash(data):
    """
    Generate SHA512 hash for PayU payment
    """
    hash_string = f"{data['key']}|{data['txnid']}|{data['amount']}|{data['productinfo']}|{data['firstname']}|{data['email']}|||||||||||{settings.PAYU_MERCHANT_SALT}"
    return hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()



def generate_txn_id():
    return "TXN" + str(random.randint(100000, 999999))

def start_payment(request):
    user = request.user
    amount = user.final_total  # take amount from model 

    txnid = generate_txn_id()

    Transaction.objects.create(
        user=user,
        txnid=txnid,
        amount=amount,
        status="pending"
    )

    # HASH
    hash_string = f"{settings.PAYU_MERCHANT_KEY}|{txnid}|{amount}|Registration Fee|{user.name}|{user.email}|||||||||||{settings.PAYU_MERCHANT_SALT}"
    hashh = hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()

    data = {
        "action": f"{settings.PAYU_BASE_URL}/_payment",
        "key": settings.PAYU_MERCHANT_KEY,
        "txnid": txnid,
        "hash": hashh,
        "amount": amount,
        "firstname": user.name,
        "email": user.email,
        "phone": user.phone_number,
        "productinfo": "Registration Fee",
        "surl": request.build_absolute_uri(settings.PAYU_SUCCESS_URL),
        "furl": request.build_absolute_uri(settings.PAYU_FAILURE_URL),
    }

    return render(request, "payu_redirect.html", data)



@csrf_exempt
def payment_success(request):
    """
    PayU success callback (POST)
    """
    txnid = request.POST.get("txnid")
    status = request.POST.get("status")
    user=request.user
    send_payment_mail(email=user.email)

    transaction = Transaction.objects.filter(txnid=txnid).first()
    if transaction:
        transaction.status = status
        transaction.save()

    return render(request, "success.html", {"transaction": transaction})


@csrf_exempt
def payment_failure(request):
    """
    PayU failure callback (POST)
    """
    txnid = request.POST.get("txnid")

    transaction = Transaction.objects.filter(txnid=txnid).first()
    if transaction:
        transaction.status = "failed"
        transaction.save()

    return render(request, "failure.html", {"transaction": transaction})



def payment_page(request):
    user = request.user
    return render(request, "payment_page.html", {"user": user})


def masterclass_payment(request):
  

    """
    Masterclass payment without forms.py or utils
    """
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()

        # Optional fields
        designation = request.POST.get("designation", "").strip()
        institution_name = request.POST.get("institution_name", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        country = request.POST.get("country", "").strip()

        

        txnid = uuid.uuid4().hex[:20]
        amount = 1 # fee

        # Save transaction
        payment = MasterClassPayment.objects.create(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            designation=designation,
            institution_name=institution_name,
            city=city,
            state=state,
            country=country,
            txnid=txnid,
            amount=amount,
            status="PENDING"
        )

        
        

        return redirect("pay_redirect", txnid=txnid)

    return render(request, "masterclass_form.html")


@csrf_exempt
def masterclass_payment_success(request):
    txnid = request.POST.get("txnid") or request.GET.get("txnid")
    MasterClassPayment.objects.filter(txnid=txnid).update(status="SUCCESS")
    return render(request, "success.html")


@csrf_exempt
def masterclass_payment_failure(request):
    txnid = request.POST.get("txnid") or request.GET.get("txnid")
    MasterClassPayment.objects.filter(txnid=txnid).update(status="FAILED")
    return render(request, "failure.html")

def pay_redirect(request, txnid):
    payment = MasterClassPayment.objects.get(txnid=txnid)
    
    data = {
        "key": settings.PAYU_MERCHANT_KEY,
        "txnid": payment.txnid,
        "amount": payment.amount,
        "productinfo": "Masterclass",
        "firstname": payment.full_name,
        "email": payment.email,
        "phone": payment.phone_number,
        
            "surl": request.build_absolute_uri(reverse("masterclass-payment-success")),
            "furl": request.build_absolute_uri(reverse("masterclass-payment-failure")),
    }
    data["hash"] = generate_hash(data)

    return render(request, "pay_redirect.html", {"action": settings.PAYU_BASE_URL, "posted": data})
