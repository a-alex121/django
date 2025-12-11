from django.urls import path
from . import views
urlpatterns = [
	path("", views.index, name="index"),
	path("info", views.info, name="info"),
    path("pag2", views.pag2, name="pag2"),
	path("log", views.afis_log, name="log"),
	path("despre", views.despre, name="despre"),
    path("produse", views.produse, name="produse"),
    path("contact", views.contact, name="contact"),
    path("cos_virtual", views.in_lucru, name="cos_virtual"),
    # Ruta pentru categoriile din meniu
    path("produse/<str:nume_categorie>", views.in_lucru, name="produse_pe_categorie"),
]
