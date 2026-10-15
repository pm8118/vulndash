import nmap
from django.utils import timezone


class NmapScanner:
    """سرویس اسکن با Nmap"""

    def __init__(self):
        self.nm = nmap.PortScanner()

    def scan_quick(self, target):
        """اسکن سریع - 100 پورت معروف"""
        return self.nm.scan(hosts=target, arguments='-T4 -F')

    def scan_full(self, target):
        """اسکن کامل - همه پورت‌ها"""
        return self.nm.scan(hosts=target, arguments='-T4 -p-')

    def scan_stealth(self, target):
        """اسکن مخفیانه با SYN"""
        return self.nm.scan(hosts=target, arguments='-sS -T2 -F')

    def scan(self, target, scan_type='quick'):
        """اجرای اسکن بر اساس نوع"""
        if scan_type == 'full':
            return self.scan_full(target)
        elif scan_type == 'stealth':
            return self.scan_stealth(target)
        else:
            return self.scan_quick(target)