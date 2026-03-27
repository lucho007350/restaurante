from django.contrib import admin
from .models import Categoria, Producto, Cliente, Pedido, DetallePedido, Carrito, ItemCarrito, PreferenciasUsuario

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'ver_imagen', 'disponible', 'promocion')
    list_filter = ('categoria', 'disponible', 'promocion')
    search_fields = ('nombre', 'descripcion')
    
    def ver_imagen(self, obj):
        if obj.imagen:
            return f'<img src="{obj.imagen.url}" width="50" height="50" style="object-fit: cover; border-radius: 5px;">'
        return "📷 Sin imagen"
    ver_imagen.allow_tags = True
    ver_imagen.short_description = 'Imagen'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'precio', 'categoria')
        }),
        ('Imagen del Producto', {
            'fields': ('imagen',),
            'description': 'Sube una imagen real del producto (recomendado: 500x500px)',
        }),
        ('Disponibilidad', {
            'fields': ('disponible', 'promocion'),
        }),
        ('Características Adicionales', {
            'fields': ('es_nuevo', 'es_mas_vendido', 'es_vegetariano', 'es_sin_gluten'),
            'classes': ('collapse',),  # Para que aparezca colapsado
        }),
    )

# ============================================
# REGISTRO DE MODELOS
# ============================================
admin.site.register(Categoria)
admin.site.register(Producto, ProductoAdmin)  
admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(DetallePedido)

admin.site.register(Carrito)
admin.site.register(ItemCarrito)
admin.site.register(PreferenciasUsuario)