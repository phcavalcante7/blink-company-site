from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from camisetas.views import webhook_stripe

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1) webhook primeiro
    path('webhook/stripe/', webhook_stripe, name='webhook_stripe'),

    # 2) depois o include geral
    path('', include('camisetas.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

