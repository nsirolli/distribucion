# Generated by Django 2.1.7 on 2019-03-04 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materias', '0010_auto_20190111_0031'),
    ]

    operations = [
        migrations.AddField(
            model_name='turno',
            name='subnumero',
            field=models.CharField(blank=True, max_length=6),
        ),
    ]