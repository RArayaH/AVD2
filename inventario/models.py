#"""
from django.conf import settings
from django.db import models 
from django.contrib.auth.models import User #AbstractBaseUser, BaseUserManager
import datetime
from auditlog.registry import auditlog


# Create your models here.   

class Insumo(models.Model):
    insumo_id = models.AutoField(primary_key=True)
    insumo_nom = models.CharField(max_length=60, blank=True, null=True)    
    insumo_vol = models.DecimalField(max_digits=6, decimal_places=1)
    insumo_env_por_caja = models.DecimalField(max_digits=5, decimal_places=1)
    insumo_cajas_por_pallet = models.DecimalField(max_digits=5, decimal_places=1)
    insumo_desc = models.CharField(max_length=150, blank=True, null=True)
    def __str__(self):
        return self.insumo_nom

class InfoAditivo(models.Model):
    adtv_id = models.AutoField(primary_key=True)
    adtv_nom = models.CharField(max_length=60, blank=True, null=True, unique=True)
    adtv_dens = models.DecimalField(max_digits=6, decimal_places=5, default=0.0)
    def __str__(self):
        return self.adtv_nom    

class Producto(models.Model):
    producto_id = models.AutoField(primary_key=True)
    producto_nom = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.producto_nom

class CompProducto(models.Model):
    comp_producto_id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    info_aditivo = models.ForeignKey(InfoAditivo, on_delete=models.CASCADE)
    pp = models.DecimalField(max_digits=6, decimal_places=5)
    vv = models.DecimalField(max_digits=6, decimal_places=5, default=1.00000)
    def __str__(self):
        return self.producto.producto_nom

class ProdCopec(models.Model):
    prod_copec_id = models.AutoField(primary_key=True)
    prod_copec_cod = models.CharField(max_length=60, blank=True, null=True)
    prod_copec_nom = models.CharField(max_length=60, blank=True, null=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    def __str__(self):
        return self.prod_copec_nom


class StockAditivo(models.Model):
    stock_ad_id = models.AutoField(primary_key=True)
    nomAditivo = models.ForeignKey(InfoAditivo, on_delete=models.CASCADE, unique=True)
    stock_ad_cant_lt = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        permissions = [
            ("can_access_crud_stock_mp", "Can access crud_stock_mp view")
        ]

class StockProducto(models.Model):
    stock_producto_id = models.AutoField(primary_key=True)
    prod_copec = models.ForeignKey(ProdCopec, on_delete=models.CASCADE)
    stock_prod_cant_vol = models.DecimalField(max_digits=10, decimal_places=2)
    stock_prod_cant_uni = models.DecimalField(max_digits=10, decimal_places=2)

class StockInsumo(models.Model):
    stock_in_id = models.AutoField(primary_key=True)
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    stock_in_cant_unit = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        permissions = [
            ("can_access_crud_stock_insumo", "Can access crud_stock_insumo view")
        ]

class LoteProd(models.Model):
    lote_prod_id = models.AutoField(primary_key=True)
    lote_prod_fecha = models.DateField(default=datetime.date.today, auto_now_add=False)
    prod_copec = models.ForeignKey(ProdCopec, on_delete=models.CASCADE)
    volumen_odp = models.DecimalField(max_digits=10, decimal_places=2)
    volumen_prod = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cant_prod = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    tk_agua = models.CharField(max_length=5, default = 'N/A', null=False)
    tk_prod = models.CharField(max_length=5, default = 'N/A', null=False)
    lote_mp = models.CharField(max_length=50, default = 'N/A', null=False)
    fecha_ven_mp = models.DateField(default=datetime.date.today)
    lote_colorante = models.CharField(max_length=10, default = 'N/A', null=False)
    fecha_ven_colorante = models.DateField(default=datetime.date.today)
    lote_aromatizante = models.CharField(max_length=10, default = 'N/A', null=False)
    fecha_ven_aromatizante = models.DateField(default=datetime.date.today)
    num_pedido = models.CharField(max_length=10, default = 'N/A', null=False)
    lote_asr = models.CharField(max_length=10, default = 'N/A', null=False)
    fecha_ven_asr = models.DateField(default=datetime.date.today)
    freezing_point = models.CharField(max_length=6, default = 'N/A', null=False)
    ph = models.CharField(max_length=6, default = 'N/A', null=False)
    glicol = models.CharField(max_length=6, default = 'N/A', null=False)
    color = models.CharField(max_length=10, default = 'N/A', null=False)
    olor = models.CharField(max_length=10, default = 'N/A', null=False)
    apariencia = models.CharField(max_length=10, default = 'N/A', null=False)
    sellos_tapas = models.CharField(max_length=10, default = 'N/A', null=False)
    valvulas = models.CharField(max_length=10, default = 'N/A', null=False)
    estado_aceptado = models.CharField(max_length=100, default = 'N/A', null=False)
    estado_produccion = models.CharField(max_length=100, default='PENDIENTE', null=False)    
    patente = models.CharField(max_length=8, default = 'N/A', null=False)
    cliente = models.CharField(max_length=50, default = 'COPEC', null=False)

    class Meta:
        permissions = [
            ("can_access_crud_orden_prod", "Can access crud_orden_prod view"),
            ("can_access_crud_calidad", "Can access crud_calidad view"),
            ("can_access_crud_lote_desp", "Can access crud_lote_desp view")
        ]

class Despacho(models.Model):
    despacho_id = models.AutoField(primary_key=True)
    lote = models.ForeignKey(LoteProd, on_delete=models.CASCADE)
    fecha_despacho = models.DateField(default=datetime.date.today, auto_now_add=False)
    tipo_despacho = models.CharField(max_length=50, default = 'PENDIENTE GUIA DESPACHO', null=False)     
    cant_despacho = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    guia_despacho = models.IntegerField(default=0, null=False)

    class Meta:
        permissions = [
            ("can_access_crud_guias_despacho", "Can access crud_guias_despacho view"),
            ("can_access_crud_despacho", "Can access crud_despacho view")
        ]

auditlog.register(Insumo)
auditlog.register(InfoAditivo)
auditlog.register(Producto)
auditlog.register(CompProducto)
auditlog.register(ProdCopec)
auditlog.register(StockAditivo)
auditlog.register(StockProducto)
auditlog.register(StockInsumo)
auditlog.register(LoteProd)
auditlog.register(Despacho)
auditlog.register(User)
"""


###################################### ESTO NO SIRVE (...POR AHORA) #############################################

#class StockProducto(models.Model):
#    stock_producto_id = models.AutoField(primary_key=True)
#    comp_producto = models.ForeignKey(CompProducto, on_delete=models.CASCADE)
#    stock_prod_cant = models.DecimalField(max_digits=10, decimal_places=2)#

#    def __str__(self):
#        return f'{self.comp_producto.productos.productos_nom} - {self.cantidad}'

#class Mezcla(models.Model):
#    mezcla_id = models.AutoField(primary_key=True)
#    info_aditivo = models.ForeignKey(InfoAditivo, on_delete=models.CASCADE)
#    pp = models.DecimalField(max_digits=5, decimal_places=2)
#    vv = models.DecimalField(max_digits=5, decimal_places=2)

#class Olor(models.Model):
#    olor_id = models.AutoField(primary_key=True)
#    olor_nombre = models.CharField(max_length=10)

#class Ph(models.Model):
#    id_rang_ph = models.AutoField(primary_key=True)
#    ph_min = models.DecimalField(max_digits=3, decimal_places=1)
#    ph_max = models.DecimalField(max_digits=3, decimal_places=1)

# Define también los modelos Apariencia y Color si tienes los detalles.
#class Apariencia(models.Model):
#    id_apar = models.AutoField(primary_key=True)
#    descripcion = models.CharField(max_length=100)

#class Color(models.Model):
#    id_color = models.AutoField(primary_key=True)
#    descripcion = models.CharField(max_length=100)

#class Glicol(models.Model):
#    glicol_rang_id = models.AutoField(primary_key=True)
#    min_glicol = models.IntegerField()
#    max_glicol = models.IntegerField()

#class Producto(models.Model):
#    prod_id = models.AutoField(primary_key=True)
#    mezcla = models.ForeignKey(Mezcla, on_delete=models.CASCADE)
#    prod_nom = models.CharField(max_length=50)
#    prod_ph = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
#    ph = models.ForeignKey(Ph, on_delete=models.SET_NULL, null=True, blank=True)
#    apariencia = models.ForeignKey('Apariencia', on_delete=models.CASCADE)
#    color = models.ForeignKey('Color', on_delete=models.CASCADE)
#    olor = models.ForeignKey(Olor, on_delete=models.CASCADE)
#    prod_glicol = models.IntegerField(null=True, blank=True)
#    glicol_rang = models.ForeignKey(Glicol, on_delete=models.SET_NULL, null=True, blank=True)
#    prod_fp = models.IntegerField(null=True, blank=True)
#    prod_grav_esp = models.DecimalField(max_digits=5, decimal_places=5, null=True, blank=True)
#    prod_api = models.CharField(max_length=50, blank=True, null=True)
#    prod_tk_agua = models.IntegerField(null=True, blank=True)
#    prod_tk_prod = models.IntegerField(null=True, blank=True)   

"""

"""
class UsuarioManager(BaseUserManager):
	def create_user(self, email, username, nombres, apellidos,tipo_usuario, password=None):
		if not email:
			raise ValueError('El usuario debe tener un Correo Electrónico')

		usuario = self.model(
			username = username, 
			email = self.normalize_email(email), 
			nombres = nombres, 
			apellidos = apellidos,
            tipo_usuario = tipo_usuario
		)
        	
		usuario.set_password(password)
		usuario.save()
		return usuario

	def create_superuser(self, email, username, nombres, apellidos,tipo_usuario, password):
		usuario = self.create_user(
			email,
			username = username, 
			nombres = nombres, 
			apellidos = apellidos,
			password = password,
            tipo_usuario = tipo_usuario
		)
		
		usuario.usuario_administrador = True
		usuario.save()
		return usuario
	

class Usuario(AbstractBaseUser):
	username = models.CharField('Nombre de usuario', unique = True, max_length=100)
	email = models.EmailField('Correo Electronico', unique = True, max_length=254)
	nombres = models.CharField('Nombres', blank = True, max_length=200, null = True)
	apellidos = models.CharField('Apellidos', blank = True, max_length=200, null = True)
	#imagen = models.ImageField('Imagen de Perfil', upload_to='perfil/', height_field=None, width_field=None, max_length = 200, blank = True, null = True)
	usuario_activo = models.BooleanField(default=True)
	usuario_administrador = models.BooleanField(default=False)
	tipo_usuario = models.CharField('Tipo de Usuario', unique = True, max_length = 20, null = False, default = 'NA')
	objects = UsuarioManager()
	
	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['email', 'nombres', 'apellidos', 'tipo_usuario']

	def __str__(self):
		return f'Usuario {self.username},{self.apellidos}'

	def has_perm(self,perm,obj = None):
		return True

	def has_module_perms(self, app_label):
		return True

	@property
	def is_staff(self):
		return self.usuario_administrador

"""