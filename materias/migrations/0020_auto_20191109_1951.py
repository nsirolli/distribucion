# Generated by Django 2.1.10 on 2019-11-09 22:51

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materias', '0019_auto_20191109_1725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carga',
            name='cargo',
            field=models.CharField(choices=[('EmeExc', 'Prof. Emerito Exclusiva'), ('EmeSmx', 'Prof. Emerito Semiexclusiva'), ('EmePar', 'Prof. Emerito Parcial'), ('HonExc', 'Prof. Honorario Exclusiva'), ('HonSmx', 'Prof. Honorario Semiexclusiva'), ('HonPar', 'Prof. Honorario Parcial'), ('ConExc', 'Prof. Consulto Exclusiva'), ('ConSmx', 'Prof. Consulto Semiexclusiva'), ('ConPar', 'Prof. Consulto Parcial'), ('PleExc', 'Prof. Plenario Exclusiva'), ('PleSmx', 'Prof. Plenario Semiexclusiva'), ('PlePar', 'Prof. Plenario Parcial'), ('VisExc', 'Prof. Visitante Exclusiva'), ('VisSmx', 'Prof. Visitante Semiexclusiva'), ('VisPar', 'Prof. Visitante Parcial'), ('TitExc', 'Prof. Titular Exclusiva'), ('TitSmx', 'Prof. Titular Semiexclusiva'), ('TitPar', 'Prof. Titular Parcial'), ('AsoExc', 'Prof. Asociado Exclusiva'), ('AsoSmx', 'Prof. Asociado Semiexclusiva'), ('AsoPar', 'Prof. Asociado Parcial'), ('AdjExc', 'Prof. Adjunto Exclusiva'), ('AdjSmx', 'Prof. Adjunto Semiexclusiva'), ('AdjPar', 'Prof. Adjunto Parcial'), ('JTPExc', 'Jefe de Trabajos Prácticos Exclusiva'), ('JTPSmx', 'Jefe de Trabajos Prácticos Semiexclusiva'), ('JTPPar', 'Jefe de Trabajos Prácticos Parcial'), ('Ay1Exc', 'Ayudante de 1ra Exclusiva'), ('Ay1Smx', 'Ayudante de 1ra Semiexclusiva'), ('Ay1Par', 'Ayudante de 1ra Parcial'), ('Ay2Par', 'Ayudante de 2da Parcial')], max_length=6),
        ),
        migrations.AlterField(
            model_name='docente',
            name='cargos',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('EmeExc', 'Prof. Emerito Exclusiva'), ('EmeSmx', 'Prof. Emerito Semiexclusiva'), ('EmePar', 'Prof. Emerito Parcial'), ('HonExc', 'Prof. Honorario Exclusiva'), ('HonSmx', 'Prof. Honorario Semiexclusiva'), ('HonPar', 'Prof. Honorario Parcial'), ('ConExc', 'Prof. Consulto Exclusiva'), ('ConSmx', 'Prof. Consulto Semiexclusiva'), ('ConPar', 'Prof. Consulto Parcial'), ('PleExc', 'Prof. Plenario Exclusiva'), ('PleSmx', 'Prof. Plenario Semiexclusiva'), ('PlePar', 'Prof. Plenario Parcial'), ('VisExc', 'Prof. Visitante Exclusiva'), ('VisSmx', 'Prof. Visitante Semiexclusiva'), ('VisPar', 'Prof. Visitante Parcial'), ('TitExc', 'Prof. Titular Exclusiva'), ('TitSmx', 'Prof. Titular Semiexclusiva'), ('TitPar', 'Prof. Titular Parcial'), ('AsoExc', 'Prof. Asociado Exclusiva'), ('AsoSmx', 'Prof. Asociado Semiexclusiva'), ('AsoPar', 'Prof. Asociado Parcial'), ('AdjExc', 'Prof. Adjunto Exclusiva'), ('AdjSmx', 'Prof. Adjunto Semiexclusiva'), ('AdjPar', 'Prof. Adjunto Parcial'), ('JTPExc', 'Jefe de Trabajos Prácticos Exclusiva'), ('JTPSmx', 'Jefe de Trabajos Prácticos Semiexclusiva'), ('JTPPar', 'Jefe de Trabajos Prácticos Parcial'), ('Ay1Exc', 'Ayudante de 1ra Exclusiva'), ('Ay1Smx', 'Ayudante de 1ra Semiexclusiva'), ('Ay1Par', 'Ayudante de 1ra Parcial'), ('Ay2Par', 'Ayudante de 2da Parcial')], max_length=6), size=2),
        ),
        migrations.AlterField(
            model_name='historicalcarga',
            name='cargo',
            field=models.CharField(choices=[('EmeExc', 'Prof. Emerito Exclusiva'), ('EmeSmx', 'Prof. Emerito Semiexclusiva'), ('EmePar', 'Prof. Emerito Parcial'), ('HonExc', 'Prof. Honorario Exclusiva'), ('HonSmx', 'Prof. Honorario Semiexclusiva'), ('HonPar', 'Prof. Honorario Parcial'), ('ConExc', 'Prof. Consulto Exclusiva'), ('ConSmx', 'Prof. Consulto Semiexclusiva'), ('ConPar', 'Prof. Consulto Parcial'), ('PleExc', 'Prof. Plenario Exclusiva'), ('PleSmx', 'Prof. Plenario Semiexclusiva'), ('PlePar', 'Prof. Plenario Parcial'), ('VisExc', 'Prof. Visitante Exclusiva'), ('VisSmx', 'Prof. Visitante Semiexclusiva'), ('VisPar', 'Prof. Visitante Parcial'), ('TitExc', 'Prof. Titular Exclusiva'), ('TitSmx', 'Prof. Titular Semiexclusiva'), ('TitPar', 'Prof. Titular Parcial'), ('AsoExc', 'Prof. Asociado Exclusiva'), ('AsoSmx', 'Prof. Asociado Semiexclusiva'), ('AsoPar', 'Prof. Asociado Parcial'), ('AdjExc', 'Prof. Adjunto Exclusiva'), ('AdjSmx', 'Prof. Adjunto Semiexclusiva'), ('AdjPar', 'Prof. Adjunto Parcial'), ('JTPExc', 'Jefe de Trabajos Prácticos Exclusiva'), ('JTPSmx', 'Jefe de Trabajos Prácticos Semiexclusiva'), ('JTPPar', 'Jefe de Trabajos Prácticos Parcial'), ('Ay1Exc', 'Ayudante de 1ra Exclusiva'), ('Ay1Smx', 'Ayudante de 1ra Semiexclusiva'), ('Ay1Par', 'Ayudante de 1ra Parcial'), ('Ay2Par', 'Ayudante de 2da Parcial')], max_length=6),
        ),
        migrations.AlterField(
            model_name='historicaldocente',
            name='cargos',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('EmeExc', 'Prof. Emerito Exclusiva'), ('EmeSmx', 'Prof. Emerito Semiexclusiva'), ('EmePar', 'Prof. Emerito Parcial'), ('HonExc', 'Prof. Honorario Exclusiva'), ('HonSmx', 'Prof. Honorario Semiexclusiva'), ('HonPar', 'Prof. Honorario Parcial'), ('ConExc', 'Prof. Consulto Exclusiva'), ('ConSmx', 'Prof. Consulto Semiexclusiva'), ('ConPar', 'Prof. Consulto Parcial'), ('PleExc', 'Prof. Plenario Exclusiva'), ('PleSmx', 'Prof. Plenario Semiexclusiva'), ('PlePar', 'Prof. Plenario Parcial'), ('VisExc', 'Prof. Visitante Exclusiva'), ('VisSmx', 'Prof. Visitante Semiexclusiva'), ('VisPar', 'Prof. Visitante Parcial'), ('TitExc', 'Prof. Titular Exclusiva'), ('TitSmx', 'Prof. Titular Semiexclusiva'), ('TitPar', 'Prof. Titular Parcial'), ('AsoExc', 'Prof. Asociado Exclusiva'), ('AsoSmx', 'Prof. Asociado Semiexclusiva'), ('AsoPar', 'Prof. Asociado Parcial'), ('AdjExc', 'Prof. Adjunto Exclusiva'), ('AdjSmx', 'Prof. Adjunto Semiexclusiva'), ('AdjPar', 'Prof. Adjunto Parcial'), ('JTPExc', 'Jefe de Trabajos Prácticos Exclusiva'), ('JTPSmx', 'Jefe de Trabajos Prácticos Semiexclusiva'), ('JTPPar', 'Jefe de Trabajos Prácticos Parcial'), ('Ay1Exc', 'Ayudante de 1ra Exclusiva'), ('Ay1Smx', 'Ayudante de 1ra Semiexclusiva'), ('Ay1Par', 'Ayudante de 1ra Parcial'), ('Ay2Par', 'Ayudante de 2da Parcial')], max_length=6), size=2),
        ),
    ]