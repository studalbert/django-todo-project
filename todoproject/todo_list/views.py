from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView

from todo_list.models import ToDoItem


def index_view(request: HttpRequest) -> HttpResponse:
    todo_items = ToDoItem.objects.all()
    context = {"todo_items": todo_items[:3]}
    return render(request, template_name="todo_list/index.html", context=context)



# class ToDoListIndexView(TemplateView):
#     template_name = "todo_list/index.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["todo_items"] = ToDoItem.objects.all()
#         return context

class ToDoListView(ListView):
    model = ToDoItem

class ToDoListIndexView(ListView):
    template_name = "todo_list/index.html"
    queryset = ToDoItem.objects.all()[:3]

class ToDoListDoneView(ListView):
    queryset = ToDoItem.objects.filter(done=True).all()

class ToDoDetailView(DetailView):
    model = ToDoItem

