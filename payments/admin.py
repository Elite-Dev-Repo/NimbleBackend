from django.contrib import admin
from .models import Payment

# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'email', 'amount', 'status', 'channel', 'currency', 'paid_at', 'created_at')
    search_fields = ('reference', 'email')
    list_filter = ('status', 'channel', 'currency', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

