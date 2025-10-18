from celery.result import AsyncResult
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery, TrigramSimilarity
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.db import models
from todo_list.forms import ToDoItemCreateForm, ToDoItemUpdateForm, ToDoItemSearchForm
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

    TITLE_WEIGHT = 0.7
    DESCRIPTION_WEIGHT = 0.4

    # model = ToDoItem
    queryset = ToDoItem.objects.active()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(form=ToDoItemSearchForm(self.request.GET))
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if search := self.request.GET.get("search"):
            # example 0
            # qs = qs.filter(
            #     models.Q(title__icontains=search)
            #     | models.Q(description__icontains=search)
            # )
            # example 1
            # qs = qs.annotate(
            #     search=SearchVector('title', 'description'),
            # ).filter(search=search)
            # example 2
            # search_vector = SearchVector('title', 'description')
            # search_query = SearchQuery(search)
            # qs = qs.annotate(
            #     search=search_vector,
            #     rank=SearchRank(search_vector, search_query),
            # ).filter(search=search_query).order_by("-rank", "pk")
            # example 3
            # qs = qs.annotate(
            #     similarity = TrigramSimilarity("title", search),
            # ).filter(similarity__gt=0.1).order_by("-similarity","pk")
            # example 4
            qs = qs.annotate(
                title_similarity = TrigramSimilarity("title", search),
                description_similarity = TrigramSimilarity("description", search),
                combined_similarity=(
                        (models.F("title_similarity") * self.TITLE_WEIGHT)
                        + (models.F("description_similarity") * self.DESCRIPTION_WEIGHT)
                ),
            ).filter(combined_similarity__gt=0.07).order_by(
                "-combined_similarity",
                "-title_similarity",
                "-description_similarity",
                "pk",
            )
        return qs


class ToDoListIndexView(ListView):
    template_name = "todo_list/index.html"
    queryset = ToDoItem.objects.active()[:3]


class ToDoListDoneView(ListView):

    queryset = ToDoItem.objects.active().done()
    extra_context = {
        "form": ToDoItemSearchForm(),
    }


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
        template_name="todo_list/task-status.html",
        context=context,
    )
