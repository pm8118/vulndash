from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Scan
from .forms import ScanForm
from .tasks import run_scan


class ScanListView(LoginRequiredMixin, ListView):
    """لیست اسکن‌های کاربر"""
    model = Scan
    template_name = 'scanner/scan_list.html'
    context_object_name = 'scans'
    paginate_by = 10

    def get_queryset(self):
        return Scan.objects.filter(user=self.request.user)


class ScanCreateView(LoginRequiredMixin, CreateView):
    """ساخت اسکن جدید"""
    model = Scan
    form_class = ScanForm
    template_name = 'scanner/scan_create.html'
    success_url = reverse_lazy('scanner:scan_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 'pending'
        response = super().form_valid(form)
        # اجرای اسکن async
        run_scan.delay(self.object.id)
        messages.success(self.request, 'اسکن در صف اجرا قرار گرفت!')
        return response


class ScanDetailView(LoginRequiredMixin, DetailView):
    """جزئیات یه اسکن"""
    model = Scan
    template_name = 'scanner/scan_detail.html'
    context_object_name = 'scan'

    def get_queryset(self):
        return Scan.objects.filter(user=self.request.user)