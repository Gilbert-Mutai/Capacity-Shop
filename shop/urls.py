from django.urls import path

from . import views

urlpatterns = [
	#Leave as empty string for base url
	path('', views.store, name="store"),
	path('category/', views.categories, name="category"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
	path("search/", views.search, name="search"),
	path('more/<str:pk>/', views.viewMore, name="more"),

	path("register/",views.RegistrationView.as_view(), name="register"),
	path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),

	


	

	# path("search/", views.search, name="search"),

]