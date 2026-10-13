
import time

from django.core.cache import cache
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product


@api_view(["GET"])
def product_detail(request, product_id):
    cache_key = f"product:{product_id}"

    # 1. Check Redis cache first
    cached_product = cache.get(cache_key)

    if cached_product is not None:
        return Response({
            "source": "redis",
            "product": cached_product,
        })

    # 2. Cache miss: fetch from database
    start = time.perf_counter()

    product = get_object_or_404(Product, id=product_id)

    db_time_ms = round(
        (time.perf_counter() - start) * 1000, 3
    )

    product_data = {
        "id": product.id,
        "name": product.name,
        "price": str(product.price),
        "stock": product.stock,
        "updated_at": product.updated_at.isoformat(),
    }

    # 3. Store a temporary copy in Redis
    cache.set(cache_key, product_data, timeout=60)

    return Response({
        "source": "database",
        "db_time_ms": db_time_ms,
        "product": product_data,
    })


@api_view(["PATCH"])
def update_product(request, product_id):
    product = get_object_or_404(
        Product, id=product_id
    )

    if "name" in request.data:
        product.name = request.data["name"]

    if "price" in request.data:
        product.price = request.data["price"]

    if "stock" in request.data:
        product.stock = request.data["stock"]

    product.save()

    # Remove stale cached data
    cache.delete(f"product:{product_id}")

    return Response({
        "message": "Product updated",
        "id": product.id,
    })