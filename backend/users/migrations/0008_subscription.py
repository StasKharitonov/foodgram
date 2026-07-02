import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_user_username'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='Subscription',
                    fields=[
                        (
                            'id',
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name='ID',
                            ),
                        ),
                        (
                            'created_at',
                            models.DateTimeField(
                                auto_now_add=True,
                                verbose_name='Дата добавления',
                            ),
                        ),
                        (
                            'subscriber',
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name='subscriptions',
                                to=settings.AUTH_USER_MODEL,
                                verbose_name='Подписчик',
                            ),
                        ),
                        (
                            'subscribed_to',
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name='subscribers',
                                to=settings.AUTH_USER_MODEL,
                                verbose_name='Автор',
                            ),
                        ),
                    ],
                    options={
                        'verbose_name': 'Подписка',
                        'verbose_name_plural': 'Подписки',
                        'db_table': 'recipes_subscription',
                        'ordering': ('-created_at',),
                        'constraints': [
                            models.UniqueConstraint(
                                fields=('subscriber', 'subscribed_to'),
                                name='unique_name_owner',
                            ),
                        ],
                    },
                ),
            ],
        ),
    ]
