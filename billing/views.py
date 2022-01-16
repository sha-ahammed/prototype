import datetime
import json

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from home.models import Orders, OrderItem, Purchase
from home.models import Product
from home.serializers import OrderSerializer
from .forms import ProductForm
from .utils import invoice_data_processor, product_data_processor


def test(user):
    return True if user.tokens.organisation else False


def login_view(request):
    if request.user.is_authenticated:
        return redirect("invoice_create")
    context = {}
    auth_form = AuthenticationForm(request)
    if request.method == "POST":
        auth_form = AuthenticationForm(request, data=request.POST)
        if auth_form.is_valid():
            user = auth_form.get_user()
            if user:
                login(request, user)
                return redirect("invoice_create")
        else:
            context["error_message"] = auth_form.get_invalid_login_error()
    context["auth_form"] = auth_form
    return render(request, 'gstbillingapp/login.html', context)


def refactor(request, function, model):
    context = {}
    last_order = model.objects.all().order_by('-id').first()
    if last_order:
        context['default_invoice_number'] = last_order.id + 1
    else:
        context['default_invoice_number'] = 1

    context['default_invoice_date'] = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    if request.method == 'POST':
        invoice_data = json.loads(request.body)

        function(invoice_data)

    return context


@login_required
@user_passes_test(test, redirect_field_name='/')
def invoice_create(request):
    return render(request, 'gstbillingapp/invoice_create.html', refactor(request, invoice_data_processor, Orders))


@login_required
@user_passes_test(test, redirect_field_name='/')
def purchase_create(request):
    return render(request, 'gstbillingapp/purchase_create.html', refactor(request, product_data_processor, Purchase))


@api_view(["POST"])
def orders(request):
    invoice_data = request.data

    order = invoice_data_processor(invoice_data)

    serializer = OrderSerializer(data=order, many=False)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.data, status=200)


@login_required
@user_passes_test(test, redirect_field_name='/')
def invoices(request):
    context = {'orders': Orders.objects.all().order_by('-id')}
    return render(request, 'gstbillingapp/invoices.html', context)


@login_required
@user_passes_test(test, redirect_field_name='/')
def purchases(request):
    context = {'orders': Purchase.objects.all().order_by('-id')}
    return render(request, 'gstbillingapp/purchases.html', context)


@login_required
@user_passes_test(test, redirect_field_name='/')
def invoice_delete(request):
    if request.method == "POST":
        invoice_id = request.POST["invoice_id"]
        invoice_obj = get_object_or_404(Orders, user=request.user, id=invoice_id)
        invoice_obj.delete()
    return redirect('invoices')


@login_required
@user_passes_test(test, redirect_field_name='/')
def customers(request):
    context = {'customers': User.objects.all()}
    return render(request, 'gstbillingapp/customers.html', context)


@login_required
@user_passes_test(test, redirect_field_name='/')
def products(request):
    context = {'products': Product.objects.all()}
    return render(request, 'gstbillingapp/products.html', context)


@login_required
@user_passes_test(test, redirect_field_name='/')
def product_edit(request, product_id):
    product_obj = Product.objects.get(id=product_id)
    if request.method == "POST":
        product_form = ProductForm(request.POST, instance=product_obj)
        if product_form.is_valid():
            product_form.save()
            return redirect('products')
    context = {'product_form': ProductForm(instance=product_obj)}
    return render(request, 'gstbillingapp/product_edit.html', context)


@login_required
@user_passes_test(test, redirect_field_name='/')
def invoice_viewer(request, invoice_id):
    invoice_obj = Orders.objects.get(id=invoice_id)

    return Response(invoice_obj)


@login_required
@user_passes_test(test, redirect_field_name='/')
def show_invoice(request, invoice_id):
    invoice = Orders.objects.get(id=invoice_id)
    items = OrderItem.objects.filter(order=invoice)

    context = {"invoice": invoice, "items": items}
    return render(request, 'gstbillingapp/invoice_show.html', context=context)


@login_required
@user_passes_test(test, redirect_field_name='/')
def product_add(request):
    if request.method == "POST":
        product_form = ProductForm(request.POST)
        if product_form.is_valid():
            new_product = product_form.save(commit=False)
            new_product.user = request.user
            new_product.save()

            return redirect('products')
    context = {'product_form': ProductForm()}
    return render(request, 'gstbillingapp/product_edit.html', context)


@login_required
@user_passes_test(test, redirect_field_name='/')
def product_delete(request):
    if request.method == "POST":
        product_id = request.POST["product_id"]
        product_obj = get_object_or_404(Product, user=request.user, id=product_id)
        product_obj.delete()
    return redirect('products')


@login_required
@user_passes_test(test, redirect_field_name='/')
def landing_page(request):
    if request.user.tokens.org:
        context = {"org": request.user.tokens.org}
        return render(request, 'gstbillingapp/pages/landing_page.html', context)
    return redirect('/')
