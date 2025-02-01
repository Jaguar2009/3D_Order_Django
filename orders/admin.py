from django.contrib import admin

from orders.models import Order, OrderFile, ModelCharacteristics, Cart, OrderApproval, OrderInfo, OrderRejection, \
    ServicePricing

admin.site.register(Order)
admin.site.register(OrderFile)
admin.site.register(ModelCharacteristics)
admin.site.register(Cart)
admin.site.register(OrderInfo)
admin.site.register(OrderApproval)
admin.site.register(OrderRejection)
admin.site.register(ServicePricing)



