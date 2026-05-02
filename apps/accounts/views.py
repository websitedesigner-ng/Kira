from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import User
from apps.orders.models import Order, Address
from apps.orders.cart import SessionCart

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        user     = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            SessionCart(request)
            return redirect(request.POST.get('next') or 'accounts:dashboard')

        return render(request, 'accounts/login.html', {
            'error': 'Invalid email or password.',
            'post':  request.POST,
        })

    return render(request, 'accounts/login.html', {
        'next': request.GET.get('next', ''),
    })



def signup_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip().lower()
        phone      = request.POST.get('phone', '').strip()
        password1  = request.POST.get('password1', '')
        password2  = request.POST.get('password2', '')

        if not all([first_name, email, password1]):
            return render(request, 'accounts/signup.html', {
                'error': 'Please fill in all required fields.',
                'post':  request.POST,
            })

        if password1 != password2:
            return render(request, 'accounts/signup.html', {
                'error': 'Passwords do not match.',
                'post':  request.POST,
            })

        if len(password1) < 8:
            return render(request, 'accounts/signup.html', {
                'error': 'Password must be at least 8 characters.',
                'post':  request.POST,
            })

        if User.objects.filter(username=email).exists():
            return render(request, 'accounts/signup.html', {
                'error': 'An account with this email already exists.',
                'post':  request.POST,
            })

        user = User.objects.create_user(
            username   = email,
            email      = email,
            password   = password1,
            first_name = first_name,
            last_name  = last_name,
            phone      = phone,
        )
        login(request, user)
        return redirect('accounts:dashboard')

    return render(request, 'accounts/signup.html')


@require_POST
def logout_view(request):
    logout(request)
    return redirect('store:home')


@login_required
def dashboard(request):
    recent_orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]

    return render(request, 'accounts/dashboard.html', {
        'recent_orders': recent_orders,
    })


@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'accounts/order_history.html', {
        'orders': orders,
    })


@login_required
def order_detail(request, reference):
    order = get_object_or_404(Order, reference=reference, user=request.user)
    return render(request, 'accounts/order_detail.html', {
        'order': order,
        'items': order.items.select_related('product', 'variant').all(),
    })


@login_required
def addresses(request):
    return render(request, 'accounts/addresses.html', {
        'addresses': request.user.addresses.all(),
    })


@login_required
def address_add(request):
    if request.method == 'POST':
        Address.objects.create(
            user       = request.user,
            label      = request.POST.get('label', '').strip(),
            full_name  = request.POST.get('full_name', '').strip(),
            phone      = request.POST.get('phone', '').strip(),
            line1      = request.POST.get('line1', '').strip(),
            line2      = request.POST.get('line2', '').strip(),
            city       = request.POST.get('city', '').strip(),
            state      = request.POST.get('state', '').strip(),
            postcode   = request.POST.get('postcode', '').strip(),
            country    = request.POST.get('country', '').strip(),
            is_default = request.POST.get('is_default') == 'on',
        )
        return redirect('accounts:addresses')

    return render(request, 'accounts/address_form.html')


@login_required
@require_POST
def address_delete(request, pk):
    get_object_or_404(Address, pk=pk, user=request.user).delete()
    return redirect('accounts:addresses')


@login_required
@require_POST
def address_set_default(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    return redirect('accounts:addresses')


@login_required
def profile(request):
    if request.method == 'POST':
        user            = request.user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name  = request.POST.get('last_name', '').strip()
        user.phone      = request.POST.get('phone', '').strip()
        user.save()
        messages.success(request, 'Profile updated.')
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html')