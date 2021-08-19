import json

from django.db.models import Count, F, Value, IntegerField, ExpressionWrapper

from django.shortcuts import (
    render,
)
from django.views import (
    View,
)
from recipes.models import Recipe, RecipeProduct, CookStep
from users.models import CustomUser


class Task1View(View):
    """
    Вывести список всех рецептов. Список должен содержать информацию о самом рецепте, авторе
    """

    def get(self, request, **kwargs):
        resipes = Recipe.objects.values('title', 'description', 'userrecipe__user')
        # result = serializers.serialize("json", data)
        data = {
            'response': list(resipes),
        }
        return render(request, 'task.html', {'json_data': json.dumps(data, ensure_ascii=False)})


class Task2View(View):
    """
    Вывести детальную информацию рецепта. Нужно получить информацию о самом рецепте, о шагах приготовления, списке
    необходимых продоктов для приготовления
    """

    def get(self, request, **kwargs):
        recipes = Recipe.objects.all()
        result = []
        for recipe in recipes:
            products = list(RecipeProduct.objects.filter(recipe=recipe).values('product', 'count'))
            steps = list(CookStep.objects.filter(recipe=recipe).values('title', 'description'))
            result.append({'recipe': recipe.title, 'products_for_recipe': products, 'steps': steps})
        data = {
            'response': result,
        }

        return render(request, 'task.html', {'json_data': json.dumps(data, ensure_ascii=False, default=str)})


class Task3View(View):
    """
    Вывести список рецептов, аналогичный заданию 1, только дополнительно должно быть выведено количество лайков. Сам
    список должен быть отсортирован по количеству лайков по убыванию
    """

    def get(self, request, **kwargs):
        resipes = Recipe.objects \
            .annotate(likes=Count('vote', filter=F('vote__is_like'))) \
            .values('title', 'description', 'userrecipe__user', 'likes') \
            .order_by('-likes')
        result = list(resipes)
        data = {
            'response': result,
        }

        return render(request, 'task.html', {'json_data': json.dumps(data, ensure_ascii=False, default=str)})


class Task4View(View):
    """
    Вывести объединенный список TOP 3 авторов и TOP 3 голосующих с количеством рецептов для первых и количеством
    голосов для вторых. В выборке должен быть указан тип в отдельной колонкке - Автор или Пользователь.
    """

    def get(self, request, **kwargs):
        authors = CustomUser.objects.filter(author__isnull=False) \
                      .annotate(count_recipe=Count('userrecipe'), type=Value('Author')) \
                      .values('email', 'count_recipe', 'type') \
                      .order_by('-count_recipe')[:3]
        users = CustomUser.objects.filter(author__isnull=True) \
                    .annotate(count_vote=Count('vote'), type=Value('User')) \
                    .values('email', 'count_vote', 'type') \
                    .order_by('-count_vote')[:3]
        result = list(authors) + list(users)
        data = {
            'response': result,
        }

        return render(request, 'task.html', {'json_data': json.dumps(data, ensure_ascii=False, default=str)})


class Task5View(View):
    """
    Все продукты указаны для приготовления одной порции блюда. Необходимо вывести список необходимых продуктов для
    приготовления самостоятельно выбранного блюда в количестве 5-ти порций
    """

    def get(self, request, **kwargs):
        recipe_id = 2
        products = list(RecipeProduct.objects.filter(recipe_id=recipe_id)
                        .annotate(count_five=ExpressionWrapper(5 * F('count'), output_field=IntegerField()))
                        .values('product', 'count_five'))
        result = {'recipe_id': recipe_id, 'products_for_five_dish': products}
        data = {
            'response': result,
        }

        return render(request, 'task.html', {'json_data': json.dumps(data, ensure_ascii=False, default=str)})
