from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from django.views.generic import ListView
from django.contrib.postgres.search import SearchVector
from blog.forms import EmailPostForm , CommentForm, SearchForm
from taggit.models import Tag
from django.db.models import Count

def post_list(request, tag_slug=None):
  
    #return render(request,'blog/post/list.html',{'posts': posts})
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3) # 3 posts in each page
    page = request.GET.get('page')
    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer deliver the first page
        object_list = paginator.page(1)
    except EmptyPage:
    # If page is out of range deliver last page of results
      posts = paginator.page(paginator.num_pages)
      # List of similar posts
      
    return render(request,
    'blog/post/list.html',
    {'page': page,
    'object_list': object_list,'tag': tag ,
    })



def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                    status='published',
                                    publish__year=year,
                                    publish__month=month,
                                    publish__day=day)
                                    # List of active comments for this post
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
    # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        print("***** Here e are inside the else *****")
        comment_form = CommentForm()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')
    return render(request,'blog/post/detail.html',{'post': post,'comments': comments,
             'new_comment': new_comment,'comment_form': comment_form,'similar_posts': similar_posts})
    



# class PostListView(ListView):
#     queryset = Post.objects.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'




def post_share(request, post_id):

    post = get_object_or_404(Post, id=post_id, status='published')
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
    else:
        form = EmailPostForm()
   #return render(request, 'blog/post/share.html', {'post': post,'form': form})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
       form = SearchForm(request.GET)
       if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(
            search=SearchVector('title', 'body'),
            ).filter(search=query)
    return render(request,'blog/post/search.html',{'form': form,'query': query,'results': results})
