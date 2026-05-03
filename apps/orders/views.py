import uuid
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from apps.store.models import Product, ProductVariant
from .cart import SessionCart
from .models import Order, OrderItem, Address
from . import paystack


def cart_detail(request):
    cart = SessionCart(request)
    return render(request, 'orders/cart.html', {
        'cart':  cart,
        'items': cart.get_items(),
        'total': cart.get_total(),
        'count': cart.get_count(),
    })


@require_POST
def cart_add(request, product_id):
    cart       = SessionCart(request)
    product    = get_object_or_404(Product, id=product_id, is_active=True)
    variant_id = request.POST.get('variant_id')
    quantity   = int(request.POST.get('quantity', 1))
    variant    = None

    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

    cart.add(product=product, variant=variant, quantity=quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'count': cart.get_count(), 'success': True})

    return redirect('orders:cart_detail')


@require_POST
def cart_update(request, item_id):
    cart     = SessionCart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.update(item_id, quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'count': cart.get_count(), 'total': str(cart.get_total())})

    return redirect('orders:cart_detail')


@require_POST
def cart_remove(request, item_id):
    cart = SessionCart(request)
    cart.remove(item_id)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'count':   cart.get_count(),
            'total':   str(cart.get_total()),
            'success': True,
        })

    return redirect('orders:cart_detail')



def checkout(request):
    cart         = SessionCart(request)
    express      = request.session.get('express_order')
    express_item = None

    if express:
        try:
            express_product = Product.objects.get(id=express['product_id'], is_active=True)
            express_variant = None
            if express['variant_id']:
                express_variant = ProductVariant.objects.get(id=express['variant_id'])

            # Build a temporary item-like object for the template
            class ExpressItem:
                def __init__(self, product, variant, quantity):
                    self.product  = product
                    self.variant  = variant
                    self.quantity = quantity

            express_item  = ExpressItem(express_product, express_variant, express['quantity'])
            items         = [express_item]
            total         = (
                express_variant.final_price if express_variant else express_product.price
            ) * express['quantity']

        except (Product.DoesNotExist, ProductVariant.DoesNotExist):
            request.session.pop('express_order', None)
            return redirect('orders:cart_detail')
    else:
        items = cart.get_items()
        total = cart.get_total()

    if not items:
        return redirect('orders:cart_detail')
        
    user_addresses = []
    if request.user.is_authenticated:
        user_addresses = list(request.user.addresses.order_by('-is_default', '-created_at'))
    
    if request.method == 'POST':
      email = (
          request.user.email
          if request.user.is_authenticated
          else request.POST.get('email', '').strip()
      )
      notes               = request.POST.get('notes', '').strip()
      selected_address_id = request.POST.get('selected_address', 'custom')
      saved_address_obj   = None
  
      if (request.user.is_authenticated
              and user_addresses
              and selected_address_id != 'custom'):
          # ── Saved address path ──
          try:
              saved_address_obj = request.user.addresses.get(id=selected_address_id)
              snap     = saved_address_obj.as_snapshot()
              name     = snap['full_name']
              phone    = snap['phone']
              address  = snap['line1']
              address2 = snap['line2']
              city     = snap['city']
              state    = snap['state']
              postcode = snap['postcode']
              country  = snap['country']
          except Address.DoesNotExist:
              saved_address_obj   = None
              selected_address_id = 'custom'
  
      if selected_address_id == 'custom' or not saved_address_obj:
          # ── Custom / guest path ──
          name     = request.POST.get('name', '').strip()
          phone    = request.POST.get('phone', '').strip()
          address  = request.POST.get('address', '').strip()
          address2 = request.POST.get('address2', '').strip()
          city     = request.POST.get('city', '').strip()
          state    = request.POST.get('state', '').strip()
          postcode = request.POST.get('postcode', '').strip()
          country  = request.POST.get('country', '').strip()
  
      # ── Validation ──
      if not all([name, email, phone, address, city, state, postcode, country]):
          return render(request, 'orders/checkout.html', {
              'items':          items,
              'total':          total,
              'express_item':   express_item,
              'user_addresses': user_addresses,
              'error':          'Please fill in all required fields.',
              'post':           request.POST,
          })
  
      # ── Save new address if requested ──
      if (selected_address_id == 'custom'
              and request.user.is_authenticated
              and request.POST.get('save_address')):
          Address.objects.create(
              user       = request.user,
              full_name  = name,
              phone      = phone,
              line1      = address,
              line2      = address2,
              city       = city,
              state      = state,
              postcode   = postcode,
              country    = country,
              is_default = not user_addresses,
          )
  
      # ── Create order ──
      order = Order.objects.create(
          user              = request.user if request.user.is_authenticated else None,
          shipping_address  = saved_address_obj,
          reference         = uuid.uuid4().hex[:12].upper(),
          customer_name     = name,
          customer_email    = email,
          customer_phone    = phone,
          shipping_name     = name,
          shipping_phone    = phone,
          shipping_line1    = address,
          shipping_line2    = address2,
          shipping_city     = city,
          shipping_state    = state,
          shipping_postcode = postcode,
          shipping_country  = country,
          notes             = notes,
          total             = total,
          status            = 'pending',
      )
  
      for item in items:
          OrderItem.objects.create(
              order    = order,
              product  = item.product,
              variant  = item.variant,
              quantity = item.quantity,
              price    = item.variant.final_price if item.variant else item.product.price,
          )
  
      request.session['pending_order_ref'] = order.reference
      request.session.pop('express_order', None)
  
      callback_url = request.build_absolute_uri(
          reverse('orders:payment_callback')
      )
      try:
          authorization_url = paystack.initialize_payment(
              email        = email,
              amount_naira = order.total,
              reference    = order.reference,
              callback_url = callback_url,
              metadata     = {'order_reference': order.reference, 'customer_name': name},
          )
          return redirect(authorization_url)
      except Exception:
          order.delete()
          return render(request, 'orders/checkout.html', {
              'items':          items,
              'total':          total,
              'express_item':   express_item,
              'user_addresses': user_addresses,
              'error':          'Payment initialisation failed. Please try again.',
              'post':           request.POST,
          })
    
    return render(request, 'orders/checkout.html', {
        'items':        items,
        'total':        total,
        'express_item': express_item,
        'user_addresses': user_addresses,
    })



def payment_callback(request):
    """
    Paystack redirects here after payment attempt.
    We verify with Paystack before trusting it.
    """
    reference = request.GET.get('reference')
    if not reference:
        return redirect('orders:cart_detail')

    try:
        order = Order.objects.get(reference=reference)
    except Order.DoesNotExist:
        return redirect('orders:cart_detail')

    try:
        data = paystack.verify_payment(reference)
    except Exception:
        return render(request, 'orders/payment_failed.html', {'order': order})

    if data['status'] == 'success':
        order.status = 'confirmed'
        order.save(update_fields=['status', 'updated_at'])

        # clear cart
        cart = SessionCart(request)
        cart.clear()
        request.session.pop('pending_order_ref', None)

        return redirect('orders:order_confirmed', reference=order.reference)

    # Payment failed or was abandoned
    order.status = 'cancelled'
    order.save(update_fields=['status', 'updated_at'])
    return render(request, 'orders/payment_failed.html', {'order': order})


@csrf_exempt
@require_POST
def paystack_webhook(request):
    """
    Paystack server-to-server webhook.
    Handles charge.success as a backup to the callback.
    """
    signature = request.headers.get('X-Paystack-Signature', '')
    if not paystack.verify_webhook_signature(request.body, signature):
        return HttpResponse(status=400)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    if payload.get('event') == 'charge.success':
        reference = payload['data'].get('reference')
        try:
            order = Order.objects.get(reference=reference)
            if order.status == 'pending':
                order.status = 'confirmed'
                order.save(update_fields=['status', 'updated_at'])
        except Order.DoesNotExist:
            pass

    return HttpResponse(status=200)


def order_confirmed(request, reference):
    order = get_object_or_404(Order, reference=reference, status='confirmed')
    return render(request, 'orders/order_confirmed.html', {
        'order': order,
        'items': order.items.select_related('product', 'variant').all(),
    })


def order_now(request, product_id):
    product    = get_object_or_404(Product, id=product_id, is_active=True)
    variant_id = request.POST.get('variant_id')
    quantity   = int(request.POST.get('quantity', 1))
    variant    = None

    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

    # Store as a temporary "express order" in session
    request.session['express_order'] = {
        'product_id': product.id,
        'variant_id': variant.id if variant else None,
        'quantity':   quantity,
    }

    return redirect('orders:checkout')