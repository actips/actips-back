# Generated by Django 2.0.5 on 2019-04-24 16:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base_media', '0003_auto_20180908_1152'),
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('sorting', models.BigIntegerField(db_index=True, default=0, help_text='用于系统进行排序的参数，可以给用户设定或者作为计算列存储组合权重', verbose_name='排序')),
                ('is_sticky', models.BooleanField(db_index=True, default=False, verbose_name='是否置顶')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')),
                ('date_updated', models.DateTimeField(auto_now=True, db_index=True, verbose_name='修改时间')),
                ('name', models.CharField(blank=True, default='', max_length=255, verbose_name='名称')),
                ('user', models.OneToOneField(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='member', serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
                ('nickname', models.CharField(blank=True, default='', max_length=255, verbose_name='昵称')),
                ('nickname_pinyin', models.CharField(blank=True, default='', max_length=255, verbose_name='昵称拼音')),
                ('gender', models.CharField(blank=True, choices=[('', '保密'), ('M', '男'), ('F', '女')], default='', max_length=1, verbose_name='性别')),
                ('real_name', models.CharField(blank=True, default='', max_length=150, verbose_name='真实姓名')),
                ('mobile', models.CharField(max_length=45, unique=True, verbose_name='手机号码')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='生日')),
                ('age', models.IntegerField(default=0, help_text='如果为0则根据birthday判定年龄，否则使用此数字作为年龄', verbose_name='年龄')),
                ('search_history', models.TextField(blank=True, help_text='最近10次搜索历史，逗号分隔', null=True, verbose_name='搜索历史')),
                ('signature', models.TextField(blank=True, null=True, verbose_name='个性签名')),
                ('district', models.IntegerField(default=0, help_text='行政区划编码，参考：https://zh.wikipedia.org/wiki/中华人民共和国行政区划', verbose_name='所在地区')),
                ('address', models.TextField(blank=True, default='', verbose_name='详细地址')),
                ('session_key', models.CharField(blank=True, default='', help_text='用于区分单用例登录', max_length=255, verbose_name='session_key')),
                ('constellation', models.CharField(blank=True, choices=[('ARIES', '白羊座'), ('TAURUS', '金牛座'), ('GEMINI', '双子座'), ('CANCER', '巨蟹座'), ('LEO', '狮子座'), ('VIRGO', '处女座'), ('LIBRA', '天秤座'), ('SCORPIO', '天蝎座'), ('SAGITTARIUS', '射手座'), ('CAPRICORN', '摩羯座'), ('AQUARIUS', '水瓶座'), ('PISCES', '双鱼座')], default='', max_length=45, verbose_name='星座')),
                ('avatar', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member', to='base_media.Image', verbose_name='头像')),
            ],
            options={
                'verbose_name': '会员',
                'verbose_name_plural': '会员',
                'db_table': 'core_member',
            },
        ),
        migrations.CreateModel(
            name='OAuthEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(blank=True, choices=[('WECHAT_APP', '微信APP'), ('WECHAT_BIZ', '微信公众平台'), ('ALIPAY', '支付宝'), ('QQ', 'QQ'), ('WEIBO', '微博')], default='', max_length=20, verbose_name='第三方平台')),
                ('app', models.CharField(blank=True, default='', max_length=120, verbose_name='app')),
                ('openid', models.CharField(max_length=128, verbose_name='用户OpenID')),
                ('nickname', models.CharField(max_length=128, null=True, verbose_name='用户昵称')),
                ('headimgurl', models.URLField(blank=True, null=True, verbose_name='用户头像')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='oauth/avatar/', verbose_name='头像文件')),
                ('params', models.TextField(blank=True, default='', verbose_name='params')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='oauthentrys_owned', to=settings.AUTH_USER_MODEL, verbose_name='作者')),
            ],
            options={
                'verbose_name': '会员',
                'verbose_name_plural': '会员',
                'db_table': 'core_oauth_entry',
            },
        ),
    ]
