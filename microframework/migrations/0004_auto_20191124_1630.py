# Generated by Django 2.2.7 on 2019-11-24 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microframework', '0003_auto_20191124_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pendingobjects',
            name='object_id',
            field=models.TextField(),
        ),
    ]
