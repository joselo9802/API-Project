from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MenuItem, Category, Cart, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "category", "featured"]

class MenuItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "category", "featured"]

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "username", "email"]

class UserRegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = ["name", "email", "username", "password"]
        extra_kwargs = {
            "password": {
                "write_only": True,
            }
        }
    def create(self, validated_data):
        user = User( 
        username = validated_data['username'],
        email = validated_data['email'],
        first_name = validated_data['name'],
        password = validated_data['password'],
        )
        user.save()
        return {
            "name" : user.first_name,
            "email" : user.email,
            "username" : user.username,
        }

class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "username", "email"]

class ManagerUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "username", "email"]

class DeliverCrewUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "username", "email"]

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "title", "price"]

class CartSerializer(serializers.ModelSerializer):
    item = CartItemSerializer()
    class Meta:
        model = Cart
        fields = ["item", "quantity", "itemprice"]
        extra_kwargs = {
            "quantity": {
                "min_value": 1,
            },
        }

class OrderItemCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["title", "price"]


class CartCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["item", "quantity"]
        extra_kwargs = {
            "quantity": {
                "min_value": 1,
            },
        }

class CustomerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "email"]

class DeliverCrewOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "email"]

class OrderItemSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True)
    item_id = serializers.IntegerField(write_only=True)
    item = OrderItemCartSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ["customer_id", "item_id", "item", "quantity"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = CustomerOrderSerializer(read_only=True)
    deliver_crew = DeliverCrewOrderSerializer(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "customer_id", "customer", "deliver_crew", "items", "total", "date", "status"]
    
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        customer_id = validated_data.pop("customer_id")
        customer = User.objects.get(id=customer_id)
        order = Order.objects.create(customer=customer, **validated_data)
        for item in items_data:
            item["customer_id"] = customer_id
            item_id = item.pop("item_id")
            quantity = item.pop("quantity")
            item, created = OrderItem.objects.get_or_create(customer_id=customer_id, item_id=item_id, defaults={'quantity': quantity})
            if not created:
                item.quantity = quantity
                item.save()
            order.items.add(item)
        return order

class OrderItemUpdateSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True)
    item = serializers.IntegerField(write_only=True)
    class Meta:
        model = OrderItem
        fields = ["customer_id", "item_id", "item", "quantity"]

class OrderUpdateCompleteManagerSerializer(serializers.ModelSerializer):
    items = OrderItemUpdateSerializer(many=True)
    customer_id = serializers.IntegerField(write_only=True)
    total = str
    class Meta:
        model = Order
        fields = ["id", "customer_id", "customer", "deliver_crew", "items", "total", "date", "status"]
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop("items")
        customer_id = validated_data.pop("customer_id")
        current_item_ids = set(instance.items.values_list("item", flat=True))
        new_item_ids = set(item["item"] for item in items_data)
        items_to_delete = current_item_ids - new_item_ids
        OrderItem.objects.filter(item__in=items_to_delete).delete()
        instance.customer_id = customer_id
        instance.status = validated_data.get('status', instance.status)
        instance.total = validated_data.get('total', instance.total)
        instance.date = validated_data.get('date', instance.date)
        instance.deliver_crew = validated_data.get('deliver_crew', instance.deliver_crew)
        instance.save()
        for item in items_data:
            item["customer_id"] = customer_id
            item_id = item.get("item")
            quantity = item.get("quantity")
            item, created = OrderItem.objects.get_or_create(customer_id=customer_id, item_id=item_id, defaults={'quantity': quantity})
            if not created:
                item.quantity = quantity
                item.save()
            instance.items.add(item)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'total' in representation:
            representation['total'] = str(representation['total'])
        return representation

class OrderUpdatePartialManagerSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Order
        fields = ["id", "customer_id", "customer", "deliver_crew", "date", "status"]
    
    def update(self, instance, validated_data):
        instance.customer_id = validated_data.get('customer_id', instance.customer_id)
        instance.status = validated_data.get('status', instance.status)
        instance.total = validated_data.get('total', instance.total)
        instance.date = validated_data.get('date', instance.date)
        instance.deliver_crew = validated_data.get('deliver_crew', instance.deliver_crew)
        instance.save()
        return instance
    
class OrderCustomerSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Order
        fields = ["id", "customer_id", "deliver_crew", "items", "total", "date", "status"]

class OrderUpdateCustomerSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True)
    items = OrderItemUpdateSerializer(many=True)
    class Meta:
        model = Order
        fields = ["id", "customer_id", "deliver_crew", "items", "total", "date", "status"]

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items")
        customer_id = validated_data.pop("customer_id")
        current_item_ids = set(instance.items.values_list("item", flat=True))
        new_item_ids = set(item["item"] for item in items_data)
        items_to_delete = current_item_ids - new_item_ids
        OrderItem.objects.filter(item__in=items_to_delete).delete()
        instance.customer_id = customer_id
        instance.total = validated_data.get('total', instance.total)
        instance.save()
        for item in items_data:
            item["customer_id"] = customer_id
            item_id = item.get("item")
            quantity = item.get("quantity")
            item, created = OrderItem.objects.get_or_create(customer_id=customer_id, item_id=item_id, defaults={'quantity': quantity})
            if not created:
                item.quantity = quantity
                item.save()
            instance.items.add(item)
        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'total' in representation:
            representation['total'] = str(representation['total'])
        return representation

class OrderDeliverCrewSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = CustomerOrderSerializer(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Order
        fields = ["id", "customer_id", "customer", "items", "total", "date", "status"]

class OrderUpdateDeliverCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]
    
    def update(self, instance, validated_data):
        instance.status = validated_data.get("status", instance.status)
        instance.save()
        return instance

        
