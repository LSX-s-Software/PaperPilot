# Generated by Django 4.2.7 on 2023-11-08 02:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("paper", "0003_remove_paper_publication_date_paper_publication_year"),
    ]

    operations = [
        migrations.AddField(
            model_name="paper",
            name="event",
            field=models.CharField(
                default="", max_length=255, verbose_name="会议/期刊"
            ),
            preserve_default=False,
        ),
    ]
