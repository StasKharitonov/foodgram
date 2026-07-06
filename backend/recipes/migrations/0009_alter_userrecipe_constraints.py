from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_recipe_image_ingredient_unique'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='favorite',
            name='unique_favorite_user_recipe',
        ),
        migrations.RemoveConstraint(
            model_name='shoppingcart',
            name='unique_cart_user_recipe',
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='recipes_favorite_unique_user_recipe',
            ),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='recipes_shoppingcart_unique_user_recipe',
            ),
        ),
    ]
