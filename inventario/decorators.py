from django.http import HttpResponse
from django.shortcuts import redirect

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            
            grupo = None
            if request.user.groups.exists():
                grupo = request.user.groups.all()[0].name
            
            print(grupo)
                
            return view_func(request, *args, **kwargs)
            """
            else:
                return HttpResponse('Acceso No Autorizado')
            """
        return wrapper_func
    return decorator