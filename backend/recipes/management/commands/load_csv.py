import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_path = '/app/data/ingredients.csv'

        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                count = 0
                for row in reader:
                    if not row:
                        continue
                    Ingredient.objects.get_or_create(
                        name=row[0].strip(),
                        measurement_unit=row[1].strip()
                    )
                    count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Загружено {count} ингридиентов')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при загрузке: {e}')
            )
