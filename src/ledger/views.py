from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, Context, Template
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from ledger.models import Transaction, Merchant

def route(**kwargs):
    def routed(request, **kwargs2):
        req_method = kwargs[request.method]
        return req_method(request, **kwargs2)
    return routed


def home(req):
    return render_to_response('home.html', {}, RequestContext(req))    


def user_is_merchant(user, merchant):
    # User is merchant
    if not user.merchant_accounts.exists():
        return HttpResponse('Unauthorized', status=401)

    # Only allowing 1 merchant account per user
    merch = user.merchant_accounts.first()

    # Trying to edit my own merch
    if merch.slug != merchant:
        return HttpResponse('Unauthorized', status=401)

    return merch

@login_required
def merchant_transaction(req, merchant):

    merch = user_is_merchant(req.user, merchant)

    accounts = merch.account_holders.all()
    ctx = {
            'merchant': merch,
            'accounts': accounts
    }

    return render_to_response('sales.html', ctx, RequestContext(req))

@login_required
def make_sale(req, merchant):
    merch = user_is_merchant(req.user, merchant)

    amount = float(req.POST['amount'])
    desc = req.POST['description']
    cust = req.POST['customer']
    customer = User.objects.get(username=cust)

    if merch.customer_has_funds(customer, amount):

        if amount <= 0.0:
            # Transaction must be positive
            return HttpResponse("Transaction amount must be a positive number")

        trans = Transaction(
                type=Transaction.DEBIT,
                merchant=merch,
                user=customer,
                amount=-amount,
                description=desc)

        trans.save()

        return HttpResponseRedirect('/%s/sale/%d/' % (merchant, trans.id))
        
    ctx = {
            'available': merch.customer_balance(customer),
            'amount': amount,
            'customer': customer,
            'reason': 'This customer does not have a sufficient balance to complete this purchase.'
            }

    return render_to_response('sale-denied.html', ctx, RequestContext(req))
      

@login_required
def sale_detail(req, merchant, transaction_id):
    trans = Transaction.query.get(id=transaction_id)
    merch = req.user.merchant_accounts.first()
   
    if (trans.merchant.slug == merchant) \
        and ((trans.user.username == req.user.username) \
            or (merch != None and trans.merchant.id == merch.id)):

        ctx = { 'transaction': trans }
        return render_to_response('sale-confirmed.html', ctx, RequestContext(req))

    return HttpResponse('Unauthorized', status=401)


@login_required
def customer_history(req, merchant, username):
    merch = Merchant.query.by_slug(merchant).first()
    customer = User.objects.get(username=username) 
    user_merch = req.user.merchant_accounts.first()

    if req.user.id == customer.id \
        or (user_merch != None and merch.id == user_merch.id and merch.has_customer(customer)):

            trans = Transaction.query.by_user(merch, customer).order_by('-timestamp')
            balance = merch.customer_balance(customer)

            ctx = { 
                    'transactions': trans,
                    'customer': customer,
                    'balance': balance,
                    'merchant': merch
            }
            return render_to_response('customer-history.html', ctx, RequestContext(req))

    return HttpResponse('Unauthorized', status=401)


@login_required
def customer_credit(req, merchant_name, customer_name):
    merch = user_is_merchant(req.user, merchant_name)
    customer = get_object_or_404(User, username=customer_name)
    balance = merch.customer_balance(customer)

    ctx = {
            'merchant': merch,
            'customer': customer,
            'balance': balance
    }

    return render_to_response('customer-add-credit.html', ctx, RequestContext(req))

