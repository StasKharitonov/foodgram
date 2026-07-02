from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_field_lengths'),
        ('users', '0008_subscription'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(
                    name='Subscription',
                ),
            ],
        ),
    ]
