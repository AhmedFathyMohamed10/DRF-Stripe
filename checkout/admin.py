from django.contrib import admin
from .models import Transaction
# Register your models here.

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'amount', 'currency', 'status', 'created_at')
    search_fields = ('stripe_session_id', 'stripe_payment_intent', 'status')
    list_filter = ('status', 'currency', 'created_at')
    readonly_fields = ('created_at',)
