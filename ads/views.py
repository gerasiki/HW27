import json

from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from ads.models import Category, Ad
from user.models import User


def index(request):
    return JsonResponse({"status": "ok"})


class CategoriesView(ListView):
    models = Category
    queryset = Category.objects.all()
    
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        self.object_list = self.object_list.order_by("name")

        response = [{"id": category.id, "name": category.name} for category in self.object_list]
        return JsonResponse(response, safe=False)


class CategoryDetailView(DetailView):
    model = Category
    
    def get(self, request, *args, **kwargs):
        category = self.get_object()

        return JsonResponse({
                "id": category.id,
                "name": category.name
            }, json_dumps_params={"ensure_ascii": False})


@method_decorator(csrf_exempt, name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    fields = ["name"]
    
    def post(self, request, *args, **kwargs):
        category_data = json.loads(request.body)
        
        category = Category.objects.create(
            name=category_data["name"],
        )

        return JsonResponse({
            "id": category.id,
            "name": category.name
        }, json_dumps_params={"ensure_ascii": False})
        

@method_decorator(csrf_exempt, name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    fields = ["name"]
    
    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        
        category_data = json.loads(request.body)
        self.object.name = category_data["name"]
        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
        }, json_dumps_params={"ensure_ascii": False})


@method_decorator(csrf_exempt, name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    success_url = "/"
    
    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        
        return JsonResponse({"status": "ok"}, status=204)
        

class AdsView(ListView):
    models = Ad
    queryset = Ad.objects.all()
    
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        self.object_list = self.object_list.select_related('author').order_by("-price")
        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        ads = [{
            "id": ad.id,
            "name": ad.name,
            "author_id": ad.author_id,
            "author": ad.author.username,
            "price": ad.price,
            "description": ad.description,
            "is_published": ad.is_published,
            "category_id": ad.category_id,
            "image": ad.image.url if ad.image else None,
        } for ad in page_obj]

        response = {
            "items": ads,
            "num_pages": page_obj.paginator.num_pages,
            "total": page_obj.paginator.count,
        }
        return JsonResponse(response, safe=False)


class AdDetailView(DetailView):
    model = Ad
    
    def get(self, request, *args, **kwargs):
        ad = self.get_object()

        return JsonResponse({
            "id": ad.id,
            "name": ad.name,
            "author_id": ad.author_id,
            "author": ad.author.first_name,
            "price": ad.price,
            "description": ad.description,
            "is_published": ad.is_published,
            "category_id": ad.category_id,
            "image": ad.image.url if ad.image else None,
        })


@method_decorator(csrf_exempt, name='dispatch')
class AdCreateView(CreateView):
    model = Ad
    fields = ["name", "author", "price", "description", "is_published", "category"]
    
    def post(self, request, *args, **kwargs):
        ad_data = json.loads(request.body)

        author = get_object_or_404(User, pk=ad_data["author_id"])
        category = get_object_or_404(Category, pk=ad_data["category"])
                
        ad = Ad.objects.create(
            name=ad_data["name"],
            author=author,
            price=ad_data["price"],
            description=ad_data["description"],
            is_published=ad_data["is_published"],
            category=category,
        )

        return JsonResponse({
            "id": ad.id,
            "name": ad.name,
            "author_id": ad.author_id,
            "author": ad.author.first_name,
            "price": ad.price,
            "description": ad.description,
            "is_published": ad.is_published,
            "category_id": ad.category_id,
            "image": ad.image.url if ad.image else None,
        })
        

@method_decorator(csrf_exempt, name='dispatch')
class AdUpdateView(UpdateView):
    model = Ad
    fields = ["name", "author", "price", "description", "category"]
    
    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        
        ad_data = json.loads(request.body)
        self.object.name = ad_data["name"]
        self.object.price = ad_data["price"]
        self.object.description = ad_data["description"]
        
        author = get_object_or_404(User, pk=ad_data["author_id"])
        self.object.category = get_object_or_404(Category, pk=ad_data["category"])
        
        self.object.save()
        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
            "author_id": self.object.author_id,
            "author": author.first_name,
            "price": self.object.price,
            "description": self.object.description,
            "is_published": self.object.is_published,
            "category_id": self.object.category_id,
            "image": self.object.image.url if self.object.image else None,
        })


@method_decorator(csrf_exempt, name='dispatch')
class AdDeleteView(DeleteView):
    model = Ad
    success_url = "/"
    
    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        
        return JsonResponse({"status": "ok"}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class AdUploadImageView(UpdateView):
    model = Ad
    fields = ["image"]

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.image = request.FILES.get('image', None)
        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "name": self.object.name,
            "author_id": self.object.author_id,
            "author": self.object.author.first_name,
            "price": self.object.price,
            "description": self.object.description,
            "is_published": self.object.is_published,
            "category_id": self.object.category_id,
            "image": self.object.image.url if self.object.image else None,
        }, json_dumps_params={"ensure_ascii": False})
