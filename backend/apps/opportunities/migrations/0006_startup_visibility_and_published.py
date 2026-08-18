from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("opportunities", "0005_exchangeprogram_is_urgent_exchangeprogram_website")
    ]

    operations = [
        migrations.AddField(
            model_name="startup",
            name="is_published",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="startup",
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
