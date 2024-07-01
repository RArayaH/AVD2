#"""
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from .forms import UserForm, InfoAditivoForm, ProductoForm, CompProductoForm, StockAditivoForm, InsumoForm, StockProductoForm, StockInsumoForm, ProdCopecForm, OdpForm, CalidadForm, GuiaDespachoForm
from .models import InfoAditivo, Producto, CompProducto, StockAditivo, Insumo, StockProducto, StockInsumo, ProdCopec, LoteProd, Despacho 
from django.http import HttpResponse
from .utils import link_callback, agregar_stock, generar_despacho, aumentar_stock_mp, aumentar_stock_insumo, actualizar_despacho, despachar
from django.http import HttpResponseForbidden
from decimal import Decimal
from django.template.loader import get_template
from xhtml2pdf import pisa
import datetime


# Create your views here.
##################################### METODOS USUARIO #####################################
@login_required(login_url='login')
def crud_usuario(request):
    users = User.objects.all ()
    grupo = request.user.groups.first()
    
    context = {
        'users': users,
        'grupo': grupo
    }
    
    return render(request, 'usercrud/crud_usuario.html', context)

@login_required(login_url='login')
def crear_usuario(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/crud_usuario')
    else:
        form = UserForm()

    grupo = request.user.groups.first()

    context = {
        'form': form,
        'grupo': grupo
    }
    return render(request, 'usercrud/crear_usuario.html', context)

@login_required(login_url='login') 
def editar_usuario(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('/crud_usuario')
    else:
        form = UserForm(instance=user)

    grupo = request.user.groups.first()
    
    context = {
        'form': form,
        'grupo': grupo
    }
    return render(request, 'usercrud/editar_usuario.html', context)    

@login_required(login_url='login')
def eliminar_usuario(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('/crud_usuario')
    
    grupo = request.user.groups.first()
    
    context = {
        'user': user,
        'grupo': grupo
    }
    return render(request, 'usercrud/eliminar_usuario.html', context)


##################################### METODOS LOGIN LOGOUT #####################################

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/home')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/home')
            else:
                messages.info(request, 'login.html', {'error': 'Nombre de usuario o contraseña incorrectos'})
            
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

##################################### PLANTILLA BASE #####################################

@login_required(login_url='login')
#@allowed_users(allowed_roles=['GESTION'])
def home(request):

    user = request.user

    if user.groups.exists():
        group = user.groups.first().name

        if group == 'GESTION':
            return redirect('/crud_orden_prod')
        elif group == 'PATIO':
            return redirect('/crud_despacho')
        elif group == 'CALIDAD':
            return redirect('/crud_calidad')
        elif group == 'GUIA_DESP':
            return redirect('/crud_guia_despacho')
        else:
            return redirect('/home')
        
    grupo = request.user.groups.first()

    context = {
        'username': request.user.username,
        'grupo': grupo
    }

    return render(request, 'usercrud/welcome_user.html', context)

##################################### METODOS MATERIA PRIMA #####################################

@login_required(login_url='login')
def crud_mp(request):

    sort_by = request.GET.get('sort_by', 'adtv_id')
    direction = request.GET.get('direction', 'asc')

    if direction == 'desc':
        sort_by = '-' + sort_by
    context = {
            'mps': InfoAditivo.objects.all().order_by(sort_by),
            'sort_by': sort_by.strip('-'), 
            'direction': direction,
            'grupo': request.user.groups.first()
        }
    
    return render(request, 'inventario/materia_prima/crud_mp.html', context)

@login_required(login_url='login')
def ingresar_mp(request):
    if request.method == 'POST':
        form = InfoAditivoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/crud_mp')  
    else:
        form = InfoAditivoForm()

    grupo = request.user.groups.first()
    
    context = {
        'form': form,
        'grupo': grupo
    }
    
    return render(request, 'inventario/materia_prima/ingresar_mp.html', context)

@login_required(login_url='login')
def editar_mp(request, adtv_id):
    aditivo = get_object_or_404(InfoAditivo, adtv_id=adtv_id)
    if request.method == 'POST':
        form = InfoAditivoForm(request.POST, instance=aditivo)
        if form.is_valid():
            form.save()
            return redirect('/crud_mp')
    else:
        form = InfoAditivoForm(instance=aditivo)

    grupo = request.user.groups.first()
    
    context = {
        'form': form,
        'grupo': grupo
    }

    return render(request, 'inventario/materia_prima/editar_mp.html', context)

@login_required(login_url='login')
def eliminar_mp(request, adtv_id):
    aditivo = get_object_or_404(InfoAditivo, adtv_id=adtv_id)
    if request.method == 'POST':
        aditivo.delete()
        return redirect('/crud_mp')

    grupo = request.user.groups.first()
    
    context = {
        'aditivo': aditivo,
        'grupo': grupo
    }

    return render(request, 'inventario/materia_prima/eliminar_mp.html', context)

##################################### METODOS INSUMO #####################################
@login_required(login_url='login')
def crud_insu(request):

    sort_by = request.GET.get('sort_by', 'insumo_id')
    direction = request.GET.get('direction', 'asc')

    if direction == 'desc':
        sort_by = '-' + sort_by

    insus = Insumo.objects.all().order_by(sort_by)

    grupo = request.user.groups.first()
    
    context = {
        'insus': insus,
        'sort_by': sort_by.strip('-'), 
        'direction': direction,
        'grupo': grupo
    }

    return render(request, 'inventario/insumos/crud_insu.html', context) 


@login_required(login_url='login')
def ingresar_in(request):

    if request.method == 'POST':
        form = InsumoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/crud_insu')
    else:
        form = InsumoForm()

    grupo = request.user.groups.first()
    
    context = {
        'form': form,
        'grupo': grupo
    }

    return render(request, 'inventario/insumos/ingresar_insumo.html', context)

@login_required(login_url='login')
def eliminar_in(request, insumo_id):

    insumo = get_object_or_404(Insumo, insumo_id=insumo_id)
    if request.method == 'POST':
        insumo.delete()
        return redirect('/crud_insu')
    
    grupo = request.user.groups.first()
    
    context = {
        'insumo': insumo,
        'grupo': grupo
    }

    return render(request, 'inventario/insumos/eliminar_insumo.html', context)

@login_required(login_url='login')
def editar_in(request, insumo_id):

    insumo = get_object_or_404(Insumo, insumo_id=insumo_id)
    if request.method == 'POST':
        form = InsumoForm(request.POST, instance=insumo)
        if form.is_valid():
            form.save()
            return redirect('/crud_insu')  
    else:
        form = InsumoForm(instance=insumo)

    grupo = request.user.groups.first()
    
    context = {
        'form': form,
        'grupo': grupo
    }

    return render(request, 'inventario/insumos/editar_insumo.html', context)

##################################### METODOS PRODUCTO #####################################
@login_required(login_url='login')
def crud_producto(request):

    productos = Producto.objects.all()

    grupo = request.user.groups.first()
    
    context = {
        'productos': productos,
        'grupo': grupo
    }

    return render(request, 'inventario/productos/crud_producto.html', context) 

@login_required(login_url='login')
def ingresar_producto(request):

    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/crud_comp')  
    else:
        form = ProductoForm()
    
    grupo = request.user.groups.first()
    
    context = {
        'form': form,
        'grupo': grupo
    }
    return render(request,'inventario/productos/ingresar_producto.html', context)

@login_required(login_url='login')
def editar_producto(request, producto_id):

    producto = get_object_or_404(Producto, producto_id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('/crud_producto')  
    else:
        form = ProductoForm(instance=producto)
    
    grupo = request.user.groups.first()
    
    context = {
        'form': form,
        'grupo': grupo
    }

    return render(request, 'inventario/productos/editar_producto.html', context)

@login_required(login_url='login')
def eliminar_producto(request, producto_id):

    producto = get_object_or_404(Producto, producto_id=producto_id)
    if request.method == 'POST':
        producto.delete()
        return redirect('/crud_producto')

    grupo = request.user.groups.first()
    
    context = {
        'producto': producto,
        'grupo': grupo
    }

    return render(request, 'inventario/productos/eliminar_producto.html', context)

##################################### METODOS PRODUCTO COPEC #####################################
@login_required(login_url='login')
def crud_producto_copec(request):

    productos = ProdCopec.objects.all()

    grupo = request.user.groups.first()
    
    context = {
        'productos': productos,
        'grupo': grupo
    }

    return render(request, 'inventario/prod_copec/crud_producto_copec.html', context) 

@login_required(login_url='login')
def ingresar_producto_copec(request):

    if request.method == 'POST':
        form = ProdCopecForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/crud_producto_copec')  
    else:
        form = ProdCopecForm()

    grupo = request.user.groups.first()
    
    context = {
        'form': form,
        'grupo': grupo
    }

    return render(request,'inventario/prod_copec/ingresar_producto_copec.html', context)

@login_required(login_url='login')
def editar_producto_copec(request, prod_copec_id):

    producto = get_object_or_404(ProdCopec, prod_copec_id=prod_copec_id)
    if request.method == 'POST':
        form = ProdCopecForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('/crud_producto_copec')  
    else:
        form = ProdCopecForm(instance=producto)

    grupo = request.user.groups.first()
    
    context = {
        'form': form,
        'grupo': grupo
    }

    return render(request, 'inventario/prod_copec/editar_producto_copec.html', context)

@login_required(login_url='login')
def eliminar_producto_copec(request, prod_copec_id):

    producto = get_object_or_404(ProdCopec, prod_copec_id=prod_copec_id)
    if request.method == 'POST':
        producto.delete()
        return redirect('/crud_producto_copec')
    
    grupo = request.user.groups.first()
    
    context = {
        'producto': producto,
        'grupo': grupo
    }

    return render(request, 'inventario/prod_copec/eliminar_producto_copec.html', context)

##################################### METODOS COMPOSICION #####################################
@login_required(login_url='login')
def crud_comp(request):
    
    producto_seleccionado = request.GET.get('producto', None)
    
    if producto_seleccionado:
        comps = CompProducto.objects.filter(producto__producto_nom = producto_seleccionado)
    else:
        comps = CompProducto.objects.none
    
    productos = CompProducto.objects.values_list('producto__producto_nom', flat=True).distinct()
    
    grupo = request.user.groups.first()
    
    context = {
        'comps': comps, 
        'productos': productos,
        'producto_seleccionado': producto_seleccionado,
        'grupo': grupo
    }

    return render(request,'inventario/comp_producto/crud_comp.html', context) 

@login_required(login_url='login')
def ingresar_comp(request):

    if request.method == 'POST':
        form = CompProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/crud_comp')  
    else:
        form = CompProductoForm()

    grupo = request.user.groups.first()
    
    context = {
        'form': form,
        'grupo': grupo
    }

    return render(request, 'inventario/comp_producto/ingresar_comp.html', context)

@login_required(login_url='login')
def editar_comp(request, comp_producto_id):

    composicion = get_object_or_404(CompProducto, comp_producto_id=comp_producto_id)
    if request.method == 'POST':
        form = CompProductoForm(request.POST, instance=composicion)
        if form.is_valid():
            form.save()
            return redirect('/crud_comp')  
    else:
        form = CompProductoForm(instance=composicion)

    grupo = request.user.groups.first()
    
    context = {
        'form': form,
        'grupo': grupo
    }

    return render(request, 'inventario/comp_producto/editar_comp.html', context)

@login_required(login_url='login')
def eliminar_comp(request, comp_producto_id):

    composicion = get_object_or_404(CompProducto, comp_producto_id=comp_producto_id)
    if request.method == 'POST':
        composicion.delete()
        return redirect('/crud_comp')
    
    context = {
        'composicion': composicion,
        'grupo': request.user.groups.first()
    }
    return render(request, 'inventario/comp_producto/eliminar_comp.html', context)

##################################### METODOS STOCK MP #####################################
@permission_required('inventario.can_access_crud_stock_mp', raise_exception=True)
@login_required(login_url='login')
def crud_stock_mp(request):

    context = {
        'grupo': request.user.groups.first(),
        'stockmps': StockAditivo.objects.all()
    }
    return render(request, 'inventario/stock_mp/crud_stock_mp.html', context) 

@login_required(login_url='login')
def ingresar_stock_mp(request):

    if request.method == 'POST':
        form = StockAditivoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/crud_stock_mp') 
    else:
        form = StockAditivoForm()
    
    context = {
        'form': form,
        'grupo': request.user.groups.first()
    }

    return render(request, 'inventario/stock_mp/ingresar_stock_mp.html', context)

@login_required(login_url='login')
def editar_stock_mp(request, stock_ad_id):

    stockmp = get_object_or_404(StockAditivo, stock_ad_id=stock_ad_id)
    if request.method == 'POST':
        form = StockAditivoForm(request.POST, instance=stockmp)
        if form.is_valid():
            form.save()
            return redirect('/crud_stock_mp')  
    else:
        form = StockAditivoForm(instance=stockmp)
    
    context = {
        'form': form,
        'grupo': request.user.groups.first()
    }

    return render(request, 'inventario/stock_mp/editar_stock_mp.html', context)

def agregar_stock_mp(request):
    if request.method == 'POST':
        cantidad = request.POST.get('cantidad_mp')
        stock_ad_id = request.POST.get('stock_ad_id')
        
        if not cantidad or not stock_ad_id:
            return HttpResponse('Parámetros incompletos', status=400)    
        
        try:
            cantidad = Decimal(cantidad)
            stock_ad_id = int(stock_ad_id)
            aumentar_stock_mp(stock_ad_id, cantidad)
            return redirect('/crud_stock_mp')
        except ValueError as e:            
            return HttpResponse(str(e), status=400)
    
    return HttpResponse('Método no permitido', status=405)

##################################### METODOS STOCK PRODUCTOS #####################################
@login_required(login_url='login')
def crud_stock_prod(request):

    stockprods = StockProducto.objects.all()

    context = {
        'stockprods': stockprods,
        'grupo': request.user.groups.first()
    }

    return render(request, 'inventario/stock_producto/crud_stock_prod.html', context) 

@login_required(login_url='login')
def ingresar_stock_prod(request):

    if request.method == 'POST':
        form = StockProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/crud_stock_prod')  
    else:
        form = StockProductoForm()

    context = {
        'form': form,
        'grupo': request.user.groups.first()
    }

    return render(request, 'inventario/stock_producto/ingresar_stock_prod.html', context)

@login_required(login_url='login')
def editar_stock_prod(request, stock_producto_id):

    stockprod = get_object_or_404(StockProducto, stock_producto_id=stock_producto_id)
    if request.method == 'POST':
        form = StockProductoForm(request.POST, instance=stockprod)
        if form.is_valid():
            form.save()
            return redirect('/crud_stock_prod')  
    else:
        form = StockProductoForm(instance=stockprod)
    
    context = {
        'form': form,
        'grupo': request.user.groups.first()
    }

    return render(request, 'inventario/stock_producto/editar_stock_prod.html', context)

##################################### METODOS STOCK INSUMO #####################################
@permission_required('inventario.can_access_crud_stock_insumo', raise_exception=True)
@login_required(login_url='login')
def crud_stock_insumo(request):
    context = {
        'grupo': request.user.groups.first(),
        'stockinsus': StockInsumo.objects.all()
    }
    return render(request, 'inventario/stock_insumo/crud_stock_insumo.html', context) 

@login_required(login_url='login')
def ingresar_stock_insumo(request):

    if request.method == 'POST':
        form = StockInsumoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/crud_stock_insumo') 
    else:
        form = StockInsumoForm()
    
    context = {
        'form': form,
        'grupo': request.user.groups.first()
    }

    return render(request, 'inventario/stock_insumo/ingresar_stock_insumo.html', context)

@login_required(login_url='login')
def editar_stock_insumo(request, stock_in_id):

    stockinsu = get_object_or_404(StockInsumo, stock_in_id=stock_in_id)
    if request.method == 'POST':
        form = StockInsumoForm(request.POST, instance=stockinsu)
        if form.is_valid():
            form.save()
            return redirect('/crud_stock_insumo')  
    else:
        form = StockInsumoForm(instance=stockinsu)

    context = {
        'form': form,
        'grupo': request.user.groups.first()
    }

    return render(request, 'inventario/stock_insumo/editar_stock_insumo.html', context)

def agregar_stock_insumo(request):
    if request.method == 'POST':
        cantidad = request.POST.get('cantidad_insumo')
        stock_in_id = request.POST.get('stock_in_id')
        
        if not cantidad or not stock_in_id:
            return HttpResponse('Parámetros incompletos', status=400)    
        
        try:
            cantidad = Decimal(cantidad)
            stock_in_id = int(stock_in_id)
            aumentar_stock_insumo(stock_in_id, cantidad)
            return redirect('/crud_stock_insumo')
        except ValueError as e:            
            return HttpResponse(str(e), status=400)
    
    return HttpResponse('Método no permitido', status=405)

###################################################################################################################

@login_required(login_url='login')
@permission_required('inventario.can_access_crud_orden_prod', raise_exception=True)
def cruds(request):
    context = {
        'grupo': request.user.groups.first()
    }
    return render(request, 'cruds.html', context)

########################################## METODOS ORDEN PRODUCCION ################################################

@login_required(login_url='login')
@permission_required('inventario.can_access_crud_orden_prod', raise_exception=True)
def crud_orden_prod(request):
    
    sort_by = request.GET.get('sort_by', 'lote_prod_id')
    direction = request.GET.get('direction', 'asc')

    if direction == 'desc':
        sort_by = '-' + sort_by   
    odps = LoteProd.objects.all().order_by(sort_by)

    context = {
        'odps': odps,
        'sort_by': sort_by.strip('-'), 
        'direction': direction,
        'grupo': request.user.groups.first()
    }

    return render(request,'ventanas_prod/orden_prod/crud_orden_prod.html', context) 

@login_required(login_url='login')
def ingresar_orden_prod(request):

    if request.method == 'POST':
        form = OdpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/crud_orden_prod') 
    else:
        form = OdpForm()
    
    context = {
        'form': form,
        'grupo': request.user.groups.first()
    }

    return render(request, 'ventanas_prod/orden_prod/ingresar_orden_prod.html', context)

@login_required(login_url='login')
def editar_orden_prod(request, lote_prod_id):
    odp = get_object_or_404(LoteProd, lote_prod_id=lote_prod_id)
    if request.method == 'POST':
        form = OdpForm(request.POST, instance=odp)
        if form.is_valid():            
            form.save()
            return redirect('/crud_orden_prod')  
    else:
        form = OdpForm(instance=odp)
    
    context = {
        'form': form,
        'grupo': request.user.groups.first()
    }

    return render(request, 'ventanas_prod/orden_prod/editar_orden_prod.html', context)

@login_required(login_url='login')
def eliminar_orden_prod(request, lote_prod_id):

    odp = get_object_or_404(LoteProd, lote_prod_id=lote_prod_id)
    if request.method == 'POST':
        odp.delete()
        return redirect('/crud_orden_prod')

    context = {
        'odp': odp,
        'grupo': request.user.groups.first()
    }

    return render(request, 'ventanas_prod/orden_prod/eliminar_orden_prod.html', context)
########################################## METODOS CALIDAD ################################################

@login_required(login_url='login')
@permission_required('inventario.can_access_crud_calidad', raise_exception=True)
def crud_calidad(request):

    sort_by = request.GET.get('sort_by', 'lote_prod_id')
    direction = request.GET.get('direction', 'asc')

    if direction == 'desc':
        sort_by = '-' + sort_by

    odps = LoteProd.objects.all().order_by(sort_by)
    
    context = {
        'odps': odps,
        'sort_by': sort_by.strip('-'),
        'direction': direction,
        'grupo': request.user.groups.first()
    }

    return render(request,'ventanas_prod/analisis_calidad/crud_calidad.html', context) 

@login_required(login_url='login')
def editar_calidad(request, lote_prod_id):
    odp = get_object_or_404(LoteProd, lote_prod_id=lote_prod_id)
    if request.method == 'POST':
        form = CalidadForm(request.POST, instance=odp)
        if form.is_valid():
            form.save()
            return redirect('/crud_calidad')
    else:
        form = CalidadForm(instance=odp)
    
    context = {
        'form': form,
        'grupo': request.user.groups.first()
    }

    return render(request, 'ventanas_prod/analisis_calidad/editar_calidad.html', context)

@login_required(login_url='login')
def confirmar_prod_calidad(request, lote_prod_id):
    odp = get_object_or_404(LoteProd, lote_prod_id=lote_prod_id)

    # Aquí obtén los valores necesarios, por ejemplo:
    prod_copec_id = odp.prod_copec.prod_copec_id
    volumen_odp = odp.volumen_odp    
    # Llama a la función agregar_stock con los parámetros necesarios
    try:
        agregar_stock(prod_copec_id, volumen_odp, lote_prod_id)
        return redirect('/crud_calidad')
    except ValueError as e:
        raise ValueError(e)

########################################## METODOS INVENTARIO BODEGA ################################################
@login_required(login_url='login')
@permission_required('inventario.can_access_crud_despacho', raise_exception=True)
def crud_inv_bodega(request):

    desps = Despacho.objects.all()

    context = {
        'desps': desps,
        'grupo': request.user.groups.first()
    }

    return render(request, 'ventanas_prod/inventario_bodega/crud_inv_bodega.html', context)

########################################## METODOS DESPACHO #########################################################
@login_required(login_url='login')
@permission_required('inventario.can_access_crud_despacho', raise_exception=True)
def crud_despacho(request):

    sort_by = request.GET.get('sort_by', 'despacho_id')
    direction = request.GET.get('direction', 'asc')
    
    if direction == 'desc':
        sort_by = '-' + sort_by

    desps = Despacho.objects.all().order_by(sort_by)
    
    context = {
        'desps': desps,      
        'sort_by': sort_by.strip('-'),
        'direction': direction,        
        'grupo': request.user.groups.first()
    }

    return render(request, 'ventanas_prod/despacho_bodega/crud_despacho.html', context) 

@login_required(login_url='login')
def crud_lote_desp(request):

    sort_by = request.GET.get('sort_by', 'lote_prod_id')
    direction = request.GET.get('direction', 'asc')

    if direction == 'desc':
        sort_by = '-' + sort_by

    odps = LoteProd.objects.all().order_by(sort_by)    

    context = {
        'odps': odps,
        'sort_by': sort_by.strip('-'), 
        'direction': direction,
        'grupo': request.user.groups.first()
    }

    return render(request, 'ventanas_prod/despacho_bodega/crud_lote_desp.html', context)

@login_required(login_url='login')
def ingresar_despacho(request):
    if request.method == 'POST':
        cantidad = request.POST.get('cantidad_despachar')
        lote_id = request.POST.get('lote_id')
        
        if not cantidad or not lote_id:
            return HttpResponse('Parámetros incompletos', status=400)    
        
        try:
            cantidad = Decimal(cantidad)
            lote_id = int(lote_id)
            generar_despacho(lote_id, cantidad)
            return redirect('/crud_despacho')
        except ValueError as e:            
            return HttpResponse(str(e), status=400)
    
    return HttpResponse('Método no permitido', status=405)

@login_required(login_url='login')
def confirmar_despacho(request, despacho_id):
 
    # Llama a la función agregar_stock con los parámetros necesarios
    try:
        despachar(despacho_id)
        return redirect('/crud_despacho')
    except ValueError as e:
        raise ValueError(e)


########################################## METODOS GUIAS DESPACHO ###################################################
@login_required(login_url='login')
@permission_required('inventario.can_access_crud_guias_despacho', raise_exception=True)
def crud_guia_despacho(request):

    sort_by = request.GET.get('sort_by', 'despacho_id')
    direction = request.GET.get('direction', 'asc')
    
    if direction == 'desc':
        sort_by = '-' + sort_by

    desps = Despacho.objects.all().order_by(sort_by)
    
    context = {
        'desps': desps,      
        'sort_by': sort_by.strip('-'),
        'direction': direction,        
        'grupo': request.user.groups.first()
    }

    return render(request, 'ventanas_prod/guias_despacho/crud_guia_despacho.html', context)

@login_required(login_url='login')
def editar_guia_despacho(request, despacho_id):
    try:
        actualizar_despacho(despacho_id)
    except ValueError as e:
        return HttpResponse(str(e), status=400)
    
    desp = get_object_or_404(Despacho, despacho_id=despacho_id)
    if request.method == 'POST':
        form = GuiaDespachoForm(request.POST, instance=desp)
        if form.is_valid():                        
            form.save()
            return redirect('/crud_guia_despacho')
            
    else:
        form = GuiaDespachoForm(instance=desp)
    
    context = {
        'form': form,
        'grupo': request.user.groups.first()
    }

    return render(request, 'ventanas_prod/guias_despacho/editar_guia_despacho.html', context)


########################################## METODOS REPORTE DIARIO ################################################
@login_required(login_url='login')
@permission_required('inventario.can_access_crud_despacho', raise_exception=True)
def crud_reporte(request):

    sort_by = request.GET.get('sort_by', 'fecha_despacho')
    direction = request.GET.get('direction', 'asc')
    
    if direction == 'desc':
        sort_by = '-' + sort_by
    
    despachos = Despacho.objects.all().order_by(sort_by)
    
    context = {
        'desps': despachos,
        'sort_by': sort_by.strip('-'),
        'direction': direction,
        'grupo': request.user.groups.first()
    }


    return render(request, 'ventanas_prod/reporte/crud_reporte.html', context)

def eliminar_reporte(request, despacho_id):
    
    desp = get_object_or_404(Despacho, despacho_id=despacho_id)
    if request.method == 'POST':
        desp.delete()
        return redirect('/crud_reporte')

    context = {
        'desp': desp,
        'grupo': request.user.groups.first()
    }

    return render(request, 'ventanas_prod/reporte/eliminar_reporte.html', context)


########################################## METODOS CERTIFICADO ######################################################

@login_required(login_url='login')
def gen_certificado(request, lote_prod_id):
    # Obtener el objeto correspondiente al lote_prod_id
    odp = get_object_or_404(LoteProd, lote_prod_id=lote_prod_id)
    fecha = datetime.date.today()
    template_path = 'ventanas_prod/orden_prod/gen_certificado.html'

    context = {'odp': odp, 'fecha': fecha}

    # Crear una respuesta HTTP con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificado_{lote_prod_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    # Convertir el HTML a PDF usando xhtml2pdf
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Verificar si hubo algún error
    if pisa_status.err:
        return HttpResponse('Ocurrió un error al generar el PDF', status=500)
        
    return response

"""

@login_required(login_url='login')
def gen_certificado(request, lote_prod_id):
    # Obtener el objeto correspondiente al lote_prod_id
    odp = get_object_or_404(LoteProd, lote_prod_id=lote_prod_id)
    
    # Renderizar el HTML a una cadena
    html = render_to_string('ventanas_prod/orden_prod/gen_certificado.html', {'odp': odp})

    # Crear una respuesta HTTP con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificado_{lote_prod_id}.pdf"'

    # Convertir el HTML a PDF usando xhtml2pdf
    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)

    # Verificar si hubo algún error
    if pisa_status.err:
        return HttpResponse('Ocurrió un error al generar el PDF', status=500)
        
    return response


"""