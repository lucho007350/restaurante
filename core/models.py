from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


# =========================
# Categorías (Ej: Bebidas, Hamburguesas, Postres)
# =========================
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# =========================
# Productos (La carta)
# =========================
class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    disponible = models.BooleanField(default=True)
    promocion = models.BooleanField(default=False)
    
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    
    # Otros campos que ya tienes
    es_nuevo = models.BooleanField(default=False)
    es_mas_vendido = models.BooleanField(default=False)
    es_vegetariano = models.BooleanField(default=False)
    es_sin_gluten = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre


# =========================
# Cliente (con sistema de puntos)
# =========================
class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    puntos = models.IntegerField(default=0)
    nivel = models.CharField(max_length=20, default='bronce', choices=[
        ('bronce', 'Bronce'),
        ('plata', 'Plata'),
        ('oro', 'Oro'),
        ('platino', 'Platino'),
    ])
    total_compras = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.usuario.username
    
    def actualizar_nivel(self):
        """Actualiza el nivel según los puntos"""
        if self.puntos >= 200:
            self.nivel = 'platino'
        elif self.puntos >= 150:
            self.nivel = 'oro'
        elif self.puntos >= 100:
            self.nivel = 'plata'
        else:
            self.nivel = 'bronce'
        self.save()
    
    def beneficio_actual(self):
        """Retorna el beneficio según el nivel"""
        beneficios = {
            'bronce': '🎁 5% de descuento en tu próxima compra',
            'plata': '🎁 10% de descuento + envío gratis',
            'oro': '🎁 15% de descuento + postre gratis',
            'platino': '🎁 20% de descuento + 2x1 en bebidas',
        }
        return beneficios.get(self.nivel, 'Sin beneficios')
    
    def descuento_nivel(self):
        """Retorna el porcentaje de descuento según el nivel"""
        descuentos = {
            'bronce': 5,
            'plata': 10,
            'oro': 15,
            'platino': 20,
        }
        return descuentos.get(self.nivel, 0)


# =========================
# Pedido
# =========================
class Pedido(models.Model):
    TIPOS = (
        ('local', 'En Restaurante'),
        ('domicilio', 'Domicilio'),
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    completado = models.BooleanField(default=False)

    def __str__(self):
        return f"Pedido {self.id}"


# =========================
# Detalle del pedido
# =========================
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.precio * self.cantidad


# =========================
# Carrito
# =========================
class Carrito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)

    def total(self):
        return sum(item.subtotal() for item in self.items.all())


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.producto.precio * self.cantidad
    

class PreferenciasUsuario(models.Model):
    TIPO_COMIDA = [
        ('entrada', 'Entradas'),
        ('postre', 'Postres'),
    ]

    # ✅ CORREGIDO: TIPO_BEBIDA con opciones correctas
    TIPO_BEBIDA = [
        ('caliente', 'Bebidas calientes'),
        ('fria', 'Bebidas frías'),
        ('ninguna', 'No me interesan las bebidas'),
    ]
    
    TIPO_PROTEINA = [
        ('carne', 'Carne de res'),
        ('pollo', 'Pollo'),
        ('pescado', 'Pescado'),
        ('mariscos', 'Mariscos'),
        ('vegetariano', 'Vegetariano'),
        ('ninguna', 'Sin preferencia'),
    ]
    
    RANGO_PRECIO = [
        ('economico', 'Económico ($0 - $15.000)'),
        ('medio', 'Medio ($15.000 - $30.000)'),
        ('alto', 'Alto ($30.000+)'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferencias')
    
    # Campos correctos
    tipo_comida = models.CharField(max_length=20, choices=TIPO_COMIDA, blank=True, null=True)
    tipo_bebida = models.CharField(max_length=20, choices=TIPO_BEBIDA, blank=True, null=True)
    tipo_proteina = models.CharField(max_length=20, choices=TIPO_PROTEINA, blank=True, null=True)
    rango_precio = models.CharField(max_length=20, choices=RANGO_PRECIO, blank=True, null=True)
    
    incluir_promociones = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferencias de {self.usuario.username}"
