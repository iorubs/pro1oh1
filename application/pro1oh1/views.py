from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from authentication.models import Account
from django.http import HttpResponse

class IndexView(TemplateView):
    template_name = 'index.html'

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)

def userCountView(request):
    """
    Return number of registered users.
    """
    queryset = Account.objects.all()
    return HttpResponse(str(len(queryset)))
