from django.contrib import admin

# Register your models here.

from .models import Empresa, Categoria, Producto, Beneficio, ProductoInstance

"""Minimal registration of Models.
admin.site.register(Producto)
admin.site.register(Empresa)
admin.site.register(ProductoInstance)
admin.site.register(Categoria)
admin.site.register(Beneficio)
"""

admin.site.register(Categoria)
admin.site.register(Beneficio)


class ProductosInline(admin.TabularInline):
    """Defines format of inline Producto insertion (used in EmpresaAdmin)"""
    model = Producto


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    """Administration object for Empresa models.
    Defines:
     - fields to be displayed in list view (list_display)
     - orders fields in detail view (fields),
       grouping the date fields horizontally
     - adds inline addition of Productos in Empresa view (inlines)
    """
    list_display = ('nombre',
                    'descripcion', 'direccion', 'telefono', 'email', 'facebook', 'web')
    fields = ['nombre', 'descripcion', ('telefono', 'email', 'facebook', 'web')]
    #inlines = [ProductosInline]

"""
class ProductosInstanceInline(admin.TabularInline):
    #Defines format of inline Producto instance insertion (used in ProductoAdmin)
    model = ProductoInstance
"""

class ProductoAdmin(admin.ModelAdmin):
    """Administration object for Producto models.
    Defines:
     - fields to be displayed in list view (list_display)
     - adds inline addition of Producto instances in Producto view (inlines)
    """
    list_display = ('nombre', 'empresa', 'display_categoria')
    #inlines = [ProductosInstanceInline]


admin.site.register(Producto, ProductoAdmin)

"""
@admin.register(ProductoInstance)
class ProductoInstanceAdmin(admin.ModelAdmin):
    #Administration object for ProductoInstance models.
    #Defines:
    # - fields to be displayed in list view (list_display)
    #- filters that will be displayed in sidebar (list_filter)
    # - grouping of fields into sections (fieldsets)

    list_display = ('Producto', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('Producto', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )
"""
