from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.homepage, name='home'),
    path('o-kompanii/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),
    path('kontakty/', views.contacts, name='contacts'),
    path('kontakty/spasibo/', views.contacts_success, name='contacts_success'),
    path('our-people/', views.our_people, name='our_people'),
    path('our-leaders/', views.our_leaders, name='our_leaders'),
    path('investory/', views.investors, name='investors'),
    path('rekomendatsii-po-stroitelstvu/', views.construction_recommendations, name='construction_recommendations'),
    path('investoram/<slug:slug>/', views.investor_page, name='investor_page'),
]
