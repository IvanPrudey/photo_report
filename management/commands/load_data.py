import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from reports.models import TradingClient, CategoryProduct, BrandProduct


class Command(BaseCommand):
    help = 'Загрузка тестовых данных из CSV файлов. Все названия вымышленные!'

    def handle(self, *args, **kwargs):
        self.load_trading_clients()
        self.load_categories()
        self.load_brands()
        self.stdout.write(
            self.style.SUCCESS('Все данные загружены успешно!')
        )

    def load_trading_clients(self):
        csv_path = (
            Path(__file__).resolve().parents[3]
            / 'data' 
            / 'tradingclient.CSV'
        )
        if not csv_path.exists():
            self.stdout.write(
                self.style.ERROR(f'Файл {csv_path} не найден!')
            )
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                TradingClient.objects.update_or_create(
                    name=row['name'],
                    defaults={'is_active': row['is_active'].lower() == 'true'}
                )
        self.stdout.write(
            self.style.SUCCESS('Сети загружены успешно!')
        )

    def load_categories(self):
        csv_path = (
            Path(__file__).resolve().parents[3]
            / 'data'
            / 'category.CSV'
        )
        if not csv_path.exists():
            self.stdout.write(
                self.style.ERROR(f'Файл {csv_path} не найден!')
            )
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                CategoryProduct.objects.update_or_create(
                    name=row['name']
                )
        self.stdout.write(
            self.style.SUCCESS('Категории загружены успешно!')
        )

    def load_brands(self):
        csv_path = (
            Path(__file__).resolve().parents[3]
            / 'data'
            / 'brand.CSV'
        )
        if not csv_path.exists():
            self.stdout.write(
                self.style.ERROR(f'Файл {csv_path} не найден')
            )
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    category = CategoryProduct.objects.get(
                        name=row['category']
                    )
                    BrandProduct.objects.update_or_create(
                        name=row['name'],
                        category=category,
                        defaults={
                            'is_active': row['is_active'].lower() == 'true'
                        }
                    )
                except CategoryProduct.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Категория {row['category']} на найдена для брэнда {row['name']}"
                        )
                    )
        self.stdout.write(
            self.style.SUCCESS('Брэнды загружены успешно!')
        )
