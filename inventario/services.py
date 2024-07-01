"""
from decimal import Decimal
from django.db import transaction
from .models import CompProducto, StockAditivo, StockProducto


def producir_producto(prod_id, cantidad_producir, envasado):
    # Convertir cantidad_producir a Decimal
    cantidad_producir = Decimal(cantidad_producir)

    with transaction.atomic():
        # Obtener todos los componentes del producto
        
        componentes = CompProducto.objects.filter(producto_id=prod_id)

        # Verificar si hay suficientes aditivos en stock
        for componente in componentes:
            stock_aditivo = StockAditivo.objects.get(nomAditivo=componente.info_aditivo)
            cantidad_necesaria = cantidad_producir * componente.vv * componente.pp  

            if stock_aditivo.stock_ad_cant_lt < cantidad_necesaria:
                raise ValueError(f"No hay suficiente stock del aditivo {componente.info_aditivo.adtv_nom}.")
            else:
                stock_aditivo.stock_ad_cant_lt -= cantidad_necesaria
                stock_aditivo.save()

        # Incrementar el stock del producto
        stock_producto, created = StockProducto.objects.get_or_create(
            prod_copec_producto=prod_id,prod_copec_formato_envasado=envasado,
            defaults={'stock_prod_cant': cantidad_producir}
        )
        if not created:
            stock_producto.stock_prod_cant += cantidad_producir
        stock_producto.save()

        return stock_producto

"""
        
