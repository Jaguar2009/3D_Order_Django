from django.contrib import admin

from orders.models import Order, OrderFile, ModelCharacteristics, Cart, PurchasedOrder

admin.site.register(Order)
admin.site.register(OrderFile)
admin.site.register(ModelCharacteristics)
admin.site.register(Cart)
admin.site.register(PurchasedOrder)


