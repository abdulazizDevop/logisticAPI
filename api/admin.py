import datetime
from django import forms
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DriverProfile, Cargo, CargoReview, Advertisement, ContactMessage

# Custom User uchun Admin
class UserAdmin(BaseUserAdmin):
    list_display = ('phone_number', 'name', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('phone_number', 'name', 'email')
    ordering = ('phone_number',)
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal Info', {'fields': ('name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'name', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    filter_horizontal = ()

# DriverProfile uchun Admin
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_type', 'license_type', 'vehicle_capacity', 'experience')
    list_filter = ('vehicle_type',)
    search_fields = ('user__phone_number', 'user__name', 'vehicle_type')

# Cargo uchun Admin
class CargoAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'driver', 'vehicle_type', 'status', 'created_at')
    list_filter = ('vehicle_type', 'status')
    search_fields = ('name', 'customer__phone_number', 'driver__user__phone_number')
    list_editable = ('status',)

# CargoReview uchun Admin
class CargoReviewAdmin(admin.ModelAdmin):
    list_display = ('cargo', 'customer', 'comment', 'created_at')
    search_fields = ('cargo__name', 'customer__phone_number', 'comment')

# Modellarni ro‘yxatdan o‘tkazish
admin.site.register(User, UserAdmin)
admin.site.register(DriverProfile, DriverProfileAdmin)
admin.site.register(Cargo, CargoAdmin)
admin.site.register(CargoReview, CargoReviewAdmin)


class AdvertisementAdminForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = '__all__'
    
    def save(self, commit=True):
        advertisement = super().save(commit=False)
        # Agar status o'zgargan bo'lsa va "Tasdiqlangan" qilingan bo'lsa
        if advertisement.status == 'Tasdiqlangan' and advertisement.is_active and not advertisement.start_date:
            # Boshlash sanasini hozirgi kun qilib o'rnatamiz
            advertisement.start_date = timezone.now().date()
            # Tugash sanasini duration_days asosida hisoblaymiz
            advertisement.end_date = advertisement.start_date + datetime.timedelta(days=advertisement.duration_days)
        
        if commit:
            advertisement.save()
        return advertisement

class AdvertisementAdmin(admin.ModelAdmin):
    form = AdvertisementAdminForm
    list_display = ('company_name', 'ad_type', 'duration_days', 'phone_number', 'status', 'is_active', 'created_at')
    list_filter = ('status', 'is_active', 'ad_type', 'duration_days')
    search_fields = ('company_name', 'description', 'phone_number')
    list_editable = ('status', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Reklama ma\'lumotlari', {
            'fields': ('company_name', 'ad_type', 'duration_days', 'phone_number', 'description')
        }),
        ('Admin boshqaruvi', {
            'fields': ('status', 'is_active', 'media_file', 'start_date', 'end_date', 'admin_notes')
        }),
        ('Ma\'lumot', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    actions = ['approve_advertisements', 'reject_advertisements', 'activate_advertisements', 'deactivate_advertisements']

    def approve_advertisements(self, request, queryset):
        for ad in queryset:
            ad.status = 'Tasdiqlangan'
            if not ad.start_date and ad.is_active:
                ad.start_date = timezone.now().date()
                ad.end_date = ad.start_date + datetime.timedelta(days=ad.duration_days)
            ad.save()
    approve_advertisements.short_description = "Tanlangan reklamalarni tasdiqlash"

    def reject_advertisements(self, request, queryset):
        queryset.update(status='Rad etilgan')
    reject_advertisements.short_description = "Tanlangan reklamalarni rad etish"

    def activate_advertisements(self, request, queryset):
        for ad in queryset:
            ad.is_active = True
            if ad.status == 'Tasdiqlangan' and not ad.start_date:
                ad.start_date = timezone.now().date()
                ad.end_date = ad.start_date + datetime.timedelta(days=ad.duration_days)
            ad.save()
    activate_advertisements.short_description = "Tanlangan reklamalarni faollashtirish"

    def deactivate_advertisements(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_advertisements.short_description = "Tanlangan reklamalarni faolsizlashtirish"

# Modellarni ro'yxatdan o'tkazish
admin.site.register(Advertisement, AdvertisementAdmin)


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'subject', 'status', 'created_at')  # Ko‘rinadigan ustunlar
    list_filter = ('status',)  # Status bo‘yicha filtr
    search_fields = ('name', 'email', 'phone_number', 'subject', 'message')  # Qidiruv maydonlari
    list_editable = ('status',)  # Statusni to‘g‘ridan-to‘g‘ri ro‘yxatda o‘zgartirish mumkin
    readonly_fields = ('created_at',)  # Faqat o‘qish uchun maydon

    fieldsets = (
        ('Xabar ma\'lumotlari', {
            'fields': ('name', 'email', 'phone_number', 'subject', 'message')
        }),
        ('Admin boshqaruvi', {
            'fields': ('status', 'created_at')
        }),
    )

admin.site.register(ContactMessage, ContactMessageAdmin)