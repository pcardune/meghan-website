from django.conf.urls.defaults import patterns
from meghanurback.views import admin

urlpatterns = patterns(
    'meghanurback.views',
    (r'^$', 'front_page'),
    (r'^bio/$', 'bio'),
    (r'^status/$', 'status'),

    (r'^gallery/$', 'redirect_to_gallery'),
    (r'^gallery/([a-zA-Z0-9_-]+)/$', 'gallery'),
    (r'^gallery/([a-zA-Z0-9_-]+)/edit/$', 'edit_gallery'),

    (r'^file/([\.a-zA-Z0-9_-]+)/$', 'file_upload'),
    (r'^file/([\.a-zA-Z0-9_-]+)/edit/$', 'edit_file_upload'),

    (r'^page/([a-zA-Z0-9_-]+)/$', 'content_page'),
    (r'^page/([a-zA-Z0-9_-]+)/edit/$', 'edit_content_page'),

    (r'^links/$', 'links'),

    (r'^events/$', 'news'),

    (r'^admin/$', 'admin_page'),
    (r'^admin/news/([a-zA-Z0-9_-]+)/delete/$', 'delete_news_item'),
    (r'^admin/news/([a-zA-Z0-9_-]+)/edit/$', 'edit_news_item'),
)

urlpatterns += patterns(
    '',

    (r'^admin/delicious/$', admin.DeliciousSettingsHandler.view),
    (r'^admin/news/$', admin.NewsAdminHandler.view),

)
