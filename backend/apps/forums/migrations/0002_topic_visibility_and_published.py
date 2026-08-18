from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("forums", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="topic",
            name="is_published",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="topic",
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
