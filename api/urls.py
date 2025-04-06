from django.urls import path
from .views import (
    RegisterView, LoginView, DriverProfileView, CargoListCreateView, 
    CargoDetailView, CargoReviewCreateView, ContactMessageView,
    AdvertisementRequestView, ActiveAdvertisementsView, AdvertisementsByTypeView
)

urlpatterns = [
    # Mavjud URL'lar
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', DriverProfileView.as_view(), name='profile'),
    path('cargos/', CargoListCreateView.as_view(), name='cargo-list-create'),
    path('cargos/<int:pk>/', CargoDetailView.as_view(), name='cargo-detail'),
    path('reviews/', CargoReviewCreateView.as_view(), name='review-create'),
    
    # Yangi URL'lar - Kontakt formasi
    path('contact/', ContactMessageView.as_view(), name='contact'),
    
    # Reklama API endpointlari
    path('ad-request/', AdvertisementRequestView.as_view(), name='ad-request'),
    path('advertisements/', ActiveAdvertisementsView.as_view(), name='active-ads'),
    path('advertisements/<str:ad_type>/', AdvertisementsByTypeView.as_view(), name='ads-by-type'),
]