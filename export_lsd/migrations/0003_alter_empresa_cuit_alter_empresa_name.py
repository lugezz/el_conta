# Generated by Django 4.1.7 on 2023-03-07 12:50

from django.db import migrations, models
import export_lsd.validators


class Migration(migrations.Migration):

    dependencies = [
        ('export_lsd', '0002_empresa_created_empresa_updated_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empresa',
            name='cuit',
            field=models.CharField(max_length=11, validators=[export_lsd.validators.validate_cuit]),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='name',
            field=models.CharField(max_length=120, validators=[export_lsd.validators.validate_name], verbose_name='Razon Social'),
        ),
    ]
