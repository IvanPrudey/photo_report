from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    BrandProduct,
    CategoryProduct,
    PhotoReport,
    TradingClient,
    User
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'username',
        'telegram_id',
        'first_name',
        'last_name',
        'role',
        'is_verified',
        'last_activity',
        'is_active'
    ]
    list_filter = ['role', 'is_verified', 'is_active', 'date_joined']
    search_fields = ['username', 'telegram_id', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('Telegram данные', {
            'fields': (
                'telegram_id',
                'role',
                'phone',
                'is_verified',
                'last_activity'
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Telegram данные', {
            'fields': ('telegram_id', 'role', 'phone')
        }),
    )


@admin.register(CategoryProduct)
class CategoryProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_name_display']
    list_filter = ['name']
    search_fields = ['name']

    def get_name_display(self, obj):
        return obj.get_name_display()
    get_name_display.short_description = 'Название категории'


@admin.register(TradingClient)
class TradingClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(BrandProduct)
class BrandProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name']


@admin.register(PhotoReport)
class PhotoReportAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'trading_client',
        'category',
        'brand',
        'is_competitor',
        'get_photos_count',
        'created_at'
    ]
    list_filter = ['is_competitor', 'created_at', 'trading_client', 'category']
    search_fields = ['user__username', 'trading_client__name', 'brand__name']
    readonly_fields = ['created_at']

    def get_photos_count(self, obj):
        return obj.get_photos_count()
    get_photos_count.short_description = 'Кол-во фото'
