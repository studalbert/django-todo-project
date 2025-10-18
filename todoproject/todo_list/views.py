from celery.result import AsyncResult
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from todo_list.forms import ToDoItemCreateForm, ToDoItemUpdateForm
from todo_list.models import ToDoItem
from todo_list.tasks import notify_admin_todo_archived


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
    queryset = ToDoItem.objects.active()


class ToDoListIndexView(ListView):
    template_name = "todo_list/index.html"
    queryset = ToDoItem.objects.active()[:3]


class ToDoListDoneView(ListView):

    queryset = ToDoItem.objects.active().done()


class ToDoDetailView(DetailView):
    # model = ToDoItem
    queryset = ToDoItem.objects.active()


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
    # model = ToDoItem
    queryset = ToDoItem.objects.active()
    success_url = reverse_lazy("todo_list:list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        # notify_admin_todo_archived.delay(todo_id=self.object.pk)
        notify_admin_todo_archived.delay_on_commit(todo_id=self.object.pk)
        return HttpResponseRedirect(success_url)

def task_status(request: HttpRequest) -> HttpResponse:
    task_id = request.GET.get("task_id") or ""
    context = {"task_id": task_id}
    result = AsyncResult(task_id)
    context.update(status=result.status, ready=result.ready, result=result.result)
    return render(
        request,
        template_name='todo_list/task-status.html',
        context=context,
    )
