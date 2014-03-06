from django.db import models
from django.db.models import Sum
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from model_utils.managers import PassThroughManager


class MerchantQuerySet(QuerySet):
    def by_slug(self, slug):
        return self.filter(slug=slug)


class Merchant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField()
    joined = models.DateTimeField(auto_now_add=True)
    # TODO: Presently, only have 1 merchant account, not enforced
    user = models.ForeignKey(User, related_name='merchant_accounts')

    query = PassThroughManager.for_queryset_class(MerchantQuerySet)()

    def customer_has_funds(self, customer, sale_amount):
        available = self.customer_balance(customer)
        return sale_amount <= available

    def customer_balance(self, customer):
        balance = Transaction.query.by_user(self, customer).aggregate(Sum('amount'))
        return balance.get('amount__sum')

    def has_customer(self, customer):
        return self.account_holders.filter(user=customer).exists()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super(Merchant, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name
    

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    accounts = models.ManyToManyField(Merchant, related_name='account_holders')

    def __unicode__(self):
        return unicode(self.user.username)


class TransactionQuerySet(QuerySet):
    def for_merchant(self, merchant):
        return self.filter(merchant=merchant)

    def by_user(self, merchant, user):
        return self.filter(user=user).for_merchant(merchant)

    def by_type(self, trans_type):
        return self.filter(type=trans_type)

    def since(self, when):
        return self.filter(timestamp__gte=when)

class Transaction(models.Model):
    DEBIT = 'debit'
    CREDIT = 'credit'
    TRANSACTION_TYPES = ((DEBIT, 'Debit'), (CREDIT, 'Credit'))

    timestamp = models.DateTimeField(auto_now_add=True)
    merchant = models.ForeignKey(Merchant)
    user = models.ForeignKey(User)
    amount = models.FloatField()
    type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    description = models.TextField()

    query = PassThroughManager.for_queryset_class(TransactionQuerySet)()

    def __unicode__(self):
        return unicode(('%s-%s') % (self.user.username,  self.timestamp))


class Balance(models.Model):
    user = models.ForeignKey(User)
    amount = models.FloatField()

