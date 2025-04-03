from rest_framework import serializers
from .models import User, DriverProfile, Cargo, CargoReview

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user

class DriverProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = DriverProfile
        fields = ['id', 'user', 'profile_picture', 'vehicle_type', 'license_type', 'vehicle_capacity', 'experience']

class CargoReviewSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    class Meta:
        model = CargoReview
        fields = ['id', 'cargo', 'customer', 'comment', 'stars', 'created_at']

class CargoSerializer(serializers.ModelSerializer):
    driver = DriverProfileSerializer(read_only=True)
    reviews = CargoReviewSerializer(many=True, read_only=True)
    customer = UserSerializer(read_only=True)

    class Meta:
        model = Cargo
        fields = ['id', 'customer', 'driver', 'name', 'weight', 'origin', 'destination', 'vehicle_type', 'status', 'created_at', 'reviews', 'price', 'description']