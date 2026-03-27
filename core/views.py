from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import HttpResponse
from decimal import Decimal
from datetime import datetime
import textwrap
import io
from django.db import models
from PIL import Image

from .models import Producto, Categoria, Cliente, Pedido, Carrito, ItemCarrito
from .models import PreferenciasUsuario

from .forms import RegistroForm, LoginForm
from .formsPreferencia import PreferenciasForm


from .models import (
    Producto, 
    Categoria, 
    Cliente, 
    Pedido, 
    Carrito, 
    ItemCarrito, 
    PreferenciasUsuario,
)
from .forms import RegistroForm, LoginForm


def carta(request):
    categoria_id = request.GET.get('categoria')
    buscar = request.GET.get('buscar')

    productos = Producto.objects.filter(disponible=True)

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    if buscar:
        productos = productos.filter(nombre__icontains=buscar)

    categorias = Categoria.objects.all()

    puntos = 0
    cliente = None
    if request.user.is_authenticated:
        cliente, creado = Cliente.objects.get_or_create(usuario=request.user)
        puntos = cliente.puntos

    # ✅ CREAR LA LISTA productos_con_precio CON LAS IMÁGENES
    productos_con_precio = []
    for producto in productos:
        precio_original = producto.precio
        precio_final = precio_original
        descuento_aplicado = 0
        
        if cliente and cliente.descuento_nivel() > 0:
            descuento_aplicado = cliente.descuento_nivel()
            descuento_decimal = Decimal(str(descuento_aplicado)) / Decimal('100')
            precio_final = precio_original * (Decimal('1') - descuento_decimal)
        
        # ✅ AQUÍ INCLUIMOS LA IMAGEN
        productos_con_precio.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio_original': precio_original,
            'precio_final': precio_final,
            'descuento': descuento_aplicado,
            'promocion': producto.promocion,
            'categoria': producto.categoria,
            'imagen': producto.imagen,  # ✅ IMPORTANTE: pasar el objeto imagen, no la URL
        })

    return render(request, 'carta.html', {
        'productos_con_precio': productos_con_precio,
        'categorias': categorias,
        'puntos': puntos,
        'cliente': cliente,
    })

    from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Pedido, Cliente

from django.contrib import messages

@login_required
def hacer_pedido(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    cliente, creado = Cliente.objects.get_or_create(usuario=request.user)

    # Calcular precio con descuento por nivel
    descuento = cliente.descuento_nivel()
    precio_final = producto.precio * (Decimal('1') - (Decimal(descuento) / Decimal('100')))
    
    # Aplicar descuento adicional por puntos si tiene más de 100
    descuento_puntos = False
    if cliente.puntos >= 100:
        precio_final = precio_final * Decimal('0.9')  # 10% extra
        cliente.puntos -= 100
        descuento_puntos = True

    # Crear pedido
    pedido = Pedido.objects.create(
        cliente=cliente,
        tipo='local',
        total=precio_final
    )

    # Calcular puntos ganados (1 punto por cada $1000)
    puntos_ganados = int(precio_final / 1000)
    cliente.puntos += puntos_ganados
    cliente.total_compras += precio_final
    cliente.actualizar_nivel()
    cliente.save()

    # Mensajes según beneficios aplicados
    messages.success(request, f"✅ Pedido realizado. Ganaste {puntos_ganados} puntos.")
    
    if descuento > 0:
        messages.info(request, f"🎉 Nivel {cliente.nivel.title()}: {descuento}% de descuento aplicado!")
    
    if descuento_puntos:
        messages.info(request, "✨ 10% extra por usar 100 puntos!")
    
    messages.info(request, f"🏆 Tu nivel actual: {cliente.nivel.title()} - {cliente.beneficio_actual()}")

    return redirect('carta')


    from django.contrib.auth.decorators import login_required

@login_required
def historial_pedidos(request):
    cliente, creado = Cliente.objects.get_or_create(usuario=request.user)
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha')

    return render(request, 'historial.html', {
        'pedidos': pedidos
    })




    from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import redirect

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            Cliente.objects.create(usuario=user)
            login(request, user)
            return redirect('configurar_preferencias')
    else:
        form = RegistroForm()

    return render(request, 'registro.html', {'form': form})


    from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

def login_usuario(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # ✅ SI ES SUPERUSUARIO, IR AL ADMIN
            if user.is_superuser:
                return redirect('/admin/')
            
            # ✅ VERIFICAR SI TIENE PREFERENCIAS
            try:
                preferencias = PreferenciasUsuario.objects.get(usuario=user)
                return redirect('carta_con_filtros')
            except PreferenciasUsuario.DoesNotExist:
                return redirect('configurar_preferencias')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


#     from django.contrib.auth import logout

# def logout_usuario(request):
#     logout(request)
#     return redirect('carta')



from django.contrib.auth import logout

def logout_usuario(request):
    logout(request)
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('login')
    return redirect('carta')



@login_required
def ver_carrito(request):
    # Obtener o crear carrito
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    
    # Obtener cliente de forma simple
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        # Si no existe, lo creamos
        cliente = Cliente.objects.create(
            usuario=request.user,
            puntos=0,
            nivel='bronce',
            total_compras=0
        )
    
    # Calcular subtotal (suma simple)
    subtotal = 0
    for item in carrito.items.all():
        subtotal += item.producto.precio * item.cantidad
    
    # Calcular descuento (si tiene nivel)
    descuento_porcentaje = 0
    if cliente.nivel == 'bronce':
        descuento_porcentaje = 5
    elif cliente.nivel == 'plata':
        descuento_porcentaje = 10
    elif cliente.nivel == 'oro':
        descuento_porcentaje = 15
    elif cliente.nivel == 'platino':
        descuento_porcentaje = 20
    
    # Calcular valores
    descuento_valor = (subtotal * descuento_porcentaje) / 100
    total_con_descuento = subtotal - descuento_valor
    
    # Puntos a ganar (1 punto cada $500)
    puntos_a_ganar = int(total_con_descuento / 500)
    
    return render(request, 'carrito.html', {
        'carrito': carrito,
        'cliente': cliente,
        'puntos': cliente.puntos,
        'subtotal': subtotal,
        'descuento': descuento_valor,
        'total_con_descuento': total_con_descuento,
        'puntos_a_ganar': puntos_a_ganar,
        'descuento_porcentaje': descuento_porcentaje,
    })

    from django.shortcuts import redirect, get_object_or_404
from .models import Producto

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)

    item, creado = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto
    )

    if not creado:
        item.cantidad += 1
        item.save()

    return redirect('carta')


from decimal import Decimal

@login_required
def confirmar_pedido(request):
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()

    if not items:
        return redirect('ver_carrito')

    # Obtener cliente
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        cliente = Cliente.objects.create(usuario=request.user, puntos=0, nivel='bronce', total_compras=0)
    
    # Calcular subtotal
    subtotal = 0
    for item in items:
        subtotal += item.producto.precio * item.cantidad
    
    # Calcular descuento por nivel
    descuento_porcentaje = 0
    if cliente.nivel == 'bronce':
        descuento_porcentaje = 5
    elif cliente.nivel == 'plata':
        descuento_porcentaje = 10
    elif cliente.nivel == 'oro':
        descuento_porcentaje = 15
    elif cliente.nivel == 'platino':
        descuento_porcentaje = 20
    
    # Total con descuento
    total_con_descuento = subtotal - ((subtotal * descuento_porcentaje) / 100)
    
    # Crear pedido
    pedido = Pedido.objects.create(
        cliente=cliente,
        tipo='local',
        total=total_con_descuento
    )
    
    # Calcular puntos ganados
    puntos_ganados = int(total_con_descuento / 500)
    cliente.puntos += puntos_ganados
    cliente.total_compras += total_con_descuento
    
    # Actualizar nivel si aplica
    if cliente.puntos >= 500:
        cliente.nivel = 'platino'
    elif cliente.puntos >= 250:
        cliente.nivel = 'oro'
    elif cliente.puntos >= 100:
        cliente.nivel = 'plata'
    
    cliente.save()
    
    # Vaciar carrito
    items.delete()
    
    messages.success(request, f"✅ Pedido confirmado. ¡Ganaste {puntos_ganados} puntos!")
    if descuento_porcentaje > 0:
        messages.info(request, f"🎉 Se aplicó {descuento_porcentaje}% de descuento por nivel {cliente.nivel}")
    
    return redirect('carta')

@login_required
def aumentar_cantidad(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.cantidad += 1
    item.save()
    return redirect('ver_carrito')


@login_required
def disminuir_cantidad(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)

    if item.cantidad > 1:
        item.cantidad -= 1
        item.save()
    else:
        item.delete()

    return redirect('ver_carrito')


@login_required
def eliminar_item(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    return redirect('ver_carrito')


@login_required
def configurar_preferencias(request):
    # Obtener o crear preferencias para el usuario
    preferencias, creado = PreferenciasUsuario.objects.get_or_create(usuario=request.user)
    
    # Obtener cliente para mostrar puntos y nivel
    cliente = get_object_or_404(Cliente, usuario=request.user)
    
    # Calcular progreso para siguiente nivel
    if cliente.nivel == 'bronce':
        puntos_necesarios = 100
        siguiente_nivel = {
            'nivel': 'Plata',
            'puntos_necesarios': max(puntos_necesarios - cliente.puntos, 0),
            'descuento': 10
        }
        progreso = min(int((cliente.puntos / puntos_necesarios) * 100), 100)
    elif cliente.nivel == 'plata':
        puntos_necesarios = 250
        siguiente_nivel = {
            'nivel': 'Oro',
            'puntos_necesarios': max(puntos_necesarios - cliente.puntos, 0),
            'descuento': 15
        }
        progreso = min(int((cliente.puntos / puntos_necesarios) * 100), 100)
    elif cliente.nivel == 'oro':
        puntos_necesarios = 500
        siguiente_nivel = {
            'nivel': 'Platino',
            'puntos_necesarios': max(puntos_necesarios - cliente.puntos, 0),
            'descuento': 20
        }
        progreso = min(int((cliente.puntos / puntos_necesarios) * 100), 100)
    else:
        siguiente_nivel = {
            'nivel': 'Máximo',
            'puntos_necesarios': 0,
            'descuento': 20
        }
        progreso = 100
    
    if request.method == 'POST':
        form = PreferenciasForm(request.POST, instance=preferencias)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Preferencias guardadas exitosamente!')
            return redirect('carta_con_filtros')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PreferenciasForm(instance=preferencias)
    
    return render(request, 'preferencias.html', {
        'form': form,
        'cliente': cliente,
        'puntos': cliente.puntos,
        'siguiente_nivel': siguiente_nivel,
        'progreso': progreso,
    })


@login_required
def carta_con_filtros(request):
    try:
        preferencias = PreferenciasUsuario.objects.get(usuario=request.user)
    except PreferenciasUsuario.DoesNotExist:
        return redirect('configurar_preferencias')
    
    cliente = get_object_or_404(Cliente, usuario=request.user)
    
    # Base de productos
    productos = Producto.objects.filter(disponible=True)
    
    # Aplicar filtros según preferencias
    
    # 1. FILTRO POR PROMOCIONES
    if preferencias.incluir_promociones:
        productos = productos.filter(promocion=True)
    
    # 2. FILTRO POR TIPO DE COMIDA
    if preferencias.tipo_comida:
        if preferencias.tipo_comida == 'entrada':
            productos = productos.filter(categoria__nombre__icontains='entrada')
        elif preferencias.tipo_comida == 'postre':
            productos = productos.filter(categoria__nombre__icontains='postre')
    
    # 3. FILTRO POR TIPO DE BEBIDA
    if preferencias.tipo_bebida and preferencias.tipo_bebida != 'ninguna':
        if preferencias.tipo_bebida == 'caliente':
            productos = productos.filter(
                models.Q(categoria__nombre__icontains='bebida caliente') |
                models.Q(nombre__icontains='café') |
                models.Q(nombre__icontains='té') |
                models.Q(nombre__icontains='chocolate') |
                models.Q(nombre__icontains='aromática')
            )
        elif preferencias.tipo_bebida == 'fria':
            productos = productos.filter(
                models.Q(categoria__nombre__icontains='bebida fría') |
                models.Q(nombre__icontains='jugo') |
                models.Q(nombre__icontains='gaseosa') |
                models.Q(nombre__icontains='limonada') |
                models.Q(nombre__icontains='malteada')|
                models.Q(nombre__icontains='Coca-cola')|
                models.Q(nombre__icontains='Pepsi')
            )
    
    # 4. FILTRO POR TIPO DE PROTEÍNA
    if preferencias.tipo_proteina and preferencias.tipo_proteina != 'ninguna':
        if preferencias.tipo_proteina == 'carne':
            productos = productos.filter(
                models.Q(descripcion__icontains='carne') |
                models.Q(nombre__icontains='carne') |
                models.Q(nombre__icontains='res') |
                models.Q(nombre__icontains='lomo') |
                models.Q(nombre__icontains='sobrebarriga')
            )
        elif preferencias.tipo_proteina == 'pollo':
            productos = productos.filter(
                models.Q(descripcion__icontains='pollo') |
                models.Q(nombre__icontains='pollo') |
                models.Q(nombre__icontains='pechuga') |
                models.Q(nombre__icontains='suprema')
            )
        elif preferencias.tipo_proteina == 'pescado':
            productos = productos.filter(
                models.Q(descripcion__icontains='pescado') |
                models.Q(nombre__icontains='pescado') |
                models.Q(nombre__icontains='mojarra') |
                models.Q(nombre__icontains='tilapia')
            )
        elif preferencias.tipo_proteina == 'mariscos':
            productos = productos.filter(
                models.Q(descripcion__icontains='mariscos') |
                models.Q(nombre__icontains='mariscos') |
                models.Q(nombre__icontains='camarón') |
                models.Q(nombre__icontains='pulpo') |
                models.Q(nombre__icontains='calamares')
            )
        elif preferencias.tipo_proteina == 'vegetariano':
            productos = productos.filter(es_vegetariano=True)
    
    # 5. FILTRO POR RANGO DE PRECIO
    if preferencias.rango_precio:
        if preferencias.rango_precio == 'economico':
            productos = productos.filter(precio__lte=15000)
        elif preferencias.rango_precio == 'medio':
            productos = productos.filter(precio__gte=15000, precio__lte=30000)
        elif preferencias.rango_precio == 'alto':
            productos = productos.filter(precio__gte=30000)
    
    # ✅ DEFINIR LA LISTA AQUÍ (FUERA DE CUALQUIER CONDICIÓN)
    productos_con_precio = []
    descuento_usuario = cliente.descuento_nivel()
    
    for producto in productos:
        precio_original = producto.precio
        precio_final = precio_original
        descuento_aplicado = 0
        
        if descuento_usuario > 0:
            descuento_aplicado = descuento_usuario
            descuento_decimal = Decimal(str(descuento_aplicado)) / Decimal('100')
            precio_final = precio_original * (Decimal('1') - descuento_decimal)
        
        productos_con_precio.append({
            'producto': producto,
            'precio_original': precio_original,
            'precio_final': precio_final,
            'descuento': descuento_aplicado,
            'imagen': producto.imagen.url if hasattr(producto, 'imagen') and producto.imagen else None
        })
    
    # Obtener todas las categorías
    categorias = Categoria.objects.all()
    
    # ✅ PASAR TODAS LAS VARIABLES AL TEMPLATE
    return render(request, 'cartaFiltrada.html', {
        'productos_con_precio': productos_con_precio,
        'categorias': categorias,
        'preferencias': preferencias,
        'cliente': cliente,
        'puntos': cliente.puntos,
    })
    

@login_required
def mis_beneficios(request):
    cliente = get_object_or_404(Cliente, usuario=request.user)
    
    # Calcular puntos para siguiente nivel
    if cliente.nivel == 'bronce':
        puntos_necesarios = 100
        siguiente_nivel = {
            'nivel': 'Plata',
            'puntos_necesarios': puntos_necesarios - cliente.puntos if cliente.puntos < puntos_necesarios else 0,
            'descuento': 10
        }
        # ✅ Calcular porcentaje aquí
        progreso = min(int((cliente.puntos / puntos_necesarios) * 100), 100)
        
    elif cliente.nivel == 'plata':
        puntos_necesarios = 250
        siguiente_nivel = {
            'nivel': 'Oro',
            'puntos_necesarios': puntos_necesarios - cliente.puntos if cliente.puntos < puntos_necesarios else 0,
            'descuento': 15
        }
        progreso = min(int((cliente.puntos / puntos_necesarios) * 100), 100)
        
    elif cliente.nivel == 'oro':
        puntos_necesarios = 500
        siguiente_nivel = {
            'nivel': 'Platino',
            'puntos_necesarios': puntos_necesarios - cliente.puntos if cliente.puntos < puntos_necesarios else 0,
            'descuento': 20
        }
        progreso = min(int((cliente.puntos / puntos_necesarios) * 100), 100)
        
    else:
        siguiente_nivel = {
            'nivel': 'Máximo',
            'puntos_necesarios': 0,
            'descuento': 20
        }
        progreso = 100
    
    return render(request, 'beneficios.html', {
        'cliente': cliente,
        'siguiente_nivel': siguiente_nivel,
        'progreso': progreso,  # ✅ Pasamos el progreso ya calculado
        'puntos': cliente.puntos,
    })


def _escape_pdf_text(texto):
    return str(texto).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def _paginar_items_menu(items):
    alto_maximo = 660
    alturas = {
        'resumen': 14,
        'categoria': 24,
        'producto': 18,
        'descripcion': 13,
        'espacio': 8,
        'vacio': 16,
    }

    paginas = []
    actual = []
    usado = 0

    for tipo, texto in items:
        alto = alturas.get(tipo, 14)
        if tipo == 'producto' and isinstance(texto, dict) and texto.get('imagen_path'):
            alto = 26
        if actual and usado + alto > alto_maximo:
            paginas.append(actual)
            actual = []
            usado = 0

        actual.append((tipo, texto))
        usado += alto

    if actual:
        paginas.append(actual)

    return paginas or [[('vacio', 'No hay productos disponibles en la carta.')]]


def _crear_pdf_simple(paginas, fecha_generacion, resumen):
    objetos = [None]

    def _agregar_objeto(contenido):
        objetos.append(contenido)
        return len(objetos) - 1

    catalogo_obj = _agregar_objeto(None)
    paginas_obj = _agregar_objeto(None)
    fuente_normal_obj = _agregar_objeto("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    fuente_titulo_obj = _agregar_objeto("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

    imagenes_cache = {}

    def _preparar_imagen_pdf(ruta_imagen, lado_maximo=24):
        with Image.open(ruta_imagen) as img:
            img = img.convert('RGB')
            ancho, alto = img.size
            if ancho <= 0 or alto <= 0:
                return None

            escala = min(lado_maximo / float(ancho), lado_maximo / float(alto), 1.0)
            nuevo_ancho = max(1, int(ancho * escala))
            nuevo_alto = max(1, int(alto * escala))

            if (nuevo_ancho, nuevo_alto) != (ancho, alto):
                resample = getattr(Image, 'Resampling', Image).LANCZOS
                img = img.resize((nuevo_ancho, nuevo_alto), resample)

            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=80, optimize=True)
            return buffer.getvalue(), nuevo_ancho, nuevo_alto

    def _registrar_imagen(ruta_imagen):
        if not ruta_imagen:
            return None
        if ruta_imagen in imagenes_cache:
            return imagenes_cache[ruta_imagen]

        try:
            imagen_procesada = _preparar_imagen_pdf(ruta_imagen)
        except Exception:
            return None

        if not imagen_procesada:
            return None

        imagen_bytes, ancho, alto = imagen_procesada
        nombre_imagen = f"Im{len(imagenes_cache) + 1}"
        stream_imagen = imagen_bytes.decode('latin-1')
        imagen_obj = _agregar_objeto(
            "<< /Type /XObject /Subtype /Image "
            f"/Width {ancho} /Height {alto} "
            "/ColorSpace /DeviceRGB /BitsPerComponent 8 "
            f"/Filter /DCTDecode /Length {len(imagen_bytes)} >>\n"
            f"stream\n{stream_imagen}\nendstream"
        )

        info = {
            'nombre': nombre_imagen,
            'obj': imagen_obj,
            'ancho': ancho,
            'alto': alto,
        }
        imagenes_cache[ruta_imagen] = info
        return info

    paginas_creadas = []

    for indice, items_pagina in enumerate(paginas, start=1):
        total_paginas = len(paginas)
        contenido = [
            "q",
            "0.97 0.98 1 rg",
            "0 0 595 842 re f",
            "Q",
            "q",
            "0.91 0.95 1 rg",
            "460 0 135 842 re f",
            "Q",
            "q",
            "0.12 0.25 0.45 rg",
            "0 776 595 66 re f",
            "Q",
            "BT",
            "1 1 1 rg",
            "/F2 20 Tf",
            "40 815 Td",
            "(Menu Actual - Restaurante Gourmet) Tj",
            "/F1 10 Tf",
            "0 -18 Td",
            f"(Generado: {_escape_pdf_text(fecha_generacion)}) Tj",
            "0 -14 Td",
            "(Menu dinamico del sistema) Tj",
            "0 0 0 rg",
            "ET",
        ]

        y = 748
        if indice == 1:
            contenido.extend([
                "q",
                "0.94 0.97 1 rg",
                "40 702 515 40 re f",
                "Q",
                "BT",
                "0.12 0.25 0.45 rg",
                "/F2 11 Tf",
                "48 727 Td",
                "(Resumen del menu) Tj",
                "/F1 10 Tf",
                "0 -14 Td",
                f"({_escape_pdf_text(resumen)}) Tj",
                "0 0 0 rg",
                "ET",
            ])
            y = 686

        fila_producto = 0
        imagenes_pagina = {}
        for tipo, texto in items_pagina:
            if tipo == 'resumen':
                contenido.extend([
                    "BT",
                    "0.25 0.25 0.25 rg",
                    "/F1 10 Tf",
                    f"46 {y} Td",
                    f"({_escape_pdf_text(texto)}) Tj",
                    "0 0 0 rg",
                    "ET",
                ])
                y -= 14
            elif tipo == 'categoria':
                contenido.extend([
                    "q",
                    "0.92 0.95 1 rg",
                    f"38 {y - 4} 520 18 re f",
                    "Q",
                    "q",
                    "0.15 0.35 0.65 rg",
                    f"38 {y - 4} 5 18 re f",
                    "Q",
                    "BT",
                    "0.12 0.25 0.45 rg",
                    "/F2 12 Tf",
                    f"44 {y + 1} Td",
                    f"({_escape_pdf_text(texto)}) Tj",
                    "0 0 0 rg",
                    "ET",
                ])
                y -= 24
            elif tipo == 'producto':
                datos_producto = texto if isinstance(texto, dict) else {'texto': str(texto), 'imagen_path': None}
                texto_producto = datos_producto.get('texto', '')
                imagen_info = _registrar_imagen(datos_producto.get('imagen_path'))

                x_texto = 46
                salto_producto = 16

                if fila_producto % 2 == 0:
                    contenido.extend([
                        "q",
                        "0.98 0.98 0.98 rg",
                        f"42 {y - 3} 510 14 re f",
                        "Q",
                    ])

                if imagen_info:
                    ancho_img = imagen_info['ancho']
                    alto_img = imagen_info['alto']
                    alto_dibujo = 20
                    ancho_dibujo = max(12, int((ancho_img / float(alto_img)) * alto_dibujo)) if alto_img else 20
                    x_img = 46
                    y_img = y - 15
                    x_texto = x_img + ancho_dibujo + 8
                    salto_producto = 24
                    imagenes_pagina[imagen_info['nombre']] = imagen_info['obj']

                    contenido.extend([
                        "q",
                        f"{ancho_dibujo} 0 0 {alto_dibujo} {x_img} {y_img} cm",
                        f"/{imagen_info['nombre']} Do",
                        "Q",
                    ])

                contenido.extend([
                    "BT",
                    "/F1 11 Tf",
                    f"{x_texto} {y} Td",
                    f"({_escape_pdf_text(texto_producto)}) Tj",
                    "ET",
                ])
                fila_producto += 1
                y -= salto_producto
            elif tipo == 'descripcion':
                contenido.extend([
                    "BT",
                    "0.35 0.35 0.35 rg",
                    "/F1 9 Tf",
                    f"54 {y} Td",
                    f"({_escape_pdf_text(texto)}) Tj",
                    "0 0 0 rg",
                    "ET",
                ])
                y -= 13
            elif tipo == 'vacio':
                contenido.extend([
                    "BT",
                    "/F1 12 Tf",
                    f"46 {y} Td",
                    f"({_escape_pdf_text(texto)}) Tj",
                    "ET",
                ])
                y -= 16
            else:
                y -= 8

        contenido.extend([
            "q",
            "0.82 0.82 0.82 RG",
            "1 w",
            "40 42 m 555 42 l S",
            "Q",
            "BT",
            "0.35 0.35 0.35 rg",
            "/F1 9 Tf",
            f"40 28 Td (Pagina {indice} de {total_paginas}) Tj",
            "430 0 Td",
            "(Gracias por preferirnos) Tj",
            "0 0 0 rg",
            "ET",
        ])

        contenido_txt = "\n".join(contenido)
        contenido_bytes = contenido_txt.encode('latin-1', errors='replace')
        objetos.append(
            f"<< /Length {len(contenido_bytes)} >>\nstream\n{contenido_txt}\nendstream"
        )
        contenido_obj = len(objetos) - 1

        xobjects = ''
        if imagenes_pagina:
            refs_xobjects = " ".join(
                f"/{nombre} {objeto} 0 R" for nombre, objeto in sorted(imagenes_pagina.items())
            )
            xobjects = f" /XObject << {refs_xobjects} >>"

        objetos.append(
            f"<< /Type /Page /Parent {paginas_obj} 0 R "
            "/MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 {fuente_normal_obj} 0 R /F2 {fuente_titulo_obj} 0 R >>{xobjects} >> "
            f"/Contents {contenido_obj} 0 R >>"
        )
        paginas_creadas.append(len(objetos) - 1)

    kids = " ".join(f"{num} 0 R" for num in paginas_creadas)
    objetos[paginas_obj] = f"<< /Type /Pages /Kids [{kids}] /Count {len(paginas_creadas)} >>"
    objetos[catalogo_obj] = f"<< /Type /Catalog /Pages {paginas_obj} 0 R >>"

    pdf = "%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets = [0]

    for idx in range(1, len(objetos)):
        offsets.append(len(pdf.encode('latin-1', errors='replace')))
        pdf += f"{idx} 0 obj\n{objetos[idx]}\nendobj\n"

    inicio_xref = len(pdf.encode('latin-1', errors='replace'))
    pdf += f"xref\n0 {len(objetos)}\n"
    pdf += "0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n"

    pdf += (
        f"trailer\n<< /Size {len(objetos)} /Root 1 0 R >>\n"
        f"startxref\n{inicio_xref}\n%%EOF"
    )

    return pdf.encode('latin-1', errors='replace')


def descargar_menu_pdf(request):
    productos = (
        Producto.objects.filter(disponible=True)
        .select_related('categoria')
        .order_by('categoria__nombre', 'nombre')
    )

    fecha_generacion = datetime.now().strftime('%d/%m/%Y %H:%M')
    items = []
    total_productos = productos.count()
    total_promociones = productos.filter(promocion=True).count()
    total_categorias = productos.values('categoria').distinct().count()
    resumen = (
        f"{total_productos} productos, {total_categorias} categorias, "
        f"{total_promociones} en promocion."
    )

    items.append(('resumen', f"Carta disponible al {fecha_generacion}"))
    items.append(('resumen', f"{total_productos} productos activos en el menu"))
    items.append(('espacio', ''))

    categoria_actual = None
    for producto in productos:
        nombre_categoria = " ".join(str(producto.categoria.nombre).split())
        if nombre_categoria != categoria_actual:
            items.append(('categoria', nombre_categoria.upper()))
            categoria_actual = nombre_categoria

        nombre_producto = " ".join(str(producto.nombre).split())
        precio = f"$ {int(producto.precio):,}".replace(',', '.')
        etiqueta_promo = "  [PROMOCION]" if producto.promocion else ""
        linea_producto = f"- {nombre_producto} - {precio}{etiqueta_promo}"
        ruta_imagen = None
        if hasattr(producto, 'imagen') and producto.imagen:
            try:
                ruta_imagen = producto.imagen.path
            except Exception:
                ruta_imagen = None

        lineas_producto = textwrap.wrap(linea_producto, width=64) or [linea_producto]
        for indice_linea, linea in enumerate(lineas_producto):
            items.append((
                'producto',
                {
                    'texto': linea,
                    'imagen_path': ruta_imagen if indice_linea == 0 else None,
                }
            ))

        if producto.descripcion:
            descripcion = " ".join(str(producto.descripcion).split())
            for linea in textwrap.wrap(descripcion, width=88)[:2]:
                items.append(('descripcion', linea))

        items.append(('espacio', ''))

    if not productos:
        items.append(('vacio', 'No hay productos disponibles en la carta.'))

    paginas = _paginar_items_menu(items)
    pdf_bytes = _crear_pdf_simple(paginas, fecha_generacion, resumen)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="menu_actual.pdf"'
    return response
