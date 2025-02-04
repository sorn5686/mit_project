from django.shortcuts import render, get_object_or_404 ,redirect
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post
import operator
from django.urls import reverse_lazy ,reverse
from django.contrib.staticfiles.views import serve
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.forms import DateTimeInput
# import pytz 

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)

def search(request):
    template='blog/home.html'

    query=request.GET.get('q')

    result=Post.objects.filter(Q(title__icontains=query) | Q(author__username__icontains=query) | Q(content__icontains=query))
    paginate_by= 5
    context={ 'posts':result }
    return render(request,template,context)
   


def getfile(request):
   return serve(request, 'File')


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'file', 'category', 'date_ended', 'max_participants']
    
    # กำหนด widget สำหรับฟิลด์ date_ended
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date_ended'].widget = DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M') 
        # form.fields['date_ended'].input_formats = ('%Y-%m-%dT%H:%M',)  # รูปแบบนี้เป็นตัวอย่าง คุณสามารถปรับให้เป็นรูปแบบไทยได้ตามต้องการ
        # form.fields['date_ended'].timezone = pytz.timezone('Asia/Bangkok')  # กำหนดโซนเวลาไทย
        return form
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form) 


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'file', 'category', 'date_ended', 'max_participants']
    
    # กำหนด widget สำหรับฟิลด์ date_ended
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date_ended'].widget = DateTimeInput(attrs={'type': 'datetime-local'}, format=' ')
        # form.fields['date_ended'].input_formats = ('%Y-%m-%dT%H:%M',)  # รูปแบบนี้เป็นตัวอย่าง คุณสามารถปรับให้เป็นรูปแบบไทยได้ตามต้องการ
        # form.fields['date_ended'].timezone = pytz.timezone('Asia/Bangkok')  # กำหนดโซนเวลาไทย
        return form
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False 


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    template_name = 'blog/post_confirm_delete.html'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

def join_post(request, pk):
    # ดึงโพสต์ที่ต้องการเข้าร่วมจากฐานข้อมูล
    post = get_object_or_404(Post, pk=pk)
    
    # เพิ่มผู้ใช้ปัจจุบันในรายชื่อผู้เข้าร่วมโพสต์
    post.participants.add(request.user)
    
    # บันทึกการเปลี่ยนแปลง
    post.save()
    
    # นำผู้ใช้กลับไปยังหน้ารายละเอียดโพสต์หลังจากการเข้าร่วม
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
