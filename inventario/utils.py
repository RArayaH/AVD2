from django.conf import settings
from django.contrib.staticfiles import finders
import os
from .models import ProdCopec, StockAditivo, StockInsumo, CompProducto, LoteProd, Despacho
from decimal import Decimal
from django.db import transaction
import math

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = finders.find(uri.replace(settings.STATIC_URL, ""))
        if not path:
            raise Exception('File {} not found in STATICFILES_DIRS.'.format(uri))
    else:
        return uri

    if not os.path.isfile(path):
        raise Exception('Media URI must start with {} or {}'.format(settings.STATIC_URL, settings.MEDIA_URL))

    return path

##############################################################################################################

@transaction.atomic
def agregar_stock(prod_copec_id, valor_total, lote_prod_id):
    try:
        
        prod_copec = ProdCopec.objects.get(prod_copec_id=prod_copec_id)
        insumo = prod_copec.insumo
        lote = LoteProd.objects.get(lote_prod_id=lote_prod_id)

        
        """
        stock_producto, created = StockProducto.objects.get_or_create(
            prod_copec=prod_copec,
            defaults={'stock_prod_cant_vol': valor_total,
                      'stock_prod_cant_uni':math.trunc(Decimal(valor_total) / insumo.insumo_vol)}
        )
        
        if not created:                
            stock_producto.stock_prod_cant_vol +=  Decimal(valor_total)
            stock_producto.stock_prod_cant_uni +=  math.trunc(Decimal(valor_total) / insumo.insumo_vol)
            stock_producto.save()

        """
        comp_productos = CompProducto.objects.filter(producto=prod_copec.producto)
        for comp_producto in comp_productos:
            aditivo = comp_producto.info_aditivo
            cantidad_a_descontar = Decimal(valor_total) * comp_producto.vv
            stock_aditivo = StockAditivo.objects.get(nomAditivo=aditivo)
            if stock_aditivo.stock_ad_cant_lt < cantidad_a_descontar:
                raise ValueError(f"No hay suficiente stock del aditivo {aditivo.adtv_nom}")
            stock_aditivo.stock_ad_cant_lt -= cantidad_a_descontar
            stock_aditivo.save()

        if insumo.insumo_nom != 'GRANEL':
            cantidad_a_descontar_insumo = math.trunc(Decimal(valor_total) / insumo.insumo_vol)
            stock_insumo = StockInsumo.objects.get(insumo=insumo)
            if stock_insumo.stock_in_cant_unit < cantidad_a_descontar_insumo:
                raise ValueError(f"No hay suficiente stock del insumo {insumo.insumo_nom}")
            stock_insumo.stock_in_cant_unit -= cantidad_a_descontar_insumo
            stock_insumo.save()

        lote.volumen_prod += valor_total
        lote.cant_prod += math.trunc(Decimal(valor_total) / insumo.insumo_vol)
        lote.estado_produccion = 'DISPONIBLE PARA DESPACHO'
        lote.save()
    except ProdCopec.DoesNotExist:
        raise ValueError(f"Producto con id {prod_copec_id} no existe")
    except StockAditivo.DoesNotExist:
        raise ValueError(f"Stock de aditivo no existe")
    except StockInsumo.DoesNotExist:
        raise ValueError(f"Stock de insumo no existe")

##############################################################################################################

def generar_despacho(lote_prod_id, cantidad):
    try:
        with transaction.atomic():
            # Obtener el lote de producción
            lote = LoteProd.objects.select_for_update().get(lote_prod_id=lote_prod_id)
            
            # Verificar si hay suficiente cantidad para despachar
            if lote.cant_prod < cantidad:
                raise ValueError("Cantidad insuficiente en el lote de producción")

            # Crear o actualizar el despacho
            despacho = Despacho.objects.create(lote=lote,cant_despacho=cantidad)

            despacho.save()
           
            # Actualizar la cantidad del lote de producción
            lote.cant_prod = lote.cant_prod - cantidad
            
            if lote.cant_prod == 0.0:
                lote.estado_produccion = 'DESPACHADO'
            
            lote.save()

            return despacho

    except LoteProd.DoesNotExist:
        raise ValueError(f"Lote de producción con ID {lote_prod_id} no encontrado")
    except Exception as e:
        raise ValueError(f"Error al actualizar el despacho: {str(e)}")

##############################################################################################################

def aumentar_stock_mp(stock_ad_id, cantidad):
    try:
        with transaction.atomic():        
            # Obtener el lote de producción
            stockmp = StockAditivo.objects.select_for_update().get(stock_ad_id=stock_ad_id)   
            
            stockmp.stock_ad_cant_lt = stockmp.stock_ad_cant_lt + cantidad
            stockmp.save()

            return stockmp

    except LoteProd.DoesNotExist:
        raise ValueError(f"Stock con ID {stock_ad_id} no encontrado")
    except Exception as e:
        raise ValueError(f"Error al actualizar el despacho: {str(e)}")

        """
        lote = LoteProd.objects.select_for_update().get(lote_prod_id=lote_prod_id)
        lote_prod_id = stockmp.lote.lote_prod_id
        # Actualizar la cantidad del lote de producción
        if lote.cant_prod == 0.0:
            lote.estado_produccion = 'DESPACHADO'
        
        lote.save()
        """

##############################################################################################################

def aumentar_stock_insumo(stock_in_id, cantidad):
    try:
        with transaction.atomic():         
            # Obtener el lote de producción
            stockinsu = StockInsumo.objects.select_for_update().get(stock_in_id=stock_in_id)

            # Actualizar la cantidad del lote de producción
            stockinsu.stock_in_cant_unit = stockinsu.stock_in_cant_unit + cantidad
            stockinsu.save()

            return stockinsu

    except LoteProd.DoesNotExist:
        raise ValueError(f"Stock con ID {stock_in_id} no encontrado")
    except Exception as e:
        raise ValueError(f"Error al actualizar el despacho: {str(e)}")
    
##############################################################################################################

def actualizar_despacho(despacho_id):
    try:
        with transaction.atomic():         
            # Obtener el lote de producción
            despacho = Despacho.objects.select_for_update().get(despacho_id=despacho_id)

            # Actualizar el estado del despacho
            despacho.tipo_despacho = 'LISTO PARA DESPACHO'
            despacho.save()

            return despacho

    except Despacho.DoesNotExist:
        raise ValueError(f"Stock con ID {despacho_id} no encontrado")
    except Exception as e:
        raise ValueError(f"Error al actualizar el despacho: {str(e)}")
    

##############################################################################################################

def despachar(despacho_id):
    try:
        with transaction.atomic():        
            # Obtener el lote de producción
            despacho = Despacho.objects.select_for_update().get(despacho_id=despacho_id)

            # Actualizar el estado del despacho
            despacho.tipo_despacho = 'DESPACHADO'
            despacho.save()

            return despacho

    except Despacho.DoesNotExist:
        raise ValueError(f"Stock con ID {despacho_id} no encontrado")
    except Exception as e:
        raise ValueError(f"Error al actualizar el despacho: {str(e)}")