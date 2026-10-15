from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from scanner.models import Scan, Host, Port, Vulnerability


class DashboardView(LoginRequiredMixin, TemplateView):
    """داشبورد اصلی با آمار و نمودار"""
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # اسکن‌های کاربر
        user_scans = Scan.objects.filter(user=user)
        scan_ids = user_scans.values_list('id', flat=True)

        # آمار کلی
        context['total_scans'] = user_scans.count()
        context['total_hosts'] = Host.objects.filter(scan_id__in=scan_ids).count()
        context['total_ports'] = Port.objects.filter(host__scan_id__in=scan_ids).count()
        context['total_vulns'] = Vulnerability.objects.filter(port__host__scan_id__in=scan_ids).count()

        # آمار وضعیت اسکن‌ها (برای نمودار دایره‌ای)
        status_counts = user_scans.values('status').annotate(count=Count('id'))
        context['status_labels'] = []
        context['status_data'] = []
        status_map = {
            'pending': 'در انتظار',
            'running': 'در حال اجرا',
            'completed': 'تکمیل شده',
            'failed': 'ناموفق',
        }
        for item in status_counts:
            context['status_labels'].append(status_map.get(item['status'], item['status']))
            context['status_data'].append(item['count'])

        # آمار پورت‌های باز (برای نمودار میله‌ای)
        top_services = (
            Port.objects
            .filter(host__scan_id__in=scan_ids)
            .exclude(service='')
            .values('service')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        context['service_labels'] = [s['service'] for s in top_services]
        context['service_data'] = [s['count'] for s in top_services]

        # ۵ اسکن آخر
        context['recent_scans'] = user_scans.order_by('-started_at')[:5]

        return context