from rest_framework import status
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, DriverProfile, Cargo, CargoReview, Advertisement
from .serializers import (UserSerializer, DriverProfileSerializer, CargoSerializer, CargoReviewSerializer, 
                          AdvertisementSerializer, AdvertisementCreateSerializer, ContactMessageSerializer)

# Registratsiya (Ochiq)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            DriverProfile.objects.create(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Custom Login (Ochiq)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        if not phone_number or not password:
            return Response({"detail": "Phone number and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, phone_number=phone_number, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


# Profil ko‘rish va tahrirlash (Faqat autentifikatsiya bilan)
class DriverProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = DriverProfile.objects.get(user=request.user)
        serializer = DriverProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = DriverProfile.objects.get(user=request.user)
        serializer = DriverProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Yuklar ro‘yxati va qo‘shish (Faqat autentifikatsiya bilan)
class CargoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cargos = Cargo.objects.all()
        serializer = CargoSerializer(cargos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CargoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Yukni tahrirlash va o‘chirish (Faqat autentifikatsiya bilan)
class CargoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        cargo = Cargo.objects.get(pk=pk)
        serializer = CargoSerializer(cargo)
        return Response(serializer.data)

    def put(self, request, pk):
        cargo = Cargo.objects.get(pk=pk)
        if cargo.customer != request.user and not request.user.driverprofile:  # Faqat mijoz yoki haydovchi o‘zgartirishi mumkin
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        
        # Agar haydovchi o‘zi o‘zi belgilamoqchi bo‘lsa
        if request.user.driverprofile and not cargo.driver:
            cargo.driver = request.user.driverprofile
            cargo.status = "Yolda"  # Haydovchi tanlaganidan keyin status o‘zgaradi
            cargo.save()
            serializer = CargoSerializer(cargo)
            return Response(serializer.data)

        # Oddiy tahrirlash (faqat mijoz uchun)
        if cargo.customer == request.user:
            serializer = CargoSerializer(cargo, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk):
        cargo = Cargo.objects.get(pk=pk)
        if cargo.customer != request.user:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        cargo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# Sharh qo‘shish (Faqat autentifikatsiya bilan)
class CargoReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CargoReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ContactMessageView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Xabaringiz muvaffaqiyatli yuborildi"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdvertisementRequestView(APIView):
    """
    Foydalanuvchilar uchun reklama so'rovini yuborish API
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = AdvertisementCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Reklama so'rovingiz qabul qilindi. Administrator tez orada siz bilan bog'lanadi."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActiveAdvertisementsView(APIView):
    """
    Frontend uchun faol reklamalarni qaytaruvchi API
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        current_date = timezone.now().date()
        # Faqat tasdiqlangan, faol va muddati tugamagan reklamalarni qaytarish
        advertisements = Advertisement.objects.filter(
            status='Tasdiqlangan',
            is_active=True,
            start_date__lte=current_date,
            end_date__gte=current_date,
            media_file__isnull=False  # Media fayli bo'lgan reklamalarni olish
        )
        serializer = AdvertisementSerializer(advertisements, many=True)
        return Response(serializer.data)


class AdvertisementsByTypeView(APIView):
    """
    Frontend uchun reklama turlariga qarab reklamalarni qaytaruvchi API
    """
    permission_classes = [AllowAny]
    
    def get(self, request, ad_type):
        current_date = timezone.now().date()
        # Turi bo'yicha reklama tanlash
        advertisements = Advertisement.objects.filter(
            status='Tasdiqlangan',
            is_active=True,
            ad_type=ad_type,
            start_date__lte=current_date,
            end_date__gte=current_date,
            media_file__isnull=False
        )
        serializer = AdvertisementSerializer(advertisements, many=True)
        return Response(serializer.data)