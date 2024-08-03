from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User, Group
from .models import MenuItem, Category, Cart, Order
from .serializers import MenuItemSerializer, MenuItemCreateSerializer, CategorySerializer, UserRegisterSerializer, UsersSerializer, CurrentUserSerializer, ManagerUsersSerializer, DeliverCrewUsersSerializer, CartSerializer, CartCreateSerializer, OrderSerializer, OrderUpdateCompleteManagerSerializer, OrderUpdatePartialManagerSerializer, OrderUpdateCustomerSerializer, OrderItemCartSerializer, OrderDeliverCrewSerializer, OrderUpdateDeliverCrewSerializer
from .permissions import ManagerRole
from rest_framework.decorators import api_view, permission_classes, throttle_classes
import math
from decimal import Decimal
from datetime import datetime

# Create your views here.

class MenuItemsCategoryView(generics.ListAPIView, generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get(self, request):
        if request.user.groups.filter(name = 'Manager').exists():
            self.permission_classes = [IsAuthenticated]
            self.throttle_classes = [UserRateThrottle]
        else:
            self.permission_classes = [AllowAny]
            self.throttle_classes = [AnonRateThrottle]
        if self.queryset.exists():
            return Response(self.serializer_class(get_list_or_404(self.queryset), many=True).data)
        else:
            return Response({ "message" : "There are no categories" }, status=status.HTTP_404_NOT_FOUND)
    def post(self, request):
        if request.user.groups.filter(name = 'Manager').exists():
            self.permission_classes = [IsAuthenticated, ManagerRole]
            self.throttle_classes = [UserRateThrottle]
            self.permission_classes = [ ManagerRole]
            self.throttle_classes = [UserRateThrottle]
            if Category.objects.filter(name = request.data['name']).exists():
                return Response({ "message" : "Category already exists" }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(self.serializer_class(Category.objects.create(name=request.data['name']), many=False).data, status=status.HTTP_201_CREATED)
        else:
            return Response({ "message" : "Unauthorized to create a category " }, status=status.HTTP_401_UNAUTHORIZED)

class MenuItemsSingleCategoryView(generics.DestroyAPIView, generics.UpdateAPIView, generics.ListAPIView):
    def get(self, request, pk):
        serializer_class = MenuItemSerializer
        self.permission_classes = [IsAuthenticated, AllowAny]
        self.throttle_classes = [AnonRateThrottle]
        if Category.objects.filter(id=pk).exists():
            return Response(serializer_class(get_list_or_404(MenuItem.objects.filter(category=pk)), many=True).data)
        else:
            return Response({ "message" : "Category does not exist" }, status=status.HTTP_404_NOT_FOUND)
    def patch(self, request, pk):
        self.permission_classes = [IsAuthenticated, ManagerRole]
        self.throttle_classes = [UserRateThrottle]
        if Category.objects.filter(id=pk).exists():
            category = Category.objects.get(id=pk)
            category.name = request.data['name']
            category.save()
            return Response(CategorySerializer(get_list_or_404(Category.objects.filter(id=pk)), many=True).data, status=status.HTTP_200_OK)
        else:
            return Response({ "message" : "Category does not exist" }, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, ManagerRole]
        self.throttle_classes = [UserRateThrottle]
        if Category.objects.filter(id=pk).exists():
            Category.objects.get(id=pk).delete()
            return Response({ "message" : "Category Removed" }, status=status.HTTP_200_OK)
        else:
            return Response({ "message" : "Category does not exist" }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def menu_items(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            items = MenuItem.objects.all()
            category_name = request.query_params.get('category')
            to_price = request.query_params.get('to_price')
            search = request.query_params.get('search')
            ordering = request.query_params.get('ordering')
            per_page = request.query_params.get('per_page', default=2)
            page = request.query_params.get('page', default=1)
            if category_name is not None:
                items = items.filter(category__name=category_name)
            if to_price is not None:
                items = items.filter(price__lte=to_price)
            if search is not None:
                items = items.filter(title__icontains=search)
            if ordering is not None:
                ordering_fields = ordering.split(',')
                items = items.order_by(*ordering_fields)
            paginator = PageNumberPagination()
            paginator.page_size = per_page
            try:
                result_page = paginator.paginate_queryset(items, request)
            except EmptyPage:
                result_page = []
            serializer = MenuItemSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        elif request.method == 'POST':
            if request.user.groups.filter(name="Manager").exists():
                serializer = MenuItemCreateSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({ "message" : "Menu Item added successfully" }, status=status.HTTP_201_CREATED)
            else:
                return Response({ "message" : "You do not have permission to add menu items" }, status=status.HTTP_403_FORBIDDEN)
    else: 
         if request.method == 'GET':
            items = MenuItem.objects.all()
            category_name = request.query_params.get('category')
            to_price = request.query_params.get('to_price')
            search = request.query_params.get('search')
            ordering = request.query_params.get('ordering')
            per_page = request.query_params.get('per_page', default=2)
            page = request.query_params.get('page', default=1)
            if category_name is not None:
                items = items.filter(category__name=category_name)
            if to_price is not None:
                items = items.filter(price__lte=to_price)
            if search is not None:
                items = items.filter(title__icontains=search)
            if ordering is not None:
                ordering_fields = ordering.split(',')
                items = items.order_by(*ordering_fields)
            paginator = PageNumberPagination()
            paginator.page_size = per_page
            try:
                result_page = paginator.paginate_queryset(items, request)
            except EmptyPage:
                result_page = []
            serializer = MenuItemSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    def get_permissions(self):
        permission_classes = [AllowAny]
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, ManagerRole]
        return[permission() for permission in permission_classes]
    def patch(self, request, pk):
        self.permission_classes = [IsAuthenticated, ManagerRole]
        self.throttle_classes = [UserRateThrottle]
        if MenuItem.objects.filter(id=pk).exists():
            serializer = MenuItemSerializer(MenuItem.objects.get(id=pk), data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({ "message" : "Menu Item updated successfully" }, status=status.HTTP_200_OK)
        else:
            return Response({ "message" : "Menu item does not exist" }, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, pk):
        self.permission_classes = [IsAuthenticated, ManagerRole]
        self.throttle_classes = [UserRateThrottle]
        if MenuItem.objects.filter(id=pk).exists():
            MenuItem.objects.get(id=pk).delete()
            return Response({ "message" : "Menu Item Removed" }, status=status.HTTP_200_OK)
        else:
            return Response({ "message" : "Menu item does not exist" }, status=status.HTTP_404_NOT_FOUND)

class UsersView(generics.CreateAPIView, generics.ListAPIView):
    queryset = User.objects.all()
    def get (self, request):
        serializer_class = UsersSerializer
        if request.user.groups.filter(name="Manager").exists():
            return Response(serializer_class(get_list_or_404(User.objects.all()), many=True).data)
        else:
            return Response({ "message" : "You are not authorized" }, status=status.HTTP_403_FORBIDDEN)
    def post(self, request):
        serializer_class = UserRegisterSerializer
        if User.objects.filter(username = request.data['username']).exists():
            return Response({ "message" : "User already exists" }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer_class(data=request.data).create(request.data), status=status.HTTP_201_CREATED )

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    def get(self, request):
        serializer_class = CurrentUserSerializer(request.user)
        return Response(serializer_class.data)

class ManagerUsersView(generics.ListAPIView, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ManagerUsersSerializer
    permission_classes = [ManagerRole]
    throttle_classes = [UserRateThrottle]
    def get (self, request):
        return Response(self.serializer_class(get_list_or_404(User.objects.filter(groups__name= 'Manager')) , many=True).data)
    def post(self, request):
        userExist = User.objects.filter(username = request.data['username'])
        managerGroup = Group.objects.get(name='Manager')
        if userExist.exists():
            user = User.objects.get(username = request.data['username'])
            user.save()
            user.groups.add(managerGroup)
            user.save()
            return Response({ "message" : "User added to manager group" }, status=status.HTTP_201_CREATED)
        else:
            return Response({ "message" : "User does not exist" }, status=status.HTTP_404_NOT_FOUND)

class ManagerUserRemoveView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = ManagerUsersSerializer
    permission_classes = [IsAuthenticated, ManagerRole]
    throttle_classes = [UserRateThrottle]
    def delete(self, request, pk):
        if User.objects.filter(pk = pk).exists():
            user = User.objects.get(pk = pk)
            user.groups.remove(Group.objects.get(name='Manager'))
            user.save()
            return Response({ "message" : "User removed from manager group" }, status=status.HTTP_200_OK)
        else:
            return Response({ "message" : "User does not exist" }, status=status.HTTP_404_NOT_FOUND)
        
class DeliverCrewUsersView(generics.ListAPIView, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = DeliverCrewUsersSerializer
    permission_classes = [ManagerRole]
    throttle_classes = [UserRateThrottle]
    def get (self, request):
        return Response(self.serializer_class(get_list_or_404(User.objects.filter(groups__name= 'Deliver Crew')) , many=True).data)
    def post(self, request):
        userExist = User.objects.filter(username = request.data['username'])
        deliverCrewGroup = Group.objects.get(name='Deliver Crew')
        if userExist.exists():
            user = User.objects.get(username = request.data['username'])
            user.save()
            user.groups.add(deliverCrewGroup)
            user.save()
            return Response({ "message" : "User added to deliver crew group" }, status=status.HTTP_201_CREATED)
        else:
            return Response({ "message" : "User does not exist" }, status=status.HTTP_404_NOT_FOUND)

class DeliverCrewUserRemoveView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = DeliverCrewUsersSerializer
    permission_classes = [IsAuthenticated, ManagerRole]
    throttle_classes = [UserRateThrottle]
    def delete(self, request, pk):
        if User.objects.filter(pk = pk).exists():
            user = User.objects.get(pk = pk)
            user.groups.remove(Group.objects.get(name='Deliver Crew'))
            user.save()
            return Response({ "message" : "User removed from deliver crew group" }, status=status.HTTP_200_OK)
        else:
            return Response({ "message" : "User does not exist" }, status=status.HTTP_404_NOT_FOUND)

class CartView(generics.ListAPIView, generics.CreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    def get(self, request):
        user = request.user
        queryset = Cart.objects.filter(user=user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request, *arg, **kwargs):
        serializer= CartCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        id = request.data['item']
        item = get_object_or_404(MenuItem, id=id)
        quantity = request.data['quantity']
        itemprice = int(quantity) * item.price
        if Cart.objects.filter(user=request.user).filter(item_id=id).exists():
            return Response({ "message" : "Item already exists in cart" }, status=status.HTTP_400_BAD_REQUEST)
        else:
            Cart.objects.update_or_create(user=request.user,  item_id=id, quantity=quantity, itemprice=itemprice)
            return Response({ "message" : "Item added in cart successfully" }, status=status.HTTP_201_CREATED)
    def delete(self, request, *args, **kwargs):
        user = request.user
        if 'item' in request.data:
            item = request.data.get('item')
            if item is not None:
                item_to_removed = Cart.objects.filter(user=user).filter(item_id=request.data['item'])
                if item_to_removed:
                    item_to_removed.delete()
                    return Response({ "message" : "Item removed from cart successfully" }, status=status.HTTP_200_OK)
                else:
                    return Response({ "message" : "Item does not exist in cart" }, status=status.HTTP_404_NOT_FOUND)
        else:
            Cart.objects.filter(user=user).delete()
            return Response({ "message" : "All items removed from cart successfully" }, status=status.HTTP_200_OK)
        
class OrdersView(generics.ListAPIView, generics.CreateAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    def get(self, request):
        if self.request.user.groups.filter(name='Manager').exists():
            customer = request.query_params.get('customer')
            deliver_crew = request.query_params.get('deliver_crew')
            status = request.query_params.get('status')
            ordering = request.query_params.get('ordering')
            queryset = Order.objects.all()
            if customer :
                queryset = queryset.filter(customer__username=customer)
            if deliver_crew :
                queryset = queryset.filter(deliver_crew__username=deliver_crew)
            if status:
                queryset = queryset.filter(status=status)
            if ordering:
                queryset = queryset.order_by(ordering)  
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            if self.request.user.groups.filter(name='Deliver Crew').exists():
                queryset = Order.objects.filter(deliver_crew=request.user)
                serializer = OrderDeliverCrewSerializer(queryset, many=True)
                return Response(serializer.data)
            else:
                customer = request.user
                queryset = Order.objects.filter(customer=customer)
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
    def post(self, request, format=None):
        if(Cart.objects.filter(user=request.user).count() == 0):
            return Response({ "message" : "Cart is empty" }, status=status.HTTP_400_BAD_REQUEST)
        else: 
            customer = request.user
            cart_items = Cart.objects.filter(user=customer)
            total = math.fsum([item.itemprice for item in cart_items])
            date = datetime.now()
            items_data = [
                {
                    "customer_id": customer.id,
                    "item_id": item.item.id,
                    "quantity": item.quantity,
                }
                for item in cart_items
            ]
            order_data = {
                "customer_id": customer.id,
                "customer": customer.id,
                "total": total,
                "date": date,
                "items": items_data,
            }
            serialized_order = OrderSerializer(data=order_data)
            serialized_order.is_valid(raise_exception=True)
            serialized_order.save()
            Cart.objects.filter(user=customer).delete()
            return Response({ "message" : "Order created successfully" }, status=status.HTTP_201_CREATED)

class OrderView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    def get(self, request, pk):
        if self.request.user.groups.filter(name='Manager').exists():
            order = Order.objects.filter(pk=pk).first()
            if order is not None:
                return Response(self.get_serializer(order).data)
            else:
                return Response({ "message" : "Order does not exist" }, status=status.HTTP_404_NOT_FOUND)
        else:
            customer_orders = Order.objects.filter(customer=request.user)
            order = customer_orders.filter(pk=pk).first()
            if order is not None:    
                return Response(self.get_serializer(order).data)
            else:
                return Response({ "message" : "Order does not exist" }, status=status.HTTP_404_NOT_FOUND)
    def patch(self, request, pk):
        if self.request.user.groups.filter(name='Deliver Crew').exists() :
            order = Order.objects.filter(pk=pk).first()
            if order is not None:
                if len(request.data) > 2:
                    return Response({ "message" : "You can only update the status of the order" }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if 'status' in request.data:
                        serializer = OrderUpdateDeliverCrewSerializer(order, data=request.data, partial=True)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        return Response({ "message" : "Order updated successfully" }, status=status.HTTP_200_OK)
                    else:
                        return Response({ "message" : "There's no status in the request" }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({ "message" : "Order does not exist" }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if self.request.user.groups.filter(name='Manager').exists() :
                order = Order.objects.get(pk=pk)
                if order is not None:
                    if 'items' in request.data: 
                        items_data = request.data['items']
                        order_data = [ { "item" : OrderItemCartSerializer(MenuItemSerializer(MenuItem.objects.get(id=item['item'])).data).data, "quantity" : item['quantity'] } for item in items_data]
                        total = str(math.fsum([ int(item['quantity']) * Decimal(item['item']['price']) for item in order_data]))
                        request.data['total'] = total
                        request.data['customer_id'] = order.customer.id
                        serializer = OrderUpdateCompleteManagerSerializer(order, data=request.data, partial=True)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        return Response({ "message" : "Order updated successfully" }, status=status.HTTP_200_OK)
                    else:
                        request.data['customer_id'] = order.customer.id
                        serializer = OrderUpdatePartialManagerSerializer(order, data=request.data, partial=True)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        return Response({ "message" : "Order updated successfully" }, status=status.HTTP_200_OK)
                else:
                    return Response({ "message" : "Order does not exist" }, status=status.HTTP_404_NOT_FOUND)
            else:
                order = Order.objects.get(pk=pk)
                if order is not None:
                    if len(request.data) > 1:
                        return Response({ "message" : "Unauthorized to update the order" }, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        if 'items' in request.data:
                            items_data = request.data['items']
                            order_data = [ { "item" : OrderItemCartSerializer(MenuItemSerializer(MenuItem.objects.get(id=item['item'])).data).data, "quantity" : item['quantity'] } for item in items_data]
                            total = str(math.fsum([ int(item['quantity']) * Decimal(item['item']['price']) for item in order_data]))
                            request.data['total'] = total
                            request.data['customer_id'] = order.customer.id
                            serializer = OrderUpdateCustomerSerializer(order, data=request.data, partial=True)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            return Response({ "message" : "Order updated successfully" }, status=status.HTTP_200_OK)
                        else: 
                            return Response({ "message" : "Unauthorized to update the order" }, status=status.HTTP_401_UNAUTHORIZED)                   
    def delete(self, request, pk):
        if self.request.user.groups.filter(name='Manager').exists() :
            order = Order.objects.filter(pk=pk).first()
            if order is not None:
                order.delete()
                return Response({ "message" : "Order deleted successfully" }, status=status.HTTP_200_OK)
            else:
                return Response({ "message" : "Order does not exist" }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({ "message" : "You are not authorized to delete this order" }, status=status.HTTP_401_UNAUTHORIZED)