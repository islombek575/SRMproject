import uuid
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Sale, SaleItem


@login_required
def create_sale(request):
    # Draft sale olish yoki yaratish
    sale_id = request.session.get("sale_id")
    if sale_id:
        try:
            sale = Sale.objects.get(id=uuid.UUID(sale_id), status="draft")
        except (Sale.DoesNotExist, ValueError):
            sale = Sale.objects.create(status="draft", seller=request.user)
            request.session["sale_id"] = str(sale.id)
    else:
        sale = Sale.objects.create(status="draft", seller=request.user)
        request.session["sale_id"] = str(sale.id)

    items = sale.items.all()
    total = sum(item.subtotal for item in items)

    if request.method == "POST":
        # Mahsulot qo'shish
        if "add_product" in request.POST:
            barcode = request.POST.get("barcode")
            quantity = int(request.POST.get("quantity", 1))
            try:
                product = Product.objects.get(barcode=barcode)

                if product.stock <= quantity:
                    messages.error(request, f"🚫 {product.name} stokda yetarli emas!")
                    return redirect("sales:create_sale")

                # SaleItem olish yoki yaratish
                item, created = SaleItem.objects.get_or_create(
                    sale=sale,
                    product=product,
                    defaults={
                        "quantity": quantity,
                        "price": product.price,
                        "subtotal": product.price * quantity,
                        "seller": request.user
                    }
                )
                if not created:
                    item.quantity += quantity
                    item.subtotal = item.price * item.quantity
                    item.save()

                messages.success(request, f"✅ {product.name} qo‘shildi!")
            except Product.DoesNotExist:
                messages.error(request, "🚫 Bunday barcode topilmadi!")
            return redirect("sales:create_sale")

        # Mahsulot o'chirish
        if "remove_product" in request.POST:
            item_id = request.POST.get("remove_product")
            item = get_object_or_404(SaleItem, id=item_id)
            item.delete()
            messages.success(request, f"{item.product.name} o'chirildi!")
            return redirect("sales:create_sale")

        # Tozalash
        if "clear_sale" in request.POST:
            sale.items.all().delete()
            messages.success(request, "🧹 Savdo tozalandi!")
            return redirect("sales:create_sale")

        # Bekor qilish
        if "cancel_sale" in request.POST:
            sale.delete()
            request.session.pop("sale_id", None)
            messages.info(request, "❌ Savdo bekor qilindi!")
            return redirect("inventory:dashboard_view")

    return render(request, "sale/create-sale.html", {"sale": sale, "items": items, "total": total})


@login_required
def finish_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id, status="draft")
    total = sum(item.subtotal for item in sale.items.all())

    if request.method == "POST":
        paid_amount = Decimal(request.POST.get("paid_amount", "0"))
        payment_type = request.POST.get("payment_type")
        customer_name = request.POST.get("customer_name", "")


        sale.total_amount = total
        sale.paid_amount = paid_amount
        sale.change_amount = paid_amount - total
        sale.status = "finished"
        sale.payment_type = payment_type
        sale.customer_name = customer_name if payment_type == "credit" else ""
        sale.save()

        # Stockni kamaytirish
        for item in sale.items.all():
            product = item.product
            product.stock -= item.quantity
            product.save()

        request.session.pop("sale_id", None)
        messages.success(request, "💰 Savdo muvaffaqiyatli yakunlandi!")
        return redirect("inventory:dashboard_view")

    return render(
        request,
        "sale/create-sale.html",
        {"sale": sale, "items": sale.items.all(), "total": total},
    )
