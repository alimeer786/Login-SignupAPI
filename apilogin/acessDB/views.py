from rest_framework import generics
from .serializers import acessDBSerializer, UpdateAcessDBSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import acessDB
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.utils import timezone
from django.core.exceptions import FieldDoesNotExist
from django.views import View
from django.templatetags.static import static
from django.db.models import Sum
from .utils import generate_multiple_projects_erection_report

from django.shortcuts import render
from datetime import datetime
from django.template.loader import render_to_string
from weasyprint import HTML, CSS


# -----------------------------------
# Views for Perfoming CRUD Operations
# -----------------------------------

class acessDBCreateView(generics.ListCreateAPIView):
    queryset = acessDB.objects.all()
    serializer_class = acessDBSerializer

class acessDBDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = acessDB.objects.all()
    serializer_class = acessDBSerializer

class UpdateAcessDBView(generics.UpdateAPIView):
    queryset = acessDB.objects.all()
    serializer_class = UpdateAcessDBSerializer
    lookup_field = 'id'


# ----------------------
# View for Filter Field 
# ----------------------

class FilterFieldView(APIView):
    def get(self, request, field_name, *args, **kwargs):
        valid_fields = [f.name for f in acessDB._meta.get_fields()]
        
        if field_name not in valid_fields:
            return Response({"error": "Invalid field name"}, status=status.HTTP_400_BAD_REQUEST)

        field_values = acessDB.objects.values_list(field_name, flat=True)
        return Response(list(field_values))

# ---------------------------------------------------------
# View for Muliple Projects Erection Report with WeasyPrint
# ---------------------------------------------------------

class MultipleProjectsErectionReportView(APIView):
    def get(self, request):
        # Get the report date
        report_date = timezone.now().strftime("%Y-%m-%d")

        # Get fields from query parameters
        fields = request.GET.get('fields', '').split(',')
        fields = [field.strip() for field in fields if field.strip()]

        if not fields:
            return HttpResponseBadRequest("No fields specified")

        # Validate fields
        valid_fields = []
        for field in fields:
            try:
                acessDB._meta.get_field(field)
                valid_fields.append(field)
            except FieldDoesNotExist:
                pass

        if not valid_fields:
            return HttpResponseBadRequest("No valid fields specified")

        # Get project number from query parameters
        project_number = request.GET.get('project_number', None)

        # Calculate total volume for the specified project number if provided
        if project_number:
            try:
                total_volume = acessDB.objects.filter(p_no=project_number).aggregate(total_volume=Sum('vol'))['total_volume']
                if total_volume is None:
                    total_volume = 0
            except FieldDoesNotExist:
                total_volume = 0
        else:
            total_volume = 0

        # Fetch all data from the model
        data = acessDB.objects.values(*valid_fields)

        # Define logo paths
        left_logo_path = 'images/logo1.png'
        right_logo_path = 'images/logo2.png'

        try:
            # Generate the PDF with all data and total volume for the specified project number
            pdf = generate_multiple_projects_erection_report(
                data,
                report_date,
                valid_fields,
                left_logo_path,
                right_logo_path,
                project_number if project_number else 'All Projects',
                total_volume
            )
        except Exception as e:
            return HttpResponseBadRequest(f"Error generating PDF: {str(e)}")

        # Create the HTTP response with PDF content
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="multiple_projects_erection_report_{report_date}.pdf"'

        return response


# -----------------------------------------
# View for Technical Transmittal with WeasyPrint
# -----------------------------------------


# To Acess URL: http://localhost:8000/api/main_api/inspection-report/

def technical_transmittal_form(request):


    css = CSS(string='''
    @page {
        size: A4;
        margin: 10mm;
    }
    body {
        width: 190mm; /* A4 page width minus margins */
        margin: 0;
        padding: 0;
    }
 ''')
    print("Inside technical_transmittal_form function")
    # Fetch dynamic data from the model or request
    project_number = request.GET.get('project_number')
    
    # Example of fetching data based on the project number
    items = acessDB.objects.filter(p_no=project_number)
    
    # Process data
    total_elements = items.count()
    total_volume = items.aggregate(total_volume=Sum('vol'))['total_volume'] or 0
    count_drawings = items.count()  # Adjust this as needed based on your data
    total_volume_factory = total_volume  # Example, you might have different logic
    grand_total_elements = total_elements
    grand_total_volume = total_volume
    
    # Context for the form
    context = {
        'company_name_arabic': 'الحلول الخرسانية المبتكرة ذ م م',
        'company_name_english': 'Innovative Concrete Solutions',
        'form_title': 'Technical Transmittal Form',
        'transmittal_number': '123456',  # Static example, replace with dynamic data if available
        'transmittal_date': datetime.now().strftime('%m/%d/%Y'),
        'issued_for': 'Example Issued For',
        'factory_name': 'Example Factory Name',
        'project_number': project_number,
        'items': items,
        'total_elements': total_elements,
        'total_volume': total_volume,
        'count_drawings': count_drawings,
        'total_volume_factory': total_volume_factory,
        'grand_total_elements': grand_total_elements,
        'grand_total_volume': grand_total_volume,
        'report_date': datetime.now().strftime('%A, %B %d, %Y'),
    }
    
    # Render the HTML template
    html_string = render_to_string('acessDB/technical_transmittal_form.html', context)

    # Convert the HTML to PDF
    pdf_file = HTML(string=html_string).write_pdf(stylesheets=[css])

    # Create a HTTP response for PDF download
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="technical_transmittal_form_{project_number}.pdf"'

    return response



# -----------------------------------------
# View for Inspection-Report with WeasyPrint
# -----------------------------------------

# To Acess URL: http://localhost:8000/api/main_api/inspection-report/?project_number=1001

def inspection_report(request):
    """
    Generates a PDF for the Inspection Report using WeasyPrint.
    Renders the report template with dynamic data and converts it to a PDF.
    """

    # CSS for PDF formatting
    css = CSS(string='''
    @page {
        size: A4;
        margin: 10mm;
    }
    body {
        width: 190mm; /* A4 page width minus margins */
        margin: 0;
        padding: 0;
    }
    ''')

    # Fetching dynamic data (replace with actual model data or request data)
    project_number = request.GET.get('project_number', 'Unknown Project')
    data = acessDB.objects.filter(p_no=project_number)
    
    # Aggregating data from the database
    total_elements = data.count()
    total_length = data.aggregate(total_length=Sum('vol'))['total_length'] or 0

    # Context to be passed to the HTML template
    context = {
        'company_name_arabic': 'الحلول الخرسانية المبتكرة ذ م م',
        'company_name_english': 'Innovative Concrete Solutions',
        'report_title': 'Inspection Report',
        'project_number': project_number,
        'report_date': datetime.now().strftime('%m/%d/%Y %I:%M:%S %p'),
        'client': 'Client Name',  # Add actual data
        'consultant': 'Consultant Name',  # Add actual data
        'location': 'Project Location',  # Add actual data
        'data': data,  # Table data
        'total_elements': total_elements,
        'total_length': total_length,
        'current_date': datetime.now().strftime('%A, %B %d, %Y'),
        'page_number': 1,  # Page number, update if you have pagination logic
        'total_pages': 1,  # Can be calculated dynamically
    }

    # Render the HTML template with the context
    html_string = render_to_string('acessDB/inspection_report.html', context)

    # Convert the rendered HTML to PDF
    pdf_file = HTML(string=html_string).write_pdf(stylesheets=[css])

    # Create the PDF response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="inspection_report_{project_number}.pdf"'

    return response



# -----------------------------------------
# View for Man-Power with WeasyPrint
# -----------------------------------------


# To acess URL: http://localhost:8000/api/main_api/manpower-report/?report_number=123&report_date=2024-09-21

def manpower_report(request):

    # Dynamic data from request or model (falling back to defaults)
    report_number = request.GET.get('report_number', '744')
    report_date = request.GET.get('report_date', datetime.now().strftime('%m/%d/%Y'))

    # Format current date for footer
    current_date = datetime.now()
    formatted_date = current_date.strftime('%A, %B %d, %Y')

    # Example labour data, can be retrieved from a model or API in real implementation
    labour_data = {
        'Engineers': {'ahcc_labours': 8, 'supply_labours': 3},
        'Inspectors': {'ahcc_labours': 5, 'supply_labours': 2},
        'Foreman': {'ahcc_labours': 4, 'supply_labours': 1},
        'Leader': {'ahcc_labours': 3, 'supply_labours': 3},
        'Crane Operator': {'ahcc_labours': 2, 'supply_labours': 2},
        'Steel Fixer': {'ahcc_labours': 10, 'supply_labours': 8},
        'Mold Fabricator': {'ahcc_labours': 7, 'supply_labours': 6},
        'Welder': {'ahcc_labours': 6, 'supply_labours': 5},
        'Carpenters': {'ahcc_labours': 9, 'supply_labours': 7},
        'Masons': {'ahcc_labours': 12, 'supply_labours': 10},
        'Riggers': {'ahcc_labours': 4, 'supply_labours': 3},
        'Helpers': {'ahcc_labours': 15, 'supply_labours': 12},
        'Unskilled Labours': {'ahcc_labours': 20, 'supply_labours': 18},
    }

    # Context to pass to the HTML template
    context = {
        'company_name_arabic': 'الحلول الخرسانية المبتكرة ذ م م',
        'company_name_english': 'Innovative Concrete Solutions',
        'report_title': 'Manpower Report',
        'report_number': report_number,
        'report_date': report_date,
        'current_date': datetime.now().strftime('%m/%d/%Y'),
        'footer_date': formatted_date,
        'labour_data': labour_data,  # Passing labour data to the template
        'page_number': 1,
        'total_pages': 1,  # This would be dynamic based on WeasyPrint pagination in a real implementation
    }

    # Render the HTML content from the template with the given context
    html_content = render_to_string('acessDB/manpower_report.html', context)

    # PDF rendering with WeasyPrint
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="manpower_report_{report_number}.pdf"'

    # Define custom CSS if necessary (for page size, margins, etc.)
    css = CSS(string='''
    @page {
        size: A4;
        margin: 10mm;
    }
    body {
        width: 190mm;
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
    }
    ''')

    # Generate and return the PDF
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(response, stylesheets=[css])

    return response


  
# -----------------------------------------
# View for Erection Report with WeasyPrint
# -----------------------------------------


#  To Acess URL: http://localhost:8000/api/main_api/erection-report/?project_number=101

def erection_report(request):


    css = CSS(string='''
    @page {
        size: A4;
        margin: 10mm;
    }
    body {
        width: 190mm; /* A4 page width minus margins */
        margin: 0;
        padding: 0;
    }
 ''')
    # Fetch project number from GET parameters
    project_number = request.GET.get('project_number')
    
    if not project_number:
        return HttpResponse("Project number is required", status=400)
    
    # Fetch data for the given project number
    data = acessDB.objects.filter(p_no=project_number)
    
    if not data.exists():
        return HttpResponse(f"No data found for project number {project_number}", status=404)
    
    # Process data: count elements and calculate total length
    total_elements = data.count()
    total_length = data.aggregate(total_length=Sum('vol'))['total_length'] or 0

    current_date = datetime.now()
    formatted_date = current_date.strftime('%A, %B %d, %Y')
    
    # Context for rendering the template
    context = {
        'company_name_arabic': 'الحلول الخرسانية المبتكرة ذ م م',
        'company_name_english': 'Innovative Concrete Solutions',
        'report_title': 'Erection Report',
        'project_no': project_number,  # Ensure these match the template variable names
        'project_name': 'Project Name Placeholder',  # Add real data if available
        'client': 'Client Placeholder',  # Add real data if available
        'consultant': 'Consultant Placeholder',  # Add real data if available
        'location': 'Location Placeholder',  # Add real data if available
        'report_date': datetime.now().strftime('%m/%d/%Y %I:%M:%S %p'),
        'elements': data,  # Assuming 'elements' is the context variable in your template
        'total_elements': total_elements,
        'total_length': total_length,
        'current_date': datetime.now().strftime('%m/%d/%Y'),
        'footer_date': formatted_date,
        'page_number': 1,  # WeasyPrint handles pagination, this might be used for custom content
        'total_pages': 1,  # WeasyPrint handles pagination, this might be used for custom content
    }

    # Render the HTML template to a string
    html_string = render_to_string('acessDB/erection_report.html', context)

    # Convert the rendered HTML to a PDF using WeasyPrint
    pdf_file = HTML(string=html_string).write_pdf(stylesheets=[css])

    # Create an HTTP response to download the PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="erection_report_{project_number}.pdf"'

    return response

# -----------------------------------------
# View for Delivery Order with WeasyPrint
# -----------------------------------------


#  To Acess URL: http://localhost:8000/api/main_api/delivery-order/?do_number=1001

def delivery_order_pdf(request, do_number):



    css = CSS(string='''
    @page {
        size: A4;
        margin: 10mm;
    }
    body {
        width: 190mm; /* A4 page width minus margins */
        margin: 0;
        padding: 0;
    }
 ''')
    # Fetch the data from the model using the provided delivery order number
    order_data = acessDB.objects.filter(do=do_number)
    
    # Handle case where no data is found
    if not order_data.exists():
        return HttpResponse(f"No data found for Delivery Order Number: {do_number}", status=404)

    # Calculating totals for elements and volume
    total_elements = order_data.count()
    total_volume = order_data.aggregate(total_volume=Sum('vol'))['total_volume'] or 0

    # Extracting details from the first entry (assuming all entries have same project/order details)
    first_entry = order_data.first()

    # Context for rendering the template
    context = {
        'logo_path_left': r"images\logo1.png",  # Update this with the correct logo path
        'logo_path_right': 'path/to/al_heloul_logo.png',  # Update with the correct logo path
        'order': {
            'do': first_entry.do,
            'delivery': first_entry.delivery.strftime('%m/%d/%Y'),
            'project_name': 'Sample Project Name',  # Replace with actual project name if available
            'p_no': first_entry.p_no,
            'client': 'Client Placeholder',  # Replace with actual client name
            'consultant': 'Consultant Placeholder',  # Replace with actual consultant name
            'location': 'Location Placeholder',  # Replace with actual location
            'transporter': first_entry.transporter
        },
        'elements': order_data,  # List of elements (from the model)
        'total_elements': total_elements,
        'total_volume': total_volume,
        'quality_check_date': datetime.now().strftime('%m/%d/%Y'),
        'quality_check_name': 'QC Inspector Name Placeholder',  # Replace with actual QC inspector name
        'driver_name': 'Driver Name Placeholder',  # Replace with actual driver name
        'vehicle_no': 'Vehicle No Placeholder',  # Replace with actual vehicle number
        'driver_mobile': 'Driver Mobile Placeholder',  # Replace with actual driver mobile number
        'footer_date': datetime.now().strftime('%A, %B %d, %Y'),
        'page_number': 1,  # WeasyPrint handles pagination
        'total_pages': 1,  # Set dynamically if needed
    }

    # Render the HTML template to a string
    html_string = render_to_string('acessDB/delivery_order.html', context)

    # Convert the rendered HTML to a PDF using WeasyPrint
    pdf_file = HTML(string=html_string).write_pdf(stylesheets=[css])

    # Create an HTTP response to serve the PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="delivery_order_{do_number}.pdf"'

    return response





# ----------------------------------------------------
# View for Dynamic Generation with WeasyPrint
# ----------------------------------------------------

def dynamic_view(request, api_name, *args, **kwargs):
    # Strip leading/trailing spaces and newline characters
    normalized_api_name = api_name.strip()
    print(f"Normalized API Name Requested: '{normalized_api_name}'")  # Ensure this is correctly indented
    
    # Compare with normalized values
    if normalized_api_name == 'technical-transmittal':
        print("Accessing technical_transmittal_form view")
        return technical_transmittal_form(request)
    elif normalized_api_name == 'erection-report':
        print("Accessing erection_report view")
        return erection_report(request)
    elif normalized_api_name == 'manpower-report':
        print("Accessing manpower_report view")
        return manpower_report(request)
    elif normalized_api_name == 'delivery-order':
        print("Accessing delivery_order_view view")
        do_number = request.GET.get('do_number')
        # do_number = kwargs.get('do_number')
        if do_number is None:
            raise Http404("Delivery order number is required")
        return delivery_order_pdf(request, do_number)
    elif normalized_api_name == 'inspection-report':
        print("Accessing inspection_report view")
        return inspection_report(request)
    else:
        print("Endpoint not found")
        raise Http404("Endpoint not found")

