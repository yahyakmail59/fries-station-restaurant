from pathlib import Path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.static import serve
from django.urls import include, path

admin.site.site_header = 'فرايز ستيشن — الإدارة'
admin.site.site_title = 'Fries Station Admin'
admin.site.index_title = 'إدارة محتوى الموقع والطلبات'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('restaurant.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif settings.SERVE_MEDIA:
    urlpatterns += [
        path(
            f'{settings.MEDIA_URL.strip("/")}/<path:path>',
            serve,
            {'document_root': Path(settings.MEDIA_ROOT), 'show_indexes': False},
            name='media',
        )
    ]
