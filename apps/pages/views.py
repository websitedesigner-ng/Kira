from django.shortcuts import render


def our_story(request):
    return render(request, 'pages/our_story.html')

def savoir_faire(request):
    return render(request, 'pages/savoir_faire.html')

def contact(request):
    return render(request, 'pages/contact.html')

def contact_submit(request):
    if request.method != 'POST':
        return redirect('pages:contact')

    first_name   = request.POST.get('first_name', '').strip()
    last_name    = request.POST.get('last_name', '').strip()
    email        = request.POST.get('email', '').strip()
    phone        = request.POST.get('phone', '').strip()
    subject      = request.POST.get('subject', 'General Enquiry').strip()
    order_number = request.POST.get('order_number', '').strip()
    message      = request.POST.get('message', '').strip()

    if not all([first_name, last_name, email, message]):
        messages.error(request, 'Please fill in all required fields.')
        return redirect('pages:contact')

    print(f"""
[KIRA CONTACT] New submission
Subject:   {subject}
Name:      {first_name} {last_name}
Email:     {email}
Phone:     {phone or '—'}
Order No:  {order_number or '—'}
Message:   {message}
    """.strip())

    messages.success(request, 'Your message has been sent.')
    return redirect('pages:contact')

def shipping_returns(request):
    return render(request, 'pages/shipping_returns.html')

def faqs(request):
    return render(request, 'pages/faqs.html')

def book_appointment(request):
    return render(request, 'pages/book_appointment.html')


def book_appointment_submit(request):
    if request.method != 'POST':
        return redirect('pages:book_appointment')

    first_name       = request.POST.get('first_name', '').strip()
    last_name        = request.POST.get('last_name', '').strip()
    email            = request.POST.get('email', '').strip()
    phone            = request.POST.get('phone', '').strip()
    visit_type       = request.POST.get('visit_type', 'Personal Shopping').strip()
    preferred_date   = request.POST.get('preferred_date', '').strip()
    preferred_time   = request.POST.get('preferred_time', '').strip()
    alternative_date = request.POST.get('alternative_date', '').strip()
    guests           = request.POST.get('guests', '1').strip()
    piece_interest   = request.POST.get('piece_interest', '').strip()
    notes            = request.POST.get('notes', '').strip()
    referral         = request.POST.get('referral', '').strip()

    if not all([first_name, last_name, email, phone, preferred_date, preferred_time]):
        messages.error(request, 'Please fill in all required fields.')
        return redirect('pages:book_appointment')

    print(f"""
[KIRA APPOINTMENT] New request
Type:      {visit_type}
Name:      {first_name} {last_name}
Email:     {email}
Phone:     {phone}
Date:      {preferred_date} at {preferred_time}
Alt Date:  {alternative_date or '—'}
Guests:    {guests}
Piece:     {piece_interest or '—'}
Notes:     {notes or '—'}
Referral:  {referral or '—'}
    """.strip())

    messages.success(request, 'Your appointment request has been received.')
    return redirect('pages:book_appointment')
    

def sustainability(request):
    return render(request, 'pages/sustainability.html')

def size_guide(request):
    return render(request, 'pages/size_guide.html')

def privacy_policy(request):
    return render(request, 'pages/privacy_policy.html')

def terms(request):
    return render(request, 'pages/terms.html')

def page_not_found(request, exception):
    return render(request, 'errors/404.html', status=404)

def server_error(request):
    return render(request, 'errors/500.html', status=500)

def permission_denied(request, exception):
    return render(request, 'errors/403.html', status=403)

def bad_request(request, exception):
    return render(request, 'errors/400.html', status=400)