from django.urls import path
from . import views


urlpatterns = [
    path(
        'create-checkout-session/<int:product_id>/',
        views.CreateCheckoutSessionView.as_view(),
        name='create-checkout-session'
    ),
    path('success', views.SuccessView.as_view(), name='success'),
    path('cancel/', views.CancelView.as_view(), name='cancel'),
]  