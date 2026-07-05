import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_path = '/app/data/ingredients.csv'

        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                ingredients = []
                for row in reader:
                    if not row:
                        continue
                    name, measurement_unit = row
                    ingredients.append(Ingredient(
                        name=name.strip(),
                        measurement_unit=measurement_unit.strip(),
                    ))
                Ingredient.objects.bulk_create(
                    ingredients,
                    ignore_conflicts=True,
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Загружено {len(ingredients)} ингридиентов'
                    )
                )
        except Exception as error:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при загрузке: {error}')
            )
