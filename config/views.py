from django.http import HttpResponse


def about_blank(request):
    return HttpResponse("about:blank")
