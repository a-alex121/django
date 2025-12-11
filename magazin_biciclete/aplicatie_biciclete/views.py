from django.shortcuts import render
from django.http import HttpResponse
from . import middleware
import logging
# Asigură-te că modelul Categorie există în models.py sau șterge importul dacă nu e folosit
# from .models import Categorie 
import locale
from datetime import datetime

def index(request):
    return HttpResponse("Primul raspuns")

l=[]
def pag2(request):
    global l
    a=request.GET.get("a",10)
    print(request.GET)
    l.append(a)
    return HttpResponse(f"<b>Am primit</b>: {l}")

# Setarea localizării pentru limba română
try:
    locale.setlocale(locale.LC_TIME, 'romanian')
except locale.Error:
    # Fallback dacă sistemul nu are localizarea instalată
    pass

def afis_data(data):
    if(not data):
        return ""
    else:
        today = datetime.now()
        if(data == "zi"):
            return f"{today.day} {today.strftime('%B').capitalize()} {today.year}"
        elif(data == 'timp'):
            return f"{today.hour}:{today.minute}:{today.second}"
        else:
            return f"{today.strftime('%A').capitalize()}, {today.day} {today.strftime('%B').capitalize()} {today.year}"

# Integrarea în view-ul 'info'
def info(request):
    keys = list(request.GET.keys())
    count = len(keys)
    
    if count > 0:
        nume_param = ", ".join(keys)
    else:
        nume_param = "niciun parametru"
    
    # Corecție: Această linie nu mai este indentată în 'else', ci se execută mereu
    param_section = f"<h2>Parametri</h2><p>Numar parametri: {count}</p><p>Nume parametri: {nume_param}</p>"
    
    data_param = request.GET.get("data")
    
    continut_info = f"""
                    <h1>Informatii despre server </h1>
                        <p>{afis_data(data_param)}</p>
                        {param_section}
                    """
    return render(request, 'templates/aplicatie_biciclete/info.html', {'continut_info': continut_info} )

class Accesare:
    id_cnt=0 
    
    def __init__(self, ip_client, url, data):
        Accesare.id_cnt+=1
        self.id=Accesare.id_cnt
        self.ip_client=ip_client
        self.url=url
        self.data=data
    
    def lista_parametri(self, request):
        lista_finala = []
        for cheie in request.GET.keys():
            valori = request.GET.getlist(cheie)
            if not valori:
                valoare = None
            elif len(valori)==1:
                valoare = valori[0]
            else:
                valoare = valori
            lista_finala.append((cheie, valoare))
        return lista_finala
    
    def get_url(self, request):
        full_url = request.get_full_path()
        return full_url
    
    def format_data(self, format_data):
        if(isinstance(self.data, str)):
            data_obj = datetime.strptime(self.data, "%d-%m-%Y %H:%M:%S")
        else:
            data_obj = self.data
        return data_obj.strftime(format_data)
    
    def pagina(self):
        string=self.url
        if '?' in string:
            string=string.split('?', 1)[0]
        if not string.startswith('/'):
            string = string + '/'
        return string or '/'

def afis_log(request):
    output_html = []

    # Preluare parametri
    param_ultimele = request.GET.get("ultimele", None)
    param_accesari = request.GET.get("accesari", None)
    dubluri_param = request.GET.get("dubluri", None)
    param_tabel = request.GET.get("tabel", None)
    
    # Logică dubluri
    dubluri = dubluri_param is not None and dubluri_param.lower() == 'true'

    # Istoricul complet
    logs = middleware.ISTORIC_CERERI
    numar_logs = len(logs)

    # Lista de lucru (filtrată)
    logs_de_afisat = logs.copy()

    # 1. Filtrare după ID-uri (dacă există parametrul iduri)
    iduri_raw = request.GET.getlist("iduri")
    if iduri_raw:
        ids_de_cautat = []
        for secventa in iduri_raw:
            for val in secventa.split(','):
                try:
                    id_int = int(val.strip())
                except ValueError:
                    continue
                
                # Adăugăm ID-ul dacă sunt permise dublurile SAU dacă nu a fost deja adăugat
                if dubluri or (id_int not in ids_de_cautat):
                    ids_de_cautat.append(id_int)
        
        # Reconstruim lista de loguri pe baza ID-urilor găsite, în ordinea cerută
        logs_filtrate_id = []
        for id_tinta in ids_de_cautat:
            gasit = False
            for log in logs:
                if log.get('id') == id_tinta:
                    logs_filtrate_id.append(log)
                    gasit = True
                    # Dacă nu sunt permise dubluri în sursă (nu e cazul aici, ID-urile sunt unice), break
                    break 
            if not gasit:
                # Opțional: putem adăuga un mesaj de eroare în output pentru ID-uri lipsă
                pass 
        
        # Actualizăm lista de afișare
        logs_de_afisat = logs_filtrate_id

    # 2. Filtrare după 'ultimele' (se aplică peste lista rezultată din ID-uri sau cea completă)
    mesaj_depasire = None
    if param_ultimele is not None:
        try:
            n = int(param_ultimele)
            if n <= 0:
                return HttpResponse("<p>Eroare: Parametrul 'ultimele' trebuie sa fie un numar intreg pozitiv.</p>")
            
            nr_curent = len(logs_de_afisat)
            if n > nr_curent:
                mesaj_depasire = f"<p>Exista doar {nr_curent} accesari fata de {n} cerute</p>"
            else:
                logs_de_afisat = logs_de_afisat[-n:]
                
        except (ValueError, TypeError):
            return HttpResponse("<p>Eroare: Parametrul 'ultimele' trebuie sa fie un numar intreg.</p>")

    # --- GENERARE HTML ---

    # Cerința: Parametrul accesari="nr"
    if param_accesari == 'nr':
        output_html.append(f"<h3>Numar total de accesari: {numar_logs}</h3>")

    # Cerința: Parametrul accesari="detalii"
    if param_accesari == "detalii":
        output_html.append(f"<h3>Detalii accesari (data si ora):</h3>")
        output_html.append("<ul>")
        for log in logs: # Cerința zice detalii accesari (probabil toate), folosim logs complet
            time = log.get('time').strftime("%d-%m-%Y %H:%M:%S")
            output_html.append(f"<li>{time}</li>")
        output_html.append("</ul>")

    # Afișare TABEL sau LISTĂ implicită
    if param_tabel is not None:
        # --- TABEL ---
        coloane_valide = ['id', 'path', 'method', 'ip', 'time']
        if param_tabel == "tot":
            coloane = coloane_valide
        else:
            coloane = [col.strip() for col in param_tabel.split(',')]
            for col in coloane:
                if col not in coloane_valide:
                    return HttpResponse(f"<p>Eroare: Coloana invalida '{col}' in parametrul 'tabel'.</p>")
        
        output_html.append("<table border='1' cellpadding='5' cellspacing='0'>")
        # Antet
        output_html.append("<tr>")
        for col in coloane:
            output_html.append(f"<th>{col.capitalize()}</th>")
        output_html.append("</tr>")
        
        # Rânduri (folosind lista filtrată!)
        for log in logs_de_afisat:
            output_html.append("<tr>")
            for col in coloane:
                val = log.get(col)
                if col == 'time' and val:
                    val = val.strftime("%Y-%m-%d %H:%M:%S")
                if val is None: val = ""
                output_html.append(f"<td>{val}</td>")
            output_html.append("</tr>")
        output_html.append("</table>")
        
    else:
        # --- LISTĂ IMPLICITĂ (paragrafe) ---
        # Se afișează dacă nu s-a cerut tabel
        for log in logs_de_afisat:
            time_str = log.get("time").strftime("%d-%m-%Y %H:%M:%S")
            output_html.append(f'<p>Path: {log.get("path")}, Method: {log.get("method")}, IP: {log.get("ip")}, Time: {time_str}</p>')

    # Mesaj depășire (dacă e cazul)
    if mesaj_depasire:
        output_html.append(mesaj_depasire)

    # --- Cerința 5: Statistici (pe istoricul complet) ---
    if logs:
        frecventa_pagini = {}
        for log in logs:
            path = log.get("path", "/")
            clean_path = path.split("?")[0] 
            if clean_path in frecventa_pagini:
                frecventa_pagini[clean_path] += 1
            else:
                frecventa_pagini[clean_path] = 1
        
        if frecventa_pagini:
            pagina_max = max(frecventa_pagini, key=frecventa_pagini.get)
            nr_max = frecventa_pagini[pagina_max]
            
            pagina_min = min(frecventa_pagini, key=frecventa_pagini.get)
            nr_min = frecventa_pagini[pagina_min]
            
            output_html.append("<h3>Statistici accesari: </h3>")
            output_html.append(f"<p>Pagina cu cele mai multe accesari: {pagina_max} ({nr_max} accesari)</p>")
            output_html.append(f"<p>Pagina cu cele mai putine accesari: {pagina_min} ({nr_min} accesari)</p>")

    return HttpResponse("".join(output_html))