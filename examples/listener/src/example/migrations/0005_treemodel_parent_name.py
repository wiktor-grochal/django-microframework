# Generated by Django 2.2.7 on 2019-11-24 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('example', '0004_secondforeignkeymodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='treemodel',
            name='parent_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]