from django.shortcuts import render
from django.http import HttpResponse
def index(request):
	return HttpResponse("Primul raspuns")

def info(request):
    continut_info = """
                <h1>Informatii despre server </h1>
                    <p>salut</p>
                """
    context = {
        'continut_info': continut_info
    }
    return render(request, 'aplicatie_biciclete/info.html', context )
    
l=[]
def pag2(request):
    global l
    a=request.GET.get("a",10)
    print(request.GET)
    l.append(a)
    return HttpResponse(f"<b>Am primit</b>: {l}")
