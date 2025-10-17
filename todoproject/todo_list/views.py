from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from todo_list.forms import ToDoItemCreateForm, ToDoItemUpdateForm
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
    # model = ToDoItem
    queryset = ToDoItem.objects.filter(archived=False)


class ToDoListIndexView(ListView):
    template_name = "todo_list/index.html"
    # TODO: custom qs, archived
    queryset = ToDoItem.objects.all()[:3]


class ToDoListDoneView(ListView):
    # TODO: archived
    queryset = ToDoItem.objects.filter(done=True).all()


class ToDoDetailView(DetailView):
    # model = ToDoItem
    # TODO: archived qs
    queryset = ToDoItem.objects.filter(archived=False)


class ToDoItemCreateView(CreateView):
    model = ToDoItem
    form_class = ToDoItemCreateForm
    # fields = ("title", "description")


class ToDoItemUpdateView(UpdateView):
    model = ToDoItem
    template_name_suffix = "_update_form"
    form_class = ToDoItemUpdateForm
    # fields = ("title", "description", "done")


class ToDoItemDeleteView(DeleteView):
    model = ToDoItem
    success_url = reverse_lazy("todo_list:list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)