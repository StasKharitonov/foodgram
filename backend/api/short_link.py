from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from recipes.models import Recipe


class ShortLinkRedirectView(View):
    def get(self, request, code):
        try:
            recipe_id = int(code, 16)
        except ValueError as error:
            raise Http404 from error

        get_object_or_404(Recipe, pk=recipe_id)
        return redirect(f'/recipes/{recipe_id}')
