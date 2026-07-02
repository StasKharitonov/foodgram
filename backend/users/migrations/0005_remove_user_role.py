from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_avatar_alter_user_first_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='role',
        ),
    ]
