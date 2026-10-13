from django.urls import path
from .views import product_detail , update_product

urlpatterns = [
    path(
        "products/<int:product_id>/",
        product_detail,
        name="product-detail",
    ),

    path(
        "products/<int:product_id>/update/",
        update_product,
    ),
]