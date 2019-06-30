# Generated by Django 2.1.9 on 2019-06-30 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('encuestas', '0005_auto_20190622_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpreferenciasdocente',
            name='cargo',
            field=models.CharField(choices=[('Eme', 'Prof. Emerito'), ('Hon', 'Prof. Honorario'), ('Con', 'Prof. Consulto'), ('Ple', 'Prof. Plenario'), ('Vis', 'Prof. Visitante'), ('Tit', 'Prof. Titular'), ('Aso', 'Prof. Asociado'), ('Adj', 'Prof. Adjunto'), ('JTP', 'Jefe de Trabajos Prácticos'), ('Ay1', 'Ayudante de 1ra'), ('Ay2', 'Ayudante de 2da')], max_length=3),
        ),
        migrations.AlterField(
            model_name='preferenciasdocente',
            name='cargo',
            field=models.CharField(choices=[('Eme', 'Prof. Emerito'), ('Hon', 'Prof. Honorario'), ('Con', 'Prof. Consulto'), ('Ple', 'Prof. Plenario'), ('Vis', 'Prof. Visitante'), ('Tit', 'Prof. Titular'), ('Aso', 'Prof. Asociado'), ('Adj', 'Prof. Adjunto'), ('JTP', 'Jefe de Trabajos Prácticos'), ('Ay1', 'Ayudante de 1ra'), ('Ay2', 'Ayudante de 2da')], max_length=3),
        ),
    ]
