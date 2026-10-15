from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Scan, Host, Port, Vulnerability
from .serializers import (
    ScanSerializer, ScanCreateSerializer,
    HostSerializer, PortSerializer, VulnerabilitySerializer
)


@extend_schema_view(
    list=extend_schema(summary='لیست اسکن‌های کاربر', tags=['Scans']),
    retrieve=extend_schema(summary='جزئیات یه اسکن', tags=['Scans']),
    create=extend_schema(summary='ساخت اسکن جدید', tags=['Scans']),
    destroy=extend_schema(summary='حذف اسکن', tags=['Scans']),
)
class ScanViewSet(viewsets.ModelViewSet):
    """API برای مدیریت اسکن‌ها"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'scan_type']
    search_fields = ['target']
    ordering_fields = ['started_at', 'finished_at', 'status']
    ordering = ['-started_at']

    def get_queryset(self):
        return Scan.objects.filter(user=self.request.user).prefetch_related('hosts__ports')

    def get_serializer_class(self):
        if self.action == 'create':
            return ScanCreateSerializer
        return ScanSerializer

    @extend_schema(
        summary='آمار خلاصه اسکن‌ها',
        tags=['Scans'],
        responses={200: dict},
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار کلی اسکن‌های کاربر"""
        user_scans = Scan.objects.filter(user=request.user)
        scan_ids = user_scans.values_list('id', flat=True)

        return Response({
            'total_scans': user_scans.count(),
            'total_hosts': Host.objects.filter(scan_id__in=scan_ids).count(),
            'total_ports': Port.objects.filter(host__scan_id__in=scan_ids).count(),
            'total_vulnerabilities': Vulnerability.objects.filter(port__host__scan_id__in=scan_ids).count(),
            'by_status': {
                'pending': user_scans.filter(status='pending').count(),
                'running': user_scans.filter(status='running').count(),
                'completed': user_scans.filter(status='completed').count(),
                'failed': user_scans.filter(status='failed').count(),
            }
        })

    @extend_schema(
        summary='اسکن‌های در حال اجرا',
        tags=['Scans'],
    )
    @action(detail=False, methods=['get'])
    def running(self, request):
        """لیست اسکن‌های در حال اجرا"""
        running_scans = self.get_queryset().filter(status__in=['pending', 'running'])
        serializer = ScanSerializer(running_scans, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary='لیست هاست‌ها', tags=['Hosts']),
    retrieve=extend_schema(summary='جزئیات هاست', tags=['Hosts']),
)
class HostViewSet(viewsets.ReadOnlyModelViewSet):
    """API برای هاست‌ها"""
    serializer_class = HostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Host.objects.filter(scan__user=self.request.user)


@extend_schema_view(
    list=extend_schema(summary='لیست پورت‌ها', tags=['Ports']),
    retrieve=extend_schema(summary='جزئیات پورت', tags=['Ports']),
)
class PortViewSet(viewsets.ReadOnlyModelViewSet):
    """API برای پورت‌ها"""
    serializer_class = PortSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Port.objects.filter(host__scan__user=self.request.user)


@extend_schema_view(
    list=extend_schema(summary='لیست آسیب‌پذیری‌ها', tags=['Vulnerabilities']),
    retrieve=extend_schema(summary='جزئیات آسیب‌پذیری', tags=['Vulnerabilities']),
)
class VulnerabilityViewSet(viewsets.ReadOnlyModelViewSet):
    """API برای آسیب‌پذیری‌ها"""
    serializer_class = VulnerabilitySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['severity']

    def get_queryset(self):
        return Vulnerability.objects.filter(port__host__scan__user=self.request.user)