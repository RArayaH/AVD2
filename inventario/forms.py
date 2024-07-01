#"""
from django import forms
from .models import InfoAditivo, Producto, CompProducto, StockAditivo, Insumo, ProdCopec, StockInsumo, StockProducto, LoteProd, User, Despacho
from django.contrib.auth.models import User, Group


class UserForm(forms.ModelForm):
    groups = forms.ModelChoiceField(queryset=Group.objects.all(), required=True)
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User
        widgets = {
            'password': forms.PasswordInput(),
        }
        fields = ['username','password','email','first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            user.groups.set([self.cleaned_data['groups']])
        return user

class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ['insumo_nom', 'insumo_vol', 'insumo_env_por_caja', 'insumo_cajas_por_pallet', 'insumo_desc']
        labels = {
            'insumo_nom': 'Nombre de insumo',            
            'insumo_vol': 'Volumen en Litros',
            'insumo_env_por_caja': 'Cantidad de envases por caja',
            'insumo_cajas_por_pallet': 'Cantidad de cajas por pallet',
            'insumo_desc': 'Descripción'
        }

class InfoAditivoForm(forms.ModelForm):
    class Meta:
        model = InfoAditivo
        fields = ['adtv_nom','adtv_dens']  
        labels = {
            'adtv_nom': 'Nombre de la materia prima',
            'adtv_dens': 'Densidad',            
        }

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['producto_nom']
        labels = {
            'producto_nom': 'Nombre del Producto',           
        }
    
class CompProductoForm(forms.ModelForm):
    class Meta:
        model = CompProducto
        fields = ['producto', 'info_aditivo', 'pp', 'vv']
        labels = {
            'producto': 'Nombre del Producto',
            'info_aditivo': 'Nombre del Aditivo', 
            'pp': 'Porcentaje Peso Peso', 
            'vv': 'Porcentaje Volumen Volumen'
        }

class ProdCopecForm(forms.ModelForm):
    class Meta:
        model = ProdCopec
        fields = ['prod_copec_cod','prod_copec_nom','producto', 'insumo']
        labels = {
            'prod_copec_cod':'Codigo de producto COPEC',
            'prod_copec_nom':'Nombre de producto COPEC',
            'producto': 'Nombre del Producto',
            'insumo': 'Nombre del Insumo'
        }

class StockAditivoForm(forms.ModelForm):
    class Meta:
        model = StockAditivo
        fields = ['nomAditivo', 'stock_ad_cant_lt']
        labels = {
            'nomAditivo': 'Nombre del Aditivo',
            'stock_ad_cant_lt': 'Cantidad del Aditivo'  
        }

class StockProductoForm(forms.ModelForm):
    class Meta:
        model = StockProducto
        fields = ['prod_copec', 'stock_prod_cant_vol','stock_prod_cant_uni']
        labels = {            
            'prod_copec': 'Nombre del producto COPEC',
            'stock_prod_cant_vol': 'Cantidad de litros de Producto',
            'stock_prod_cant_uni': 'Cantidad de unidades de Producto'  
        }

class StockInsumoForm(forms.ModelForm):
    class Meta:
        model = StockInsumo
        fields = ['insumo', 'stock_in_cant_unit']
        labels = {            
            'insumo': 'Nombre del Insumo',
            'stock_in_cant_unit': 'Cantidad del Insumo'  
        }

class OdpForm(forms.ModelForm):
    class Meta:
        model = LoteProd
        fields = ['lote_prod_fecha', 'prod_copec','volumen_odp', 'cliente']
        labels = {
            'lote_prod_fecha': 'Fecha de Planificacion', 
            'prod_copec': 'Producto Copec',
            'volumen_odp': 'Volumen [LT]',
            'cliente': 'Cliente'
        }

class CalidadForm(forms.ModelForm):
    class Meta:
        model = LoteProd
        fields = ['tk_agua',
                  'tk_prod', 
                  'lote_mp', 
                  'fecha_ven_mp',
                  'lote_colorante', 
                  'fecha_ven_colorante', 
                  'lote_aromatizante', 
                  'fecha_ven_aromatizante', 
                  'num_pedido', 
                  'lote_asr', 
                  'fecha_ven_asr',
                  'freezing_point',
                  'ph',
                  'glicol',
                  'color',
                  'olor',
                  'apariencia',
                  'sellos_tapas',
                  'valvulas'
                ]
        labels = { 
            'tk_agua':'TK de Agua',
            'tk_prod':'TK de Producto', 
            'lote_mp':'Lote de Aditivo', 
            'fecha_ven_mp':'Fecha de vencimiento de Aditivo',      
            'lote_colorante':'Lote de Colorante',       
            'fecha_ven_colorante':'Fecha de vencimiento de Colorante', 
            'lote_aromatizante':'Lote de Aromatizante', 
            'fecha_ven_aromatizante':'Fecha de vencimiento de Aromatizante', 
            'num_pedido':'Numero de Pedido', 
            'lote_asr':'Lote de ASR', 
            'fecha_ven_asr':'Fecha de vencimiento de ASR',
            'freezing_point':'Freezing Point del Producto',
            'ph':'pH del Producto',
            'glicol':'Porcentaje de Glicol del Producto',
            'color':'Color del Producto',
            'olor':'Olor del Producto',
            'apariencia':'Apariencia del Producto',
            'sellos_tapas':'Sellos/tapas',
            'valvulas':'Valvulas'                   
        }

class DespachoForm(forms.ModelForm):
    class Meta:
        model = Despacho
        fields = ['lote', 'fecha_despacho', 'cant_despacho']
        labels = {
            'lote': 'Lote', 
            'fecha_despacho': 'Fecha de Despacho',
            'cant_despacho': 'cant_despacho'
        }

class GuiaDespachoForm(forms.ModelForm):
    class Meta:
        model = Despacho
        fields = ['guia_despacho']
        labels = {
            'Guia de Despacho': 'guia_despacho'
        }
#"""