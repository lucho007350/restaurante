"""
URL configuration for restaurante project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static  # ✅ IMPORTACIÓN CORRECTA

from core.views import (
    carta, carta_con_filtros, configurar_preferencias, hacer_pedido,
    historial_pedidos, registro, login_usuario, logout_usuario,
    ver_carrito, agregar_al_carrito, confirmar_pedido,
    aumentar_cantidad, disminuir_cantidad, eliminar_item,
    mis_beneficios, descargar_menu_pdf
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', carta, name='carta'),
    path('pedido/<int:producto_id>/', hacer_pedido, name='hacer_pedido'),
    path('preferencias/', configurar_preferencias, name='configurar_preferencias'),
    path('carta-filtrada/', carta_con_filtros, name='carta_con_filtros'),
    path('historial/', historial_pedidos, name='historial'),
    path('registro/', registro, name='registro'),
    path('login/', login_usuario, name='login'),
    path('logout/', logout_usuario, name='logout'),
    path('carrito/', ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', agregar_al_carrito, name='agregar_carrito'),
    path('confirmar/', confirmar_pedido, name='confirmar_pedido'),
    path('carrito/aumentar/<int:item_id>/', aumentar_cantidad, name='aumentar_cantidad'),
    path('carrito/disminuir/<int:item_id>/', disminuir_cantidad, name='disminuir_cantidad'),
    path('carrito/eliminar/<int:item_id>/', eliminar_item, name='eliminar_item'),
    path('beneficios/', mis_beneficios, name='mis_beneficios'),
    path('descargar-menu-pdf/', descargar_menu_pdf, name='descargar_menu_pdf'),
    
]

# ✅ Servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)