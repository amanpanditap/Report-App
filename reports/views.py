from django import http
from django.shortcuts import get_object_or_404, render
from profiles.models import Profile
from django.http import JsonResponse
from .utils import get_report_image
from .models import Report
from .forms import ReportForm
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.generic import ListView, DetailView, TemplateView
from sales.models import Sale, Position, CSV
from products.models import Product
from customers.models import Customer
from django.utils.dateparse import parse_date
import csv
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'reports/main.html'

class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'reports/detail.html'

class UploadTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/from_file.html'

@login_required
def csv_upload_view(request):
    print('File is being Uploaded')

    if request.method == 'POST':
        csv_file_name = request.FILES.get('file').name
        csv_file = request.FILES.get('file')
        obj, created = CSV.objects.get_or_create(file_name = csv_file_name)

        if created:
            obj.csv_file = csv_file
            obj.save()
            with open(obj.csv_file.path, 'r') as f:
                reader = csv.reader(f)
                reader.__next__()
                for row in reader:
                    #print(row, type(row))
                    data = ";".join(row)
                    #print(data, type(data))
                    data = data.split(';')
                    #print(data, type(data))
                    data.pop()
                    #print(data)
        
                    a = data[1].split()
                    transaction_id = a[0]
                    b = data[2].split()
                    product = b[0]
                    c = data[3].split()
                    quantity = c[0]
                    d = data[4].split()
                    customer = d[0]
                    date = parse_date(str(data[5].split()[0]))
                    print(date)

                    try:
                        product_obj = Product.objects.get(name__iexact = product)
                    except Product.DoesNotExist:
                        product_obj = None
                    
                    print(product_obj)

                    if product_obj is not None:
                        customer_obj, _ = Customer.objects.get_or_create(name=customer) 
                        salesman_obj = Profile.objects.get(user=request.user)
                        position_obj = Position.objects.create(product=product_obj, quantity= int(quantity), created=date)

                        sale_obj, _ = Sale.objects.get_or_create(transaction_id=transaction_id, customer=customer_obj, salesman=salesman_obj, created=date)
                        sale_obj.positions.add(position_obj)
                        sale_obj.save()

                return JsonResponse({'ex': False})
        else:
            return JsonResponse({'ex': True})

    return HttpResponse()

@login_required
def create_report_view(request):
    form = ReportForm(request.POST or None)
    if request.is_ajax():
        image = request.POST.get('image')
        img = get_report_image(image)
        author = Profile.objects.get(user=request.user)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.image = img
            instance.author = author
            instance.save()
    
    # Other Way without form and using Models
    # if request.is_ajax():
    #     name = request.POST.get('name')
    #     remarks = request.POST.get('remarks')
    #     image = request.POST.get('image')

    #     img = get_report_image(image)

    #     author = Profile.objects.get(user = request.user)
    #     Report.objects.create(name=name, remarks=remarks,image= img, author=author)
        return JsonResponse({'msg': 'send'})
    return JsonResponse({})

@login_required
def render_pdf_view(request, pk):
    template_path = 'reports/pdf.html'
    obj = get_object_or_404(Report, pk=pk)
    context = {'obj': obj}

    response = HttpResponse(content_type='application/pdf')
    #response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # If Download
    response['Content-Disposition'] = 'filename="report.pdf"'
    # If Display
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response