from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import ListView
from django.core.mail import send_mail
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from taggit.models import Tag

from blogger.settings import EMAIL_HOST_USER

from .models import Post
from .forms import EmailPostForm, CommentForm, SearchForm



def post_share_view(request, post_id) :
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST' :
        form = EmailPostForm(request.POST)
        if form.is_valid() :
            clean_data = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{clean_data['name']} recommends you to read"
            message =   f"Read '{post.title}' at {post_url} \n\n{clean_data['name']}'s comment : {clean_data['comment']}"
            send_mail(subject, message, EMAIL_HOST_USER, (clean_data['to'],))
            sent = True
    else :
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', { 'post' : post, 'form' : form, 'sent' : sent })


# class PostListView(ListView) :
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 10
#     template_name = 'blog/post/list.html'


def post_detail_view(request, year, month, day, post) :
    post = get_object_or_404(
            Post, 
            slug = post,
            status = 'published',
            publish__year = year,
            publish__month = month,
            publish__day = day    
        )
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST' :
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid() :
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else :
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
                        .exclude(id=post.id) \
                        .annotate(same_tags=Count('tags')) \
                        .order_by('-same_tags', '-publish')[:3]

    context = {
        'post' : post,
        'comments' : comments,
        'new_comment' : new_comment,
        'comment_form' : comment_form,
        'similar_posts' : similar_posts,
    }
    return render(request, 'blog/post/detail.html', context)



def post_list_view(request, tag_slug=None) :
    posts_list = Post.published.all()
    tag = None
    if tag_slug :
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts_list = posts_list.filter(tags__in=[tag])

    paginator = Paginator(posts_list, 10)
    page = request.GET.get('page')
    try :
        posts = paginator.page(page)
    except PageNotAnInteger :
        posts = paginator.page(1)
    except EmptyPage :
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', { 'page' : page, 'posts' : posts, 'tag' : tag })


def post_search_view(request) :
    form = SearchForm()
    query = None 
    results = []
    if 'query' in request.GET :
        form = SearchForm(request.GET)
        if form.is_valid() :
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', 'body')
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                        search = search_vector,
                        rank = SearchRank(search_vector, search_query)
                    ).filter(search=query).order_by('-rank')
    fcontext = {
        'form' : form,
        'query' : query,
        'results' : results
    }
    return render(request, 'blog/post/search.html', context)

    