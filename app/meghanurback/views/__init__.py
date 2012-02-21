import logging
from collections import defaultdict
from google.appengine.ext import db

from django.shortcuts import render_to_response
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from meghanurback import etsy, flickr, models, forms, conf, delicious
from meghanurback.views.utils import require_admin, with_context


@with_context
def front_page(request):
    return 'front_page.html', locals()

@with_context
def news(request):
    news_items = list(db.GqlQuery("SELECT * FROM NewsItem ORDER BY start_date DESC"))
    return 'news.html', locals()

@with_context
def bio(request):
    return HttpResponseRedirect('/page/bio/')
#    etsy_details = etsy.get_user_details(conf.ETSY_ACCOUNT)
#    bio_sections = etsy_details.get('bio','').split('\n')
#    return 'bio.html', locals()

def redirect_to_gallery(request):
    for ps in models.Photoset.all().order('navigation_order'):
        if ps.enabled:
            return HttpResponseRedirect(ps.absolute_url)
    raise Http404()

@with_context
def gallery(request, navigation_url):
    photoset = models.Photoset.all().filter('navigation_url = ',navigation_url.lower()).get()
    if photoset is None:
        raise Http404()

    photoset_nav = []
    for ps in models.Photoset.all().order('navigation_order'):
        if not ps.enabled:
            continue
        photoset_nav.append({'photoset':ps,
                             'selected':request.path.startswith(ps.absolute_url)})

    photos = flickr.get_photoset(photoset_id=photoset.photoset_id)
    return 'gallery.html', {'photos':photos,
                            'photoset':photoset,
                            'photoset_nav':photoset_nav}

@with_context
def links(request):
    all_posts = delicious.posts_all()
    by_tag = defaultdict(list)
    for post in all_posts:
        for tag in post['tags']:
            by_tag[tag].append(post)
    tags = [{'name':tag,'posts':posts} for tag, posts in by_tag.iteritems()]
    return 'links.html', {'tags':tags}


def file_upload(request, navigation_url):
    logging.info("Handling file upload request")
    file_upload = models.FileUpload.from_nav(navigation_url)
    response = HttpResponse(file_upload.data, mimetype=file_upload.content_type)
    response['Content-Disposition'] = 'attachement; filename='+file_upload.filename
    return response

@with_context
def content_page(request, navigation_url):
    page = models.Page.from_nav(navigation_url)
    return 'page.html', locals()

def status(request):
    etsy_ping = False
    ping = etsy.ping()
    if ping:
        etsy_ping = ping[0]
    photos = flickr.get_public_photos()
    total_photos = len(photos)
    return render_to_response('status.html', locals())


class Admin(object):

    def handle_flickr_gallery_add(self, request):
        if request.POST.get('add') == 'flickr_gallery':
            form = forms.PhotosetForm(request.POST)
            if form.is_valid():
                cd = form.clean_data
                new_photoset = models.Photoset(
                    navigation_url = cd.get('navigation_url').lower(),
                    navigation_title = cd.get('navigation_title'),
                    photoset_id = cd.get('photoset_id'),
                    navigation_order = cd.get('navigation_order'),
                    enabled = False)
                new_photoset.put()
        else:
            form = forms.PhotosetForm()
        return form

    def handle_file_upload_add(self, request):
        if request.POST.get('add') == 'file_upload':
            form = forms.FileUploadForm(request.POST)
            if form.is_valid():
                cd = form.clean_data
                new_file_upload = models.FileUpload()

                nav = models.NavigationItem()
                nav.title = cd['navigation_title']
                nav.order = cd['navigation_order']
                nav.url = cd['navigation_url']
                nav.put()

                upload_data = request.FILES.get('upload_data')
                new_file_upload.filename = upload_data['filename']
                new_file_upload.data = db.Blob(upload_data['content'])
                new_file_upload.content_type = upload_data['content-type']
                new_file_upload.navigation_item = nav
                new_file_upload.put()
        else:
            form = forms.FileUploadForm()
        return form

    def handle_page_add(self, request):
        if request.POST.get('add') == 'page':
            form = forms.PageAddForm(request.POST)
            if form.is_valid():
                cd = form.clean_data
                new_file_upload = models.FileUpload()

                nav = models.NavigationItem()
                nav.title = cd['navigation_title']
                nav.order = cd['navigation_order']
                nav.url = cd['navigation_url']
                nav.put()

                new_page = models.Page()
                new_page.navigation_item = nav
                new_page.content = "Replace this content"
                new_page.put()
        else:
            form = forms.PageAddForm()
        return form

    def handle_table_actions(self, request):
        enableKey = request.POST.get("enable")
        disableKey = request.POST.get("disable")
        deleteKey = request.POST.get("delete")
        if enableKey:
            photoset = db.get(enableKey)
            photoset.enabled = True
            photoset.put()
        if disableKey:
            photoset = db.get(disableKey)
            photoset.enabled = False
            photoset.put()
        if deleteKey:
            photoset = db.get(deleteKey)
            photoset.delete()


    add_handlers = {'flickr_gallery':handle_flickr_gallery_add,
                    'file_upload':handle_file_upload_add,
                    'page':handle_page_add}

    def __call__(self, request):
        flickr_form = self.handle_flickr_gallery_add(request)
        file_upload_form = self.handle_file_upload_add(request)
        page_form = self.handle_page_add(request)

        self.handle_table_actions(request)

        photoset_list = flickr.get_photoset_list()
        photosets = models.Photoset.all()
        photosets.order('navigation_order')

        uploads = models.FileUpload.all()
        pages = models.Page.all()
        return 'admin.html', locals()

_admin = Admin()

@require_admin
@with_context
def admin_page(request):
    return _admin(request)

@require_admin
def delete_news_item(request, news_item_key):
    db.get(news_item_key).delete()
    return HttpResponseRedirect("/admin/news")

@require_admin
@with_context
def edit_gallery(request, navigation_url):
    photosets = list(db.GqlQuery("SELECT * FROM Photoset WHERE navigation_url = :1", navigation_url.lower()))
    if len(photosets) == 0:
        raise Http404()
    photoset = photosets[0]
    if request.method == 'POST':
        form = forms.PhotosetForm(request.POST)
        if form.is_valid():
            cd = form.clean_data
            photoset.photoset_id = cd['photoset_id']
            photoset.navigation_url = cd['navigation_url']
            photoset.navigation_title = cd['navigation_title']
            photoset.navigation_order = cd['navigation_order']
            photoset.enabled = cd['enabled']
            photoset.about_text = cd['about_text']
            photoset.put()
            return HttpResponseRedirect('/admin/')
    else:
        form = forms.PhotosetForm(initial=dict(photoset_id=photoset.photoset_id,
                                               navigation_url=photoset.navigation_url,
                                               navigation_title=photoset.navigation_title,
                                               navigation_order=photoset.navigation_order,
                                               enabled=photoset.enabled,
                                               about_text=photoset.about_text,))
    return 'edit_gallery.html', dict(photoset=photoset, form=form)

@require_admin
@with_context
def edit_file_upload(request, navigation_url):
    file_upload = models.FileUpload.from_nav(navigation_url)
    if request.method == 'POST':
        form = forms.FileUploadForm(request.POST)
        if form.is_valid():
            for key, val in form.clean_data.items():
                setattr(file_upload, key, val)
            file_upload.put()
            return HttpResponseRedirect('/admin/')
    else:
        form = forms.FileUploadForm(initial=dict(navigation_url=file_upload.navigation_url,
                                                 navigation_title=file_upload.navigation_title,
                                                 navigation_order=file_upload.navigation_order,
                                                 enabled=file_upload.enabled))
    return 'edit_file_upload.html', dict(file_upload=file_upload, form=form)


@require_admin
@with_context
def edit_content_page(request, navigation_url):
    page = models.Page.from_nav(navigation_url)
    if request.method == 'POST':
        form = forms.PageForm(request.POST)
        if form.is_valid():
            for key, val in form.clean_data.items():
                setattr(page, key, val)
            page.put()
            return HttpResponseRedirect('/admin/')
    else:
        form = forms.PageForm(initial=dict(navigation_url=page.navigation_url,
                                           navigation_title=page.navigation_title,
                                           navigation_order=page.navigation_order,
                                           enabled=page.enabled,
                                           content=page.content))
    return 'edit_page.html', dict(page=page, form=form)

