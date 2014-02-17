from django.contrib import admin
from ledger.models import Merchant, Transaction, UserProfile

admin.site.register(Merchant)
admin.site.register(Transaction) 
admin.site.register(UserProfile)
