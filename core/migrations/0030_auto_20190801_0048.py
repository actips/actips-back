# Generated by Django 2.2.1 on 2019-08-01 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20190730_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onlinejudgesubmission',
            name='language',
            field=models.CharField(choices=[('', ''), ('C', 'C'), ('CPP', 'C++'), ('JAVA', 'Java'), ('PYTHON2', 'Python2'), ('PYTHON3', 'Python3'), ('PASCAL', 'Pascal'), ('DELPHI', 'Delphi'), ('RUBY', 'Ruby'), ('CSHARP', 'C#'), ('HASKELL', 'Haskell'), ('OCAML', 'OCaml'), ('SCALA', 'Scala'), ('D', 'D'), ('GO', 'Go'), ('JAVASCRIPT', 'JavaScript'), ('KOTLIN', 'Kotlin'), ('RUST', 'Rust'), ('CLANG', 'Clang'), ('NODEJS', 'Node.js'), ('PERL', 'Perl'), ('SCHEME', 'Scheme'), ('PHP', 'PHP')], max_length=30, verbose_name='语言'),
        ),
    ]
