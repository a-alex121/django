from datetime import datetime 

ISTORIC_CERERI = []

class Accesare:
    def __init__(self, get_response):
        self.get_response  = get_response
        self.cereri_cnt = 0

    def __call__(self, request):
        self.cereri_cnt += 1

        date_cerere = {
            'id': self.cereri_cnt,
            'path': request.path,
            'method': request.method,
            'ip': request.META.get('REMOTE_ADDR'),
            'time': datetime.now()
        }

        ISTORIC_CERERI.append(date_cerere)

        raspuns = self.get_response(request)
        return raspuns