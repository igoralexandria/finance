from django.urls import path
from . import views

urlpatterns = [
    path('definir_contas/', views.definir_contas, name="definir_contas"),
    path('ver_contas/', views.ver_contas, name="ver_contas"),
    path('pagar_conta/<int:conta_id>/', views.pagar_conta, name='pagar_conta'),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('definir_mensais/', views.definir_mensais, name="definir_mensais"),
]
