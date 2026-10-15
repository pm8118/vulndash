from celery import shared_task
from django.utils import timezone
from .models import Scan, Host, Port
from .services.nmap_scanner import NmapScanner


@shared_task
def run_scan(scan_id):
    """اجرای اسکن به صورت async"""
    try:
        scan = Scan.objects.get(id=scan_id)
    except Scan.DoesNotExist:
        return f"Scan {scan_id} not found"

    # وضعیت: در حال اجرا
    scan.status = 'running'
    scan.save()

    try:
        scanner = NmapScanner()
        result = scanner.scan(scan.target, scan.scan_type)

        # پردازش نتایج
        for host_ip in result.get('scan', {}):
            host_data = result['scan'][host_ip]

            # ذخیره هاست
            hostnames = host_data.get('hostnames', [])
            hostname = hostnames[0].get('name', '') if hostnames else ''

            host, created = Host.objects.get_or_create(
                scan=scan,
                ip_address=host_ip,
                defaults={
                    'hostname': hostname,
                    'is_up': host_data.get('status', {}).get('state') == 'up',
                }
            )

            # ذخیره پورت‌ها
            for protocol in ['tcp', 'udp']:
                if protocol in host_data:
                    for port_num, port_data in host_data[protocol].items():
                        Port.objects.get_or_create(
                            host=host,
                            number=port_num,
                            protocol=protocol,
                            defaults={
                                'state': port_data.get('state', 'open'),
                                'service': port_data.get('name', ''),
                                'version': f"{port_data.get('product', '')} {port_data.get('version', '')}".strip(),
                            }
                        )

        # وضعیت: تکمیل شده
        scan.status = 'completed'
        scan.finished_at = timezone.now()
        scan.save()

        return f"Scan {scan_id} completed successfully"

    except Exception as e:
        scan.status = 'failed'
        scan.error_message = str(e)
        scan.finished_at = timezone.now()
        scan.save()
        return f"Scan {scan_id} failed: {e}"