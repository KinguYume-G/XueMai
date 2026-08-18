from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("communities", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="community",
            name="is_published",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="community",
            name="visibility",
            field=models.CharField(
                choices=[
                    ("public", "Public"),
                    ("university", "University"),
                    ("private", "Private"),
                ],
                default="public",
                max_length=20,
            ),
        ),
    ]
