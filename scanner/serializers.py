from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Scan, Host, Port, Vulnerability


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class VulnerabilitySerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)

    class Meta:
        model = Vulnerability
        fields = [
            'id', 'cve_id', 'title', 'description', 'severity',
            'severity_display', 'cvss_score', 'reference_url', 'discovered_at'
        ]


class PortSerializer(serializers.ModelSerializer):
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    protocol_display = serializers.CharField(source='get_protocol_display', read_only=True)
    vulnerabilities = VulnerabilitySerializer(many=True, read_only=True)

    class Meta:
        model = Port
        fields = [
            'id', 'number', 'protocol', 'protocol_display',
            'state', 'state_display', 'service', 'version', 'banner',
            'vulnerabilities'
        ]


class HostSerializer(serializers.ModelSerializer):
    ports = PortSerializer(many=True, read_only=True)
    port_count = serializers.IntegerField(source='ports.count', read_only=True)

    class Meta:
        model = Host
        fields = [
            'id', 'ip_address', 'hostname', 'os_family',
            'mac_address', 'is_up', 'discovered_at', 'port_count', 'ports'
        ]


class ScanSerializer(serializers.ModelSerializer):
    """Serializer کامل برای نمایش اسکن"""
    user = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    scan_type_display = serializers.CharField(source='get_scan_type_display', read_only=True)
    host_count = serializers.IntegerField(source='hosts.count', read_only=True)
    hosts = HostSerializer(many=True, read_only=True)

    class Meta:
        model = Scan
        fields = [
            'id', 'user', 'target', 'scan_type', 'scan_type_display',
            'status', 'status_display', 'started_at', 'finished_at',
            'error_message', 'host_count', 'hosts'
        ]
        read_only_fields = ['user', 'status', 'started_at', 'finished_at', 'error_message']


class ScanCreateSerializer(serializers.ModelSerializer):
    """Serializer برای ساخت اسکن جدید"""

    class Meta:
        model = Scan
        fields = ['target', 'scan_type']

    def validate_target(self, value):
        """اعتبارسنجی هدف"""
        if not value.strip():
            raise serializers.ValidationError('هدف نمی‌تونه خالی باشه.')
        return value.strip()

    def create(self, validated_data):
        user = self.context['request'].user
        scan = Scan.objects.create(
            user=user,
            status='pending',
            **validated_data
        )
        # اجرای اسکن async
        from .tasks import run_scan
        run_scan.delay(scan.id)
        return scan