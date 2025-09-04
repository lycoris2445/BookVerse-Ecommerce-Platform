from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F

from .cart_serializers import AddItemIn, UpdateQtyIn, OrderOut
from apps.orders.models import Order, OrderDetail
from apps.orders.services.cart_as_order import get_or_create_open_order, add_item, update_qty


def _serialize(order: Order):
    items = (
        OrderDetail.objects.filter(OrderID=order.OrderID)
        .values("BookID", "Quantity", "Price")
        .annotate(line_total=F("Quantity") * F("Price"))
        .order_by("OrderDetailID")
    )
    return {
        "order_id": order.OrderID,
        "status": order.Status,
        "total": str(order.TotalAmount or 0),
        "items": list(items),
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cart(request):
    order = (
        Order.objects.filter(CustomerID=request.user.id, Status="Pending").order_by("OrderID").first()
    )
    if not order:
        return Response({"order_id": None, "status": "Pending", "total": "0.00", "items": []})
    return Response(_serialize(order))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    s = AddItemIn(data=request.data)
    s.is_valid(raise_exception=True)
    order = get_or_create_open_order(request.user.id)
    add_item(order, s.validated_data["book_id"], s.validated_data["qty"])
    return Response(_serialize(order), status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_item_qty(request):
    s = UpdateQtyIn(data=request.data)
    s.is_valid(raise_exception=True)
    order = get_or_create_open_order(request.user.id)
    update_qty(order, s.validated_data["book_id"], s.validated_data["qty"])
    return Response(_serialize(order))


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_item(request, book_id: int):
    order = get_or_create_open_order(request.user.id)
    update_qty(order, book_id, 0)
    return Response(_serialize(order))
