from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_subscription_self_constraint'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='bio',
        ),
        migrations.AlterModelOptions(
            name='user',
            options={
                'ordering': ('username',),
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
        ),
        migrations.RemoveConstraint(
            model_name='subscription',
            name='prevent_self_subscription',
        ),
        migrations.RemoveConstraint(
            model_name='subscription',
            name='unique_name_owner',
        ),
        migrations.RenameField(
            model_name='subscription',
            old_name='subscriber',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='subscription',
            old_name='subscribed_to',
            new_name='author',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='created_at',
        ),
        migrations.AlterModelOptions(
            name='subscription',
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
            },
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_name_owner',
            ),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.CheckConstraint(
                condition=~models.Q(user=models.F('author')),
                name='prevent_self_subscription',
            ),
        ),
    ]
