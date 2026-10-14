from django.contrib import admin
from .models import Scan, Host, Port, Vulnerability


@admin.register(Scan)
class ScanAdmin(admin.ModelAdmin):
    list_display = ('id', 'target', 'scan_type', 'status', 'user', 'started_at')
    list_filter = ('status', 'scan_type', 'started_at')
    search_fields = ('target',)
    readonly_fields = ('started_at', 'finished_at')
    date_hierarchy = 'started_at'


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip_address', 'hostname', 'os_family', 'is_up', 'scan')
    list_filter = ('is_up', 'os_family')
    search_fields = ('ip_address', 'hostname', 'mac_address')


@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'protocol', 'state', 'service', 'version', 'host')
    list_filter = ('protocol', 'state', 'service')
    search_fields = ('number', 'service')


@admin.register(Vulnerability)
class VulnerabilityAdmin(admin.ModelAdmin):
    list_display = ('id', 'cve_id', 'title', 'severity', 'cvss_score', 'port')
    list_filter = ('severity',)
    search_fields = ('cve_id', 'title')
    list_display_links = ('id', 'title')