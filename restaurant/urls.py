from django.urls import path

from . import views, views_cashier, views_dashboard, views_order, views_panel

app_name = 'restaurant'

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu_page, name='menu'),
    path('reservation/', views.create_reservation, name='create_reservation'),
    path('order/', views_order.create_order, name='create_order'),
    path('o/<str:token>/', views_order.order_detail, name='order_detail'),
    path('o/<str:token>/receipt.png', views_order.order_receipt, name='order_receipt'),
    path('dashboard/', views_dashboard.dashboard, name='dashboard'),
    path('dashboard/cashier/', views_cashier.cashier, name='cashier'),
    path(
        'dashboard/reservations/<int:pk>/status/',
        views_dashboard.update_reservation_status,
        name='dashboard_reservation_status',
    ),
    path('dashboard/settings/', views_panel.site_settings, name='panel_settings'),
    path('dashboard/<slug:slug>/', views_panel.section_list, name='panel_list'),
    path('dashboard/<slug:slug>/new/', views_panel.section_form, name='panel_add'),
    path('dashboard/<slug:slug>/<int:pk>/', views_panel.section_form, name='panel_edit'),
    path('dashboard/<slug:slug>/<int:pk>/toggle/', views_panel.section_toggle, name='panel_toggle'),
    path('dashboard/<slug:slug>/<int:pk>/delete/', views_panel.section_delete, name='panel_delete'),
    path('robots.txt', views.robots_txt, name='robots'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap'),
]
