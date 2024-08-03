from django.urls import path
from. import views

urlpatterns = [
    path('menu-items/category', views.MenuItemsCategoryView.as_view()),
    path('menu-items/category/<int:pk>', views.MenuItemsSingleCategoryView.as_view()),
    path('menu-items', views.menu_items),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
    path('orders', views.OrdersView.as_view()),
    path('orders/<int:pk>', views.OrderView.as_view()),
    path('users', views.UsersView.as_view()),
    path('users/me', views.CurrentUserView.as_view()),
    path('groups/manager/users', views.ManagerUsersView.as_view()),
    path('groups/manager/users/<int:pk>', views.ManagerUserRemoveView.as_view()),
    path('groups/deliver-crew/users', views.DeliverCrewUsersView.as_view()),
    path('groups/deliver-crew/users/<int:pk>', views.DeliverCrewUserRemoveView.as_view())
]