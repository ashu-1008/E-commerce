from django.shortcuts import render
from django.http import HttpResponse
from .models import Blogpost
from math import ceil
# Create your views here.
blogs = Blogpost.objects.all()


def index(request):

    no_blogs = len(blogs)
    data = []
    for a in range(0, (no_blogs - 1), 2):
        row_data = [blogs[a], blogs[a+1]]
        data.append(row_data)
    if no_blogs % 2 != 0:
        data.append([blogs[no_blogs-1]])
    data_for_frontend = {
        'data_list': data,
    }
    return render(request, 'blog/index.html', data_for_frontend)


def blogpost(request, blog_id):
    blog_post = Blogpost.objects.filter(post_id=blog_id)

    # array of all id
    id_list = []
    for _id in blogs:
        id_list.append(_id.post_id)


    current_id_index = id_list.index(blog_id)

    if current_id_index == 0:                            # if first blog
        data_for_frontend = {
            'blog_post': blog_post,
            'next_blog_id': id_list[current_id_index+1],
            'nav': 'next'
        }
    elif current_id_index == len(id_list)-1:              # if last blog
        data_for_frontend = {
            'blog_post': blog_post,
            'prev_blog_id': id_list[current_id_index - 1],
            'nav': 'prev'
        }
    else:                                                 # not first or last blog
        data_for_frontend = {
            'blog_post': blog_post,
            'prev_blog_id': id_list[current_id_index - 1],
            'next_blog_id': id_list[current_id_index + 1],
            'nav': 'prev-next'
        }
    return render(request, 'blog/blogpost.html', data_for_frontend)
