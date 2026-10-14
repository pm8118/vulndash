from django.db import models
from django.contrib.auth.models import User


class Scan(models.Model):
    """یه اسکن شبکه که کاربر ایجاد می‌کنه"""

    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('running', 'در حال اجرا'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
    ]

    SCAN_TYPE_CHOICES = [
        ('quick', 'سریع'),
        ('full', 'کامل'),
        ('stealth', 'مخفیانه'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scans',
        verbose_name='کاربر'
    )
    target = models.CharField(
        max_length=255,
        verbose_name='هدف',
        help_text='IP یا دامنه (مثلاً 192.168.1.1 یا example.com)'
    )
    scan_type = models.CharField(
        max_length=20,
        choices=SCAN_TYPE_CHOICES,
        default='quick',
        verbose_name='نوع اسکن'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان شروع'
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='زمان پایان'
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='پیام خطا'
    )

    class Meta:
        verbose_name = 'اسکن'
        verbose_name_plural = 'اسکن‌ها'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.target} - {self.get_status_display()}"


class Host(models.Model):
    """یه هاست که توی اسکن پیدا شده"""

    scan = models.ForeignKey(
        Scan,
        on_delete=models.CASCADE,
        related_name='hosts',
        verbose_name='اسکن'
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='آدرس IP'
    )
    hostname = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='نام هاست'
    )
    os_family = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='سیستم عامل'
    )
    mac_address = models.CharField(
        max_length=17,
        blank=True,
        verbose_name='آدرس MAC'
    )
    is_up = models.BooleanField(
        default=True,
        verbose_name='روشن'
    )
    discovered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان کشف'
    )

    class Meta:
        verbose_name = 'هاست'
        verbose_name_plural = 'هاست‌ها'
        ordering = ['ip_address']
        unique_together = [['scan', 'ip_address']]

    def __str__(self):
        return f"{self.ip_address} ({self.hostname or 'بدون نام'})"


class Port(models.Model):
    """یه پورت باز روی یه هاست"""

    PROTOCOL_CHOICES = [
        ('tcp', 'TCP'),
        ('udp', 'UDP'),
    ]

    STATE_CHOICES = [
        ('open', 'باز'),
        ('closed', 'بسته'),
        ('filtered', 'فیلتر شده'),
    ]

    host = models.ForeignKey(
        Host,
        on_delete=models.CASCADE,
        related_name='ports',
        verbose_name='هاست'
    )
    number = models.PositiveIntegerField(
        verbose_name='شماره پورت'
    )
    protocol = models.CharField(
        max_length=10,
        choices=PROTOCOL_CHOICES,
        default='tcp',
        verbose_name='پروتکل'
    )
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default='open',
        verbose_name='وضعیت'
    )
    service = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='سرویس'
    )
    version = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='نسخه'
    )
    banner = models.TextField(
        blank=True,
        verbose_name='Banner'
    )

    class Meta:
        verbose_name = 'پورت'
        verbose_name_plural = 'پورت‌ها'
        ordering = ['number']
        unique_together = [['host', 'number', 'protocol']]

    def __str__(self):
        return f"{self.number}/{self.protocol} ({self.service or 'ناشناس'})"


class Vulnerability(models.Model):
    """یه آسیب‌پذیری که روی یه پورت پیدا شده"""

    SEVERITY_CHOICES = [
        ('critical', 'بحرانی'),
        ('high', 'بالا'),
        ('medium', 'متوسط'),
        ('low', 'پایین'),
        ('info', 'اطلاعاتی'),
    ]

    port = models.ForeignKey(
        Port,
        on_delete=models.CASCADE,
        related_name='vulnerabilities',
        verbose_name='پورت'
    )
    cve_id = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='شناسه CVE',
        help_text='مثلاً CVE-2021-44228'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='عنوان'
    )
    description = models.TextField(
        blank=True,
        verbose_name='توضیحات'
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='info',
        verbose_name='شدت'
    )
    cvss_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name='امتیاز CVSS'
    )
    reference_url = models.URLField(
        blank=True,
        verbose_name='لینک مرجع'
    )
    discovered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان کشف'
    )

    class Meta:
        verbose_name = 'آسیب‌پذیری'
        verbose_name_plural = 'آسیب‌پذیری‌ها'
        ordering = ['-severity', '-cvss_score']

    def __str__(self):
        return f"{self.cve_id or self.title} - {self.get_severity_display()}"