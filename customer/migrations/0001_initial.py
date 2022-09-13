# Generated by Django 3.2.15 on 2022-09-13 11:32

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vendor', '__first__'),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='base.user')),
                ('start_date', models.DateField()),
                ('shift', models.CharField(blank=True, choices=[(1, 'morning'), (2, 'evening'), (3, 'both')], max_length=10, null=True)),
                ('milk_unit', models.IntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_customer', to='vendor.vendor')),
            ],
            options={
                'db_table': 'Customer',
            },
            bases=('base.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
