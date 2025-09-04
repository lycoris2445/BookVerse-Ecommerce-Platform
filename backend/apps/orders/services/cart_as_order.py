from django.db import transaction
from django.db.models import Sum, F
from apps.orders.models import Order, OrderDetail
from apps.catalog.models import Book


def get_or_create_open_order(customer_id: int) -> Order:
    """Return existing Pending order for customer or create one."""
    order = (
        Order.objects.filter(CustomerID=customer_id, Status="Pending")
        .order_by("OrderID")
        .first()
    )
    if order:
        return order
    return Order.objects.create(CustomerID=customer_id, TotalAmount=0, Status="Pending")


@transaction.atomic
def add_item(order: Order, book_id: int, qty: int = 1) -> Order:
    # product lookup from book table
    product = Book.objects.get(BookID=book_id)
    # use select_for_update to prevent races on the same order details row
    qs = OrderDetail.objects.select_for_update()
    od, created = qs.get_or_create(
        OrderID=order.OrderID,
        BookID=book_id,
        defaults={"Quantity": 0, "Price": product.Price},
    )

    # always set current price
    od.Price = product.Price
    od.Quantity = max(0, int(od.Quantity) + int(qty))
    if od.Quantity == 0:
        od.delete()
    else:
        od.save(update_fields=["Price", "Quantity"])

    recalc_order_total(order)
    return order


def recalc_order_total(order: Order):
    total = (
        OrderDetail.objects.filter(OrderID=order.OrderID)
        .aggregate(s=Sum(F("Quantity") * F("Price")))
        .get("s")
        or 0
    )
    Order.objects.filter(pk=order.OrderID).update(TotalAmount=total)
    order.TotalAmount = total
    return total


@transaction.atomic
def update_qty(order: Order, book_id: int, qty: int):
    if int(qty) <= 0:
        OrderDetail.objects.filter(OrderID=order.OrderID, BookID=book_id).delete()
    else:
        od = OrderDetail.objects.get(OrderID=order.OrderID, BookID=book_id)
        od.Quantity = int(qty)
        od.save(update_fields=["Quantity"])
    recalc_order_total(order)
    return order
