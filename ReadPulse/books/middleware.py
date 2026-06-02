from django.shortcuts import redirect
from django.conf import settings
class LoginRequiredMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        p=request.path
        allowed=['/accounts/','/static/','/admin/login/']
        if not request.user.is_authenticated and not any(p.startswith(x) for x in allowed):
            return redirect(settings.LOGIN_URL)
        return self.get_response(request)
