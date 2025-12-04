from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("product/add/", views.product_add, name="product_add"),
    path("product/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("product/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("product/<int:pk>/json/", views.product_json, name="product_json"),

    path("cart/", views.view_cart, name="view_cart"),
    path("cart/state/", views.cart_state, name="cart_state"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="cart_add"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path("cart/update/<int:pk>/<str:action>/", views.cart_update_quantity, name="cart_update_quantity"),

    path("admin/", views.admin_panel, name="admin_panel"),
    path("admin/user/<int:user_id>/cart/", views.user_cart, name="user_cart"),
    path("admin/user/<int:user_id>/toggle-admin/", views.toggle_admin_role, name="toggle_admin_role"),
    
    # Статистика
    path("stats/", views.stats_view, name="stats"),
    path("stats/data/", views.stats_data, name="stats_data"),
    
    # Wishlist
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/state/", views.wishlist_state, name="wishlist_state"),
    path("wishlist/toggle/<int:product_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    
    # Профиль
    path("profile/", views.profile_view, name="profile"),
]