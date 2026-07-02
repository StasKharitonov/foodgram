import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_user_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(
                max_length=150,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message='Имя юзера может содержать следующие символы: @.+-_',
                        regex='^[\\w.@+-]+\\Z',
                    ),
                ],
                verbose_name='Псевдоним',
            ),
        ),
    ]
