from django.urls import path,include

from . import views

urlpatterns = [
	path('', views.store, name="store"),
	path('', include("django.contrib.auth.urls")),
    path("register/", views.register, name="register"),

	path('category/', views.categories, name="category"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
	path("search/", views.search, name="search"),

	path('more/<str:pk>/', views.viewMore, name="more"),
	path('profile/<str:pk>/', views.profile, name="profile"),

]