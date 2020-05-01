from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, CustomerContact, Orders, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum

# Create your views here.
MERCHANT_KEY = '_MxBpabI0EqY9nyq'


def index(request):
    allProds = []
    catProds = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catProds}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - n // 4)
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {
        'allProds': allProds
    }
    return render(request, 'shop/index.html', params)


def searchMatch(query, item):
    """ return true if query matches the item  """
    query = query.lower()
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower() or query in item.subcategory.lower():
        return True
    else:
        return False


def search(request):
    query = request.GET.get('search')
    allProds = []
    catProds = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catProds}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - n // 4)
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {
        'allProds': allProds
    }
    if len(allProds) == 0 or len(query) < 4:
        params = {
            'msg': "Please Make Sure You Enter a Relevant item"
        }
    return render(request, 'shop/search.html', params)


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        query = request.POST.get('query')
        contact = CustomerContact(name=name, email=email, phone=phone, query=query)
        contact.save()
    return render(request, 'shop/contact.html')


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId')
        email = request.POST.get('email')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(orderId) > 0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                response = json.dumps({"status": "success",
                                       "updates": updates,
                                       "itemsJson": order[0].items_json},
                                      default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')


def productView(request, myid):
    # fetch the product using id

    product = Product.objects.filter(id=myid)
    return render(request, 'shop/product.html', {"product": product})


def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('items_json', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        address1 = request.POST.get('addr1', '')
        landmark = request.POST.get('landmark', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zipcode', '')
        amount = request.POST.get('amount', '')
        order = Orders(items_json=items_json, name=name, phoneNo=phone, email=email,
                       address=address1, landmark=landmark, city=city,
                       state=state, zip_code=zip_code, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The Order has been placed.")
        update.save()
        # return render(request, 'shop/checkout.html', {'thank': True, 'id': order.order_id})
        # Request paytm to transfer the amount to your account after payment by user
        param_dict = {
            'MID': 'vQfOun19018534043455',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',
        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'shop/paytm.html', {'param_dict': param_dict})
    return render(request, 'shop/checkout.html')


@csrf_exempt
def handlerequest(request):
    # will handle paytm post request
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because ' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})
