from django.test import TestCase
from django.contrib.auth.models import User
from .models import (
    Categoria, Producto, Cliente,
    Pedido, DetallePedido,
    Carrito, ItemCarrito,
    PreferenciasUsuario
)



class CategoriaTest(TestCase):

    def test_crear_categoria(self):
        categoria = Categoria.objects.create(nombre="Bebidas")
        self.assertEqual(categoria.nombre, "Bebidas")


class ProductoTest(TestCase):

    def test_crear_producto(self):
        categoria = Categoria.objects.create(nombre="Comida")

        producto = Producto.objects.create(
            nombre="Hamburguesa",
            descripcion="Rica hamburguesa",
            precio=15000,
            categoria=categoria
        )

        self.assertEqual(producto.nombre, "Hamburguesa")


class ClienteTest(TestCase):

    def test_crear_cliente(self):
        user = User.objects.create_user(username="luis", password="1234")

        cliente = Cliente.objects.create(usuario=user)

        self.assertEqual(cliente.usuario.username, "luis")





class ClienteNivelTest(TestCase):

    def test_actualizar_nivel(self):
        user = User.objects.create_user(username="ana", password="1234")

        cliente = Cliente.objects.create(usuario=user, puntos=120)

        cliente.actualizar_nivel()

        self.assertEqual(cliente.nivel, 'plata')





class ClienteBeneficioTest(TestCase):

    def test_beneficio(self):
        user = User.objects.create_user(username="carlos", password="1234")

        cliente = Cliente.objects.create(usuario=user, nivel='oro')

        beneficio = cliente.beneficio_actual()

        self.assertIn("15%", beneficio)


class PedidoTest(TestCase):

    def test_crear_pedido(self):
        user = User.objects.create_user(username="test", password="123")
        cliente = Cliente.objects.create(usuario=user)

        pedido = Pedido.objects.create(
            cliente=cliente,
            tipo='local',
            total=50000
        )

        self.assertEqual(pedido.total, 50000)






class DetallePedidoTest(TestCase):

    def test_subtotal(self):
        categoria = Categoria.objects.create(nombre="Comida")

        producto = Producto.objects.create(
            nombre="Pizza",
            descripcion="Grande",
            precio=20000,
            categoria=categoria
        )

        user = User.objects.create_user(username="juan", password="1234")
        cliente = Cliente.objects.create(usuario=user)

        pedido = Pedido.objects.create(
            cliente=cliente,
            tipo='local',
            total=0
        )

        detalle = DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=2,
            precio=20000
        )

        self.assertEqual(detalle.subtotal(), 40000)




class CarritoTest(TestCase):

    def test_agregar_producto_carrito(self):
        user = User.objects.create_user(username="test", password="123")
        categoria = Categoria.objects.create(nombre="Comida")

        producto = Producto.objects.create(
            nombre="Pizza",
            descripcion="Grande",
            precio=20000,
            categoria=categoria
        )

        carrito = Carrito.objects.create(usuario=user)

        item = ItemCarrito.objects.create(
            carrito=carrito,
            producto=producto,
            cantidad=2
        )

        self.assertEqual(item.subtotal(), 40000)



class ItemCarritoTest(TestCase):

    def test_subtotal_item(self):
        categoria = Categoria.objects.create(nombre="Bebidas")

        producto = Producto.objects.create(
            nombre="Jugo",
            descripcion="Natural",
            precio=4000,
            categoria=categoria
        )

        user = User.objects.create_user(username="maria", password="1234")
        carrito = Carrito.objects.create(usuario=user)

        item = ItemCarrito.objects.create(
            carrito=carrito,
            producto=producto,
            cantidad=2
        )

        self.assertEqual(item.subtotal(), 8000)




class PreferenciasTest(TestCase):

    def test_crear_preferencias(self):
        user = User.objects.create_user(username="sofia", password="1234")

        pref = PreferenciasUsuario.objects.create(
            usuario=user,
            tipo_comida='entrada',
            tipo_bebida='fria',
            tipo_proteina='pollo',
            rango_precio='medio'
        )

        self.assertEqual(pref.usuario.username, "sofia")


















from django.test import TestCase, Client
from django.urls import reverse
from .models import Producto, Categoria

class VistaCartaTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nombre="Comida")

        Producto.objects.create(
            nombre="Pizza",
            descripcion="Grande",
            precio=20000,
            categoria=self.categoria
        )

    def test_ver_carta(self):
        response = self.client.get(reverse('carta'))
        self.assertEqual(response.status_code, 200)


from django.contrib.auth.models import User

class LoginTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="123")

    def test_login(self):
        response = self.client.post('/login/', {
            'username': 'test',
            'password': '123'
        })
        self.assertEqual(response.status_code, 302)


class CarritoVistaTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="123")
        self.client.login(username="test", password="123")

    def test_ver_carrito(self):
        response = self.client.get('/carrito/')
        self.assertEqual(response.status_code, 200)




class AgregarCarritoTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="123")
        self.client.login(username="test", password="123")

        self.categoria = Categoria.objects.create(nombre="Comida")
        self.producto = Producto.objects.create(
            nombre="Pizza",
            descripcion="Grande",
            precio=20000,
            categoria=self.categoria
        )

    def test_agregar_producto(self):
        response = self.client.get(reverse('agregar_carrito', args=[self.producto.id])) 
        self.assertEqual(response.status_code, 302)


from .models import Carrito

class ConfirmarPedidoTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="123")
        self.client.login(username="test", password="123")

        # ✅ crear carrito
        self.carrito = Carrito.objects.create(usuario=self.user)

    def test_confirmar_pedido(self):
        response = self.client.get(reverse('confirmar_pedido'))
        self.assertEqual(response.status_code, 302)



class HacerPedidoTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="123")
        self.client.login(username="test", password="123")

        self.categoria = Categoria.objects.create(nombre="Comida")
        self.producto = Producto.objects.create(
            nombre="Pizza",
            descripcion="Grande",
            precio=20000,
            categoria=self.categoria
        )

    def test_hacer_pedido(self):
        response = self.client.get(f'/pedido/{self.producto.id}/')
        self.assertEqual(response.status_code, 302)

class HistorialTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="123")
        self.client.login(username="test", password="123")

    def test_historial(self):
        response = self.client.get('/historial/')
        self.assertEqual(response.status_code, 200)


class AumentarCarritoTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="123")
        self.client.login(username="test", password="123")

        self.categoria = Categoria.objects.create(nombre="Comida")
        self.producto = Producto.objects.create(
            nombre="Pizza",
            descripcion="Grande",
            precio=20000,
            categoria=self.categoria
        )

        self.carrito = Carrito.objects.create(usuario=self.user)
        self.item = ItemCarrito.objects.create(
            carrito=self.carrito,
            producto=self.producto,
            cantidad=1
        )

    def test_aumentar(self):
        response = self.client.get(f'/carrito/aumentar/{self.item.id}/')
        self.assertEqual(response.status_code, 302)  


class DisminuirCarritoTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="123")
        self.client.login(username="test", password="123")

        self.categoria = Categoria.objects.create(nombre="Comida")
        self.producto = Producto.objects.create(
            nombre="Pizza",
            descripcion="Grande",
            precio=20000,
            categoria=self.categoria
        )

        self.carrito = Carrito.objects.create(usuario=self.user)
        self.item = ItemCarrito.objects.create(
            carrito=self.carrito,
            producto=self.producto,
            cantidad=2
        )

    def test_disminuir(self):
        response = self.client.get(f'/carrito/disminuir/{self.item.id}/')
        self.assertEqual(response.status_code, 302)         


class EliminarItemTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="123")
        self.client.login(username="test", password="123")

        self.categoria = Categoria.objects.create(nombre="Comida")
        self.producto = Producto.objects.create(
            nombre="Pizza",
            descripcion="Grande",
            precio=20000,
            categoria=self.categoria
        )

        self.carrito = Carrito.objects.create(usuario=self.user)
        self.item = ItemCarrito.objects.create(
            carrito=self.carrito,
            producto=self.producto,
            cantidad=1
        )

    def test_eliminar(self):
        response = self.client.get(f'/carrito/eliminar/{self.item.id}/')
        self.assertEqual(response.status_code, 302)             



class BeneficiosTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='123')
        self.client.login(username='test', password='123')
        Cliente.objects.create(usuario=self.user)

    def test_beneficios(self):
        response = self.client.get('/beneficios/')
        self.assertEqual(response.status_code, 200)


class BeneficiosPlatinoTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='platino', password='123')
        self.client.login(username='platino', password='123')
        Cliente.objects.create(usuario=self.user, puntos=600, nivel='platino')

    def test_beneficios_platino(self):
        response = self.client.get('/beneficios/')
        self.assertEqual(response.status_code, 200)


class DescargarPDFTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_pdf(self):
        response = self.client.get('/descargar-menu-pdf/')
        self.assertEqual(response.status_code, 200)


class RegistroTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_ver_registro(self):
        response = self.client.get(reverse('registro'))
        self.assertEqual(response.status_code, 200)

    def test_registro_post_valido(self):
        response = self.client.post(reverse('registro'), {
            'username': 'nuevouser',
            'password1': 'testpass123',
            'password2': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)


class LoginUsuarioTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='123')

    def test_ver_login(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_post_sin_preferencias(self):
        response = self.client.post(reverse('login'), {
            'username': 'test',
            'password': '123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_post_con_preferencias(self):
        PreferenciasUsuario.objects.create(usuario=self.user)
        response = self.client.post(reverse('login'), {
            'username': 'test',
            'password': '123',
        })
        self.assertEqual(response.status_code, 302)


class LogoutTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='123')

    def test_logout(self):
        self.client.login(username='test', password='123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class ConfigurarPreferenciasTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='123')
        self.client.login(username='test', password='123')
        Cliente.objects.create(usuario=self.user, puntos=50, nivel='bronce')

    def test_ver_preferencias(self):
        response = self.client.get(reverse('configurar_preferencias'))
        self.assertEqual(response.status_code, 200)

    def test_guardar_preferencias(self):
        response = self.client.post(reverse('configurar_preferencias'), {
            'tipo_comida': 'entrada',
            'tipo_bebida': 'caliente',
            'tipo_proteina': 'pollo',
            'rango_precio': 'medio',
            'incluir_promociones': True,
        })
        self.assertEqual(response.status_code, 302)

    def test_preferencias_nivel_plata(self):
        cliente = Cliente.objects.get(usuario=self.user)
        cliente.puntos = 150
        cliente.nivel = 'plata'
        cliente.save()
        response = self.client.get(reverse('configurar_preferencias'))
        self.assertEqual(response.status_code, 200)

    def test_preferencias_nivel_oro(self):
        cliente = Cliente.objects.get(usuario=self.user)
        cliente.puntos = 300
        cliente.nivel = 'oro'
        cliente.save()
        response = self.client.get(reverse('configurar_preferencias'))
        self.assertEqual(response.status_code, 200)

    def test_preferencias_nivel_platino(self):
        cliente = Cliente.objects.get(usuario=self.user)
        cliente.puntos = 600
        cliente.nivel = 'platino'
        cliente.save()
        response = self.client.get(reverse('configurar_preferencias'))
        self.assertEqual(response.status_code, 200)


class CartaConFiltrosTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='123')
        self.client.login(username='test', password='123')
        Cliente.objects.create(usuario=self.user)
        PreferenciasUsuario.objects.create(
            usuario=self.user,
            tipo_comida='entrada',
            tipo_bebida='caliente',
            tipo_proteina='pollo',
            rango_precio='medio'
        )
        self.categoria = Categoria.objects.create(nombre='entrada')
        Producto.objects.create(
            nombre='Empanada',
            descripcion='carne',
            precio=10000,
            categoria=self.categoria,
            disponible=True
        )

    def test_carta_filtrada(self):
        response = self.client.get(reverse('carta_con_filtros'))
        self.assertEqual(response.status_code, 200)

    def test_filtro_sin_preferencias_redirige(self):
        self.user2 = User.objects.create_user(username='test2', password='123')
        self.client.login(username='test2', password='123')
        response = self.client.get(reverse('carta_con_filtros'))
        self.assertEqual(response.status_code, 302)


class CartaTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nombre='Comida')
        Producto.objects.create(
            nombre='Pizza',
            descripcion='Grande',
            precio=20000,
            categoria=self.categoria,
            disponible=True
        )

    def test_carta_con_filtro_categoria(self):
        response = self.client.get(f"{reverse('carta')}?categoria={self.categoria.id}")
        self.assertEqual(response.status_code, 200)

    def test_carta_con_busqueda(self):
        response = self.client.get(f"{reverse('carta')}?buscar=Pizza")
        self.assertEqual(response.status_code, 200)

    def test_carta_usuario_autenticado(self):
        user = User.objects.create_user(username='cliente', password='123')
        Cliente.objects.create(usuario=user, puntos=100, nivel='plata')
        self.client.login(username='cliente', password='123')
        response = self.client.get(reverse('carta'))
        self.assertEqual(response.status_code, 200)


class VerCarritoTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='123')
        self.client.login(username='test', password='123')
        Cliente.objects.create(usuario=self.user, nivel='plata')
        self.cat = Categoria.objects.create(nombre='Comida')
        self.prod = Producto.objects.create(nombre='Pizza', descripcion='Grande', precio=20000, categoria=self.cat)

    def test_ver_carrito_sin_existencia_cliente(self):
        user2 = User.objects.create_user(username='test2', password='123')
        self.client.login(username='test2', password='123')
        response = self.client.get(reverse('ver_carrito'))
        self.assertEqual(response.status_code, 200)

    def test_ver_carrito_con_items(self):
        carrito = Carrito.objects.create(usuario=self.user)
        ItemCarrito.objects.create(carrito=carrito, producto=self.prod, cantidad=2)
        response = self.client.get(reverse('ver_carrito'))
        self.assertEqual(response.status_code, 200)

    def test_ver_carrito_nivel_bronce(self):
        cliente = Cliente.objects.get(usuario=self.user)
        cliente.nivel = 'bronce'
        cliente.save()
        Carrito.objects.create(usuario=self.user)
        response = self.client.get(reverse('ver_carrito'))
        self.assertEqual(response.status_code, 200)

    def test_ver_carrito_nivel_oro(self):
        cliente = Cliente.objects.get(usuario=self.user)
        cliente.nivel = 'oro'
        cliente.save()
        Carrito.objects.create(usuario=self.user)
        response = self.client.get(reverse('ver_carrito'))
        self.assertEqual(response.status_code, 200)

    def test_ver_carrito_nivel_platino(self):
        cliente = Cliente.objects.get(usuario=self.user)
        cliente.nivel = 'platino'
        cliente.save()
        Carrito.objects.create(usuario=self.user)
        response = self.client.get(reverse('ver_carrito'))
        self.assertEqual(response.status_code, 200)


class ConfirmarPedidoTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='123')
        self.client.login(username='test', password='123')
        self.carrito = Carrito.objects.create(usuario=self.user)
        Cliente.objects.create(usuario=self.user, nivel='platino')
        self.cat = Categoria.objects.create(nombre='Comida')
        self.prod = Producto.objects.create(nombre='Pizza', descripcion='Grande', precio=20000, categoria=self.cat)

    def test_confirmar_pedido_sin_cliente(self):
        self.user2 = User.objects.create_user(username='test2', password='123')
        self.client.login(username='test2', password='123')
        response = self.client.get(reverse('confirmar_pedido'))
        self.assertEqual(response.status_code, 302)

    def test_confirmar_pedido_vacio(self):
        self.client.login(username='test', password='123')
        response = self.client.get(reverse('confirmar_pedido'))
        self.assertEqual(response.status_code, 302)

    def test_confirmar_pedido_con_items(self):
        ItemCarrito.objects.create(carrito=self.carrito, producto=self.prod, cantidad=2)
        response = self.client.get(reverse('confirmar_pedido'))
        self.assertEqual(response.status_code, 302)


class CartaFiltrosCompletoTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='123')
        self.client.login(username='test', password='123')
        Cliente.objects.create(usuario=self.user)
        PreferenciasUsuario.objects.create(usuario=self.user)
        self.cat_entrada = Categoria.objects.create(nombre='entrada')
        self.cat_bebida_caliente = Categoria.objects.create(nombre='bebida caliente')
        self.cat_postre = Categoria.objects.create(nombre='postre')
        self.p1 = Producto.objects.create(nombre='Empanada', descripcion='carne molida', precio=10000, categoria=self.cat_entrada, disponible=True, promocion=True)
        self.p2 = Producto.objects.create(nombre='Cafe', descripcion='cafe negro', precio=5000, categoria=self.cat_bebida_caliente, disponible=True)
        self.p3 = Producto.objects.create(nombre='TresLeches', descripcion='postre dulce', precio=15000, categoria=self.cat_postre, disponible=True)

    def test_filtro_promociones(self):
        pref = PreferenciasUsuario.objects.get(usuario=self.user)
        pref.incluir_promociones = True
        pref.save()
        response = self.client.get(reverse('carta_con_filtros'))
        self.assertEqual(response.status_code, 200)

    def test_filtro_postre(self):
        pref = PreferenciasUsuario.objects.get(usuario=self.user)
        pref.tipo_comida = 'postre'
        pref.save()
        response = self.client.get(reverse('carta_con_filtros'))
        self.assertEqual(response.status_code, 200)

    def test_filtro_bebida_fria(self):
        self.cat_bebida_fria = Categoria.objects.create(nombre='bebida fria')
        Producto.objects.create(nombre='Jugo', descripcion='jugo natural', precio=6000, categoria=self.cat_bebida_fria, disponible=True)
        pref = PreferenciasUsuario.objects.get(usuario=self.user)
        pref.tipo_bebida = 'fria'
        pref.save()
        response = self.client.get(reverse('carta_con_filtros'))
        self.assertEqual(response.status_code, 200)

    def test_filtro_proteina_res(self):
        pref = PreferenciasUsuario.objects.get(usuario=self.user)
        pref.tipo_proteina = 'carne'
        pref.save()
        response = self.client.get(reverse('carta_con_filtros'))
        self.assertEqual(response.status_code, 200)

    def test_filtro_proteina_pollo(self):
        pref = PreferenciasUsuario.objects.get(usuario=self.user)
        pref.tipo_proteina = 'pollo'
        pref.save()
        response = self.client.get(reverse('carta_con_filtros'))
        self.assertEqual(response.status_code, 200)

    def test_filtro_proteina_pescado(self):
        pref = PreferenciasUsuario.objects.get(usuario=self.user)
        pref.tipo_proteina = 'pescado'
        pref.save()
        response = self.client.get(reverse('carta_con_filtros'))
        self.assertEqual(response.status_code, 200)

    def test_filtro_proteina_maricos(self):
        pref = PreferenciasUsuario.objects.get(usuario=self.user)
        pref.tipo_proteina = 'mariscos'
        pref.save()
        response = self.client.get(reverse('carta_con_filtros'))
        self.assertEqual(response.status_code, 200)

    def test_filtro_proteina_vegetariano(self):
        self.p1.es_vegetariano = True
        self.p1.save()
        pref = PreferenciasUsuario.objects.get(usuario=self.user)
        pref.tipo_proteina = 'vegetariano'
        pref.save()
        response = self.client.get(reverse('carta_con_filtros'))
        self.assertEqual(response.status_code, 200)

    def test_filtro_precio_economico(self):
        pref = PreferenciasUsuario.objects.get(usuario=self.user)
        pref.rango_precio = 'economico'
        pref.save()
        response = self.client.get(reverse('carta_con_filtros'))
        self.assertEqual(response.status_code, 200)

    def test_filtro_precio_medio(self):
        pref = PreferenciasUsuario.objects.get(usuario=self.user)
        pref.rango_precio = 'medio'
        pref.save()
        response = self.client.get(reverse('carta_con_filtros'))
        self.assertEqual(response.status_code, 200)

    def test_filtro_precio_alto(self):
        pref = PreferenciasUsuario.objects.get(usuario=self.user)
        pref.rango_precio = 'alto'
        pref.save()
        response = self.client.get(reverse('carta_con_filtros'))
        self.assertEqual(response.status_code, 200)


class CartaClienteConDescuentoTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='cliente', password='123')
        self.client.login(username='cliente', password='123')
        self.cat = Categoria.objects.create(nombre='Comida')
        self.producto = Producto.objects.create(
            nombre='Pizza',
            descripcion='Grande',
            precio=50000,
            categoria=self.cat,
            disponible=True,
            promocion=True
        )

    def test_carta_cliente_bronce(self):
        Cliente.objects.create(usuario=self.user, puntos=50, nivel='bronce')
        response = self.client.get(reverse('carta'))
        self.assertEqual(response.status_code, 200)

    def test_carta_cliente_plata(self):
        Cliente.objects.create(usuario=self.user, puntos=150, nivel='plata')
        response = self.client.get(reverse('carta'))
        self.assertEqual(response.status_code, 200)

    def test_carta_cliente_oro(self):
        Cliente.objects.create(usuario=self.user, puntos=300, nivel='oro')
        response = self.client.get(reverse('carta'))
        self.assertEqual(response.status_code, 200)

    def test_carta_cliente_platino(self):
        Cliente.objects.create(usuario=self.user, puntos=600, nivel='platino')
        response = self.client.get(reverse('carta'))
        self.assertEqual(response.status_code, 200)


class AgregarAlCarritoItemExistenteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='123')
        self.client.login(username='test', password='123')
        self.categoria = Categoria.objects.create(nombre='Comida')
        self.producto = Producto.objects.create(
            nombre='Pizza',
            descripcion='Grande',
            precio=20000,
            categoria=self.categoria
        )
        self.carrito = Carrito.objects.create(usuario=self.user)
        ItemCarrito.objects.create(carrito=self.carrito, producto=self.producto, cantidad=1)

    def test_agregar_item_existente_aumenta_cantidad(self):
        response = self.client.get(reverse('agregar_carrito', args=[self.producto.id]))
        self.assertEqual(response.status_code, 302)


class DisminuirCantidadEliminarTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='123')
        self.client.login(username='test', password='123')
        self.categoria = Categoria.objects.create(nombre='Comida')
        self.producto = Producto.objects.create(
            nombre='Pizza',
            descripcion='Grande',
            precio=20000,
            categoria=self.categoria
        )
        self.carrito = Carrito.objects.create(usuario=self.user)
        self.item = ItemCarrito.objects.create(
            carrito=self.carrito,
            producto=self.producto,
            cantidad=1
        )

    def test_disminuir_cantidad_uno_elimina_item(self):
        response = self.client.get(reverse('disminuir_cantidad', args=[self.item.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ItemCarrito.objects.filter(id=self.item.id).exists())





class DescargarPDFConProductosTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nombre='Comida')
        Producto.objects.create(
            nombre='Pizza',
            descripcion='Grande',
            precio=20000,
            categoria=self.categoria,
            disponible=True,
            promocion=True
        )

    def test_pdf_con_productos(self):
        response = self.client.get('/descargar-menu-pdf/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')


class HacerPedidoTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='123')
        self.client.login(username='test', password='123')
        self.categoria = Categoria.objects.create(nombre='Comida')
        self.producto = Producto.objects.create(
            nombre='Pizza',
            descripcion='Grande',
            precio=20000,
            categoria=self.categoria
        )

    def test_hacer_pedido_sin_descuento(self):
        Cliente.objects.create(usuario=self.user, puntos=0, nivel='bronce')
        response = self.client.get(reverse('hacer_pedido', args=[self.producto.id]))
        self.assertEqual(response.status_code, 302)

    def test_hacer_pedido_con_descuento_y_puntos(self):
        Cliente.objects.create(usuario=self.user, puntos=150, nivel='plata')
        response = self.client.get(reverse('hacer_pedido', args=[self.producto.id]))
        self.assertEqual(response.status_code, 302)        