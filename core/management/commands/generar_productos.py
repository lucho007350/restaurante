from django.core.management.base import BaseCommand
from core.models import Categoria, Producto
from decimal import Decimal


class Command(BaseCommand):
    help = 'Genera productos de ejemplo para el restaurante'

    def handle(self, *args, **options):
        categorias_data = {
            'Hamburguesas': [
                {'nombre': 'Hamburguesa Clásica', 'descripcion': 'Carne de res, lechuga, tomate, cebolla, queso cheddar y salsa especial', 'precio': 25000},
                {'nombre': 'Hamburguesa BBQ', 'descripcion': 'Carne de res, tocino crujiente, cebolla caramelizada y salsa BBQ', 'precio': 28000},
                {'nombre': 'Hamburguesa Vegana', 'descripcion': 'Hamburguesa de lentejas con aguacate, tomate y aliño vegano', 'precio': 26000},
                {'nombre': 'Doble Cheeseburger', 'descripcion': 'Doble carne, doble queso, lechuga y tomate', 'precio': 32000},
                {'nombre': 'Hamburguesa Picante', 'descripcion': 'Carne de res, jalapeños, queso pepper jack y salsa habanero', 'precio': 27000},
            ],
            'Bebidas': [
                {'nombre': 'Refresco de Cola', 'descripcion': 'Refresco gasificado tradicional', 'precio': 5000},
                {'nombre': 'Limonada Natural', 'descripcion': 'Limonada preparada con limones frescos', 'precio': 7000},
                {'nombre': 'Cerveza Nacional', 'descripcion': 'Cerveza rubia nacional bien fría', 'precio': 8000},
                {'nombre': 'Jugo de Mango', 'descripcion': 'Jugo natural de mango', 'precio': 7500},
                {'nombre': 'Agua Mineral', 'descripcion': 'Agua mineral sin gas', 'precio': 4000},
            ],
            'Postres': [
                {'nombre': 'Brownie con Helado', 'descripcion': 'Brownie de chocolate caliente con bola de helado de vainilla', 'precio': 12000},
                {'nombre': 'Cheesecake', 'descripcion': 'Tarta de queso con cobertura de frutas', 'precio': 10000},
                {'nombre': 'Flan de Caramelo', 'descripcion': 'Flan casero con salsa de caramelo', 'precio': 9000},
                {'nombre': 'Helado Sundae', 'descripcion': 'Helado con nueces, chocolate y crema', 'precio': 11000},
            ],
            'Entradas': [
                {'nombre': 'Papas Fritas', 'descripcion': 'Papas fritas crujientes con sal', 'precio': 8000},
                {'nombre': 'Aros de Cebolla', 'descripcion': 'Aros de cebolla empanizados y crujientes', 'precio': 9000},
                {'nombre': 'Alitas BBQ', 'descripcion': 'Alitas de pollo con salsa BBQ', 'precio': 15000},
                {'nombre': 'Nachos con Queso', 'descripcion': 'Nachos con queso fundido y jalapeños', 'precio': 12000},
            ],
            'Pizzas': [
                {'nombre': 'Pizza Margherita', 'descripcion': 'Salsa de tomate, mozzarella fresco y albahaca', 'precio': 28000},
                {'nombre': 'Pizza Pepperoni', 'descripcion': 'Salsa de tomate, mozzarella y pepperoni', 'precio': 30000},
                {'nombre': 'Pizza Vegetariana', 'descripcion': 'Mozzarella, pimientos, champiñones, cebolla y aceitunas', 'precio': 27000},
                {'nombre': 'Pizza Hawaiana', 'descripcion': 'Jamón, piña y mozzarella', 'precio': 29000},
            ],
        }

        productos_creados = 0

        for cat_nombre, productos in categorias_data.items():
            categoria, _ = Categoria.objects.get_or_create(nombre=cat_nombre)
            
            for prod_data in productos:
                producto, created = Producto.objects.get_or_create(
                    nombre=prod_data['nombre'],
                    defaults={
                        'descripcion': prod_data['descripcion'],
                        'precio': Decimal(str(prod_data['precio'])),
                        'categoria': categoria,
                        'disponible': True,
                    }
                )
                if created:
                    productos_creados += 1

        self.stdout.write(self.style.SUCCESS(f'Se crearon {productos_creados} productos exitosamente!'))
