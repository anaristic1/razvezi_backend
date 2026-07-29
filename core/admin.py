from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Route, Driver, Dispatcher, UserAtLocation, Company

#admin.site.unregister(User)
#admin.site.register(User, UserAdmin)
admin.site.register(UserAtLocation)

admin.site.register(Driver)
admin.site.register(Dispatcher)
admin.site.register(Company)

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    readonly_fields = ('date_created', 'created_by', )
    #exclude = ('created_by', )

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "taken_by":
            kwargs["queryset"] = User.objects.filter(role="driver")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Info", {"fields": ("role",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra Info", {"fields": ("role",)}),
    )
