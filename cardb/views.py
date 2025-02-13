# Create your views here.
import self as self
from geopy import Nominatim
from rest_framework import generics, viewsets, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import CountryCar, CompanyCar, Order, carmodel, CarName, Sections, Products, Delivery, add_delvery
from .Serializer import CarDetailsSerializer, CarModelSerializer, CountrySerializer, ManufacturerSerializer, \
    SectionSerializer, DeliverySerializer_write, \
    AddDelivery_driver, \
    Delivery_driver, Delivery_driver_read, ProductSerializer, OrderSerializer, DeliverySerializer, \
    DeliverySerializer_workshop, OrderSerializer_read, AddDelivery_driver_read, AddDelivery_driver_status


class IsSellerUser(permissions.BasePermission):
    message = "You do not have permission to access this resource."

    def has_permission(self, request, view):
        # Check if the user is authenticated and is of type 'SELLER'
        return request.user.is_authenticated and request.user.type == 'SELLER'

class IsWorkShopUser(permissions.BasePermission):
    message = "You do not have permission to access this resource."

    def has_permission(self, request, view):
        # Check if the user is authenticated and is of type 'WORKSHOP'
        return request.user.is_authenticated and request.user.type == 'WORKSHOP'

class IsDRIVERUser(permissions.BasePermission):
    message = "You do not have permission to access this resource."
    def has_permission(self, request, view):
        # Check if the user is authenticated and is of type 'DELIVERY'
        return request.user.is_authenticated and request.user.type == 'DRIVER'


class CountryListCreateView(viewsets.ReadOnlyModelViewSet):
    queryset = CountryCar.objects.all()
    serializer_class = CountrySerializer



class ManufacturerListCreateView(viewsets.ReadOnlyModelViewSet):
    queryset = CompanyCar.objects.all()
    serializer_class = ManufacturerSerializer



class CarModelListCreateView(viewsets.ReadOnlyModelViewSet):
    queryset =carmodel.objects.all()
    serializer_class = CarModelSerializer

   #------------------
class CarDetailsListCreateView(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsSellerUser]
    queryset = CarName.objects.all()
    serializer_class = CarDetailsSerializer

class CarDetailsDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsSellerUser]
    queryset = CarName.objects.all()
    serializer_class = CarDetailsSerializer


#-------
class SectionListCreateView(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsSellerUser]  # Only allows seller users
    queryset = Sections.objects.all()
    serializer_class = SectionSerializer

class SectionListCreateViewworkshop(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsWorkShopUser]  # Only allows workshop users
    queryset = Sections.objects.all()

    def get_queryset(self):
        return Sections.objects.filter(user=self.request.user)

    serializer_class = SectionSerializer

class SectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsWorkShopUser]  # Only allows workshop users
    queryset = Sections.objects.all()

    def get_queryset(self):
        return Sections.objects.filter(user=self.request.user)

    serializer_class = SectionSerializer

# Product Views
class ProductListCreateView(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsSellerUser]  # Only allows seller users
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

class ProductListCreateViewwork(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsWorkShopUser]  # Only allows workshop users
    queryset = Products.objects.all()

    def get_queryset(self):
        return Products.objects.filter(user=self.request.user)

    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsWorkShopUser]  # Only allows workshop users
    queryset = Products.objects.all()

    def get_queryset(self):
        return Products.objects.filter(user=self.request.user)

    serializer_class = ProductSerializer


# ordrer
class OrderListCreateView(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsSellerUser]  # Only allows seller users
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            # Use OrderCreateSerializer for POST requests (creation)
            return OrderSerializer
        else:
            # Use OrderListSerializer for GET requests (listing)
            return OrderSerializer_read
    def perform_create(self, serializer):
        # Set the user to the currently authenticated user before saving the order
        serializer.save(user=self.request.user)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsSellerUser]  # Only allows seller users
    queryset = Order.objects.all()
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    serializer_class = OrderSerializer_read

#delvery
geolocator = Nominatim(user_agent="location")
class DeliveryListCreateView(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsSellerUser]
    queryset = Delivery.objects.all()
    def get_serializer_class(self):
        if self.request.method == 'POST':
            # Use OrderCreateSerializer for POST requests (creation)
            return DeliverySerializer_write
        else:
            # Use OrderListSerializer for GET requests (listing)
            return DeliverySerializer

    def perform_create(self, serializer):
        address = serializer.initial_data["address"]
        g = geolocator.geocode(address)
        lat = g.latitude
        lng = g.longitude

        serializer.save()

class DeliveryList_workshop(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsWorkShopUser]
    serializer_class = DeliverySerializer
    def get_queryset(self):

        # Assuming you have a one-to-one relationship between Products and Users
           # Adjust this based on your actual relationship

        # Filter deliveries based on conditions
        queryset = Delivery.objects.filter(
            orders__product__user=self.request.user,

        )
        return queryset

    def perform_create(self, serializer):
        # Assuming you want to associate the created delivery with the current user
        serializer.save(user=self.request.user)



class DeliveryDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsWorkShopUser]
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer_workshop

    def get_queryset(self):
        # Assuming you have a one-to-one relationship between Products and Users
        # Adjust this based on your actual relationship

        # Filter deliveries based on conditions
        queryset = Delivery.objects.filter(
            orders__product__user=self.request.user,

        )
        return queryset

    def perform_create(self, serializer):
        # Assuming you want to associate the created delivery with the current user
        serializer.save(user=self.request.user)


#
class Delivery_driverview(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsDRIVERUser]
    queryset = Delivery.objects.queryset = Delivery.objects.filter(order_bollen=True)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            # Use OrderCreateSerializer for POST requests (creation)
            return Delivery_driver
        else:
            # Use OrderListSerializer for GET requests (listing)
            return Delivery_driver_read


class Delivery_driverlist(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsDRIVERUser]
    queryset = Delivery.objects.filter(order_bollen=True)
    serializer_class = Delivery_driver

class Delivery_driverlist_rejected(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsDRIVERUser]
    queryset = Delivery.objects.filter(order_bollen=True)
    serializer_class = Delivery_driver


class AddDeliveryView(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsDRIVERUser]

    queryset = add_delvery.objects.filter(delivery__order_bollen=True)

    def get_queryset(self):
        # Assuming you have a one-to-one relationship between Products and Users
        # Adjust this based on your actual relationship

        # Filter deliveries based on conditions
        queryset = add_delvery.objects.filter(
            delivery__order_bollen=True,
            user=self.request.user,
            status='active'
        )
        return queryset


    def get_serializer_class(self):
        if self.request.method == 'POST':
            # Use OrderCreateSerializer for POST requests (creation)
            return AddDelivery_driver
        else:
            # Use OrderListSerializer for GET requests (listing)
            return AddDelivery_driver_read

class AddDeliveryView_edit_status(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsDRIVERUser]

    queryset = add_delvery.objects.filter(delivery__order_bollen=True)

    def get_queryset(self):
        # Assuming you have a one-to-one relationship between Products and Users
        # Adjust this based on your actual relationship

        # Filter deliveries based on conditions
        queryset = add_delvery.objects.filter(
            delivery__order_bollen=True,
            user=self.request.user,
            status='active'
        )
        return queryset

    serializer_class = AddDelivery_driver_status


class AddDeliveryView_edit_pending(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsDRIVERUser]

    queryset = add_delvery.objects.filter(delivery__order_bollen=True)

    def get_queryset(self):
        # Assuming you have a one-to-one relationship between Products and Users
        # Adjust this based on your actual relationship

        # Filter deliveries based on conditions
        queryset = add_delvery.objects.filter(
            delivery__order_bollen=True,
            user=self.request.user,
            status='pending'
        )
        return queryset

    serializer_class =AddDelivery_driver_read

class AddDeliveryView_edit_rejected(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsDRIVERUser]

    queryset = add_delvery.objects.filter(delivery__order_bollen=True)

    def get_queryset(self):
        # Assuming you have a one-to-one relationship between Products and Users
        # Adjust this based on your actual relationship

        # Filter deliveries based on conditions
        queryset = add_delvery.objects.filter(
            delivery__order_bollen=True,
            user=self.request.user,
            status='rejected'
        )
        return queryset

    serializer_class =AddDelivery_driver_read
class AddDeliveryView_edit_completed(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsDRIVERUser]

    queryset = add_delvery.objects.filter(delivery__order_bollen=True)

    def get_queryset(self):
        # Assuming you have a one-to-one relationship between Products and Users
        # Adjust this based on your actual relationship

        # Filter deliveries based on conditions
        queryset = add_delvery.objects.filter(
            delivery__order_bollen=True,
            user=self.request.user,
            status='completed'
        )
        return queryset

    serializer_class =AddDelivery_driver_read

