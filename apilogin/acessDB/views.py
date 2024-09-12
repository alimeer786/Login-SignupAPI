from rest_framework import generics
from .serializers import acessDBSerializer, UpdateAcessDBSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import acessDB
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django.core.exceptions import FieldDoesNotExist
from django.views import View
from django.templatetags.static import static
from django.db.models import Sum
from .utils import generate_multiple_projects_erection_report


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

class FilterFieldView(APIView):
    def get(self, request, field_name, *args, **kwargs):
        valid_fields = [f.name for f in acessDB._meta.get_fields()]
        
        if field_name not in valid_fields:
            return Response({"error": "Invalid field name"}, status=status.HTTP_400_BAD_REQUEST)

        field_values = acessDB.objects.values_list(field_name, flat=True)
        return Response(list(field_values))



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

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.units import inch
from datetime import datetime
from .models import acessDB

import arabic_reshaper

def create_line(width=1.0, height=0.05, color=colors.black):
    drawing = Drawing(width, height)
    drawing.add(Line(0, 0, width, 0, strokeColor=color))
    return drawing


def TechnicalTransmittalFormView(request):
    # Fetch data from the database
    data = acessDB.objects.all()

    # Set up the HttpResponse with the PDF response type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transmittal_report.pdf"'

    # Create a document and set page size
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    # Load styles and update if needed
    styles = getSampleStyleSheet()
    if 'Title' in styles:
        styles['Title'].fontName = 'Helvetica-Bold'
        styles['Title'].fontSize = 16
        styles['Title'].spaceAfter = 12
    else:
        styles.add(ParagraphStyle(name='Title', fontName='Helvetica-Bold', fontSize=16, spaceAfter=12))

    if 'Normal' in styles:
        styles['Normal'].fontName = 'Helvetica'
        styles['Normal'].fontSize = 10

    # Logos paths
    logo_path_left = "C:/Users/alime/Proj1/apilogin/acessDB/static/images/logo1.png"
    logo_path_right = "C:/Users/alime/Proj1/apilogin/acessDB/static/images/logo2.png"

    # Load logos
    left_logo = Image(logo_path_left, width=50, height=50)
    right_logo = Image(logo_path_right, width=50, height=50)

    # Create header with logos and text
    header_table_data = [
        [right_logo,
         Table([
             [Paragraph("لحلول الخرسانية المبتكرة ذ م م", ParagraphStyle(name='ArabicTitle', fontName='Helvetica-Bold', fontSize=16, alignment=1))],
             [Paragraph("Innovative Concrete Solutions", styles['Title'])],
             [Paragraph("Technical Transmittal Form", styles['Title'])],
         ], colWidths=[None], spaceBefore=5, spaceAfter=5),
         left_logo]
    ]

    header_table = Table(header_table_data, colWidths=[1.5 * inch, None, 1.5 * inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.2 * inch))

    # Add a horizontal line to separate header and table
    line = create_line(width=doc.width, height=0.05)
    elements.append(line)
    elements.append(Spacer(1, 0.2 * inch))

    # Add transmittal details
    transmittal_info = Table([
        ['Transmittal Number: 2256', '', 'Transmittal Date: 9/6/2024 11:25:19 PM']
    ], colWidths=[200, 140, 200])
    transmittal_info.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(transmittal_info)

    # Title
    title = Paragraph("Technical Transmittal Form", styles['Title'])
    elements.append(title)

    # Add a spacer
    elements.append(Spacer(1, 12))

    # Table data
    table_data = [
        ['Project', 'Element Tag', 'Rev.', 'Rev. Date', 'Quantity', 'Casting Factory', 'Volume (CM)'],  # Header
    ]

    transmittal_number = 2256

    # Populate table with dynamic data
    for entry in data:
        row = [
            entry.p_no,
            entry.e_tag,
            entry.rev,
            entry.issue.strftime('%m/%d/%Y'),
            entry.qty,
            "AHCC UAQ",  # Assuming a static value for "Casting Factory"
            entry.vol,
        ]
        table_data.append(row)

    # Create table with style
    table = Table(table_data, colWidths=[60, 120, 40, 80, 60, 100, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header row background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header row text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header row font
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header row padding
    ]))

    # Add table to the document elements
    elements.append(table)

    # Summary Section
    total_volume = sum([entry.vol for entry in data])
    elements.append(Paragraph(f"Issued Elements for Project {data[0].p_no if data else ''}: (3 Elements) with a Total Volume of: {total_volume:.2f}", styles['Normal']))
    
    # Add a line and a spacer
    elements.append(create_line(width=doc.width))
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph("Count of Drawings: 2", styles['Normal']))
    
    # Add a line and a spacer
    elements.append(create_line(width=doc.width))
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph(f"Total Volume in factory: {total_volume:.3f}", styles['Normal']))
    
    # Add a line and a spacer
    elements.append(create_line(width=doc.width))
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph(f"Grand Total Volume: {total_volume:.3f}", styles['Normal']))
    
    # Add a line and a spacer
    elements.append(create_line(width=doc.width))
    elements.append(Spacer(1, 12))
    
    # Additional Information Section
    elements.append(Paragraph(f"Transmittal Number: {transmittal_number}", styles['Normal']))
    
    # Add a line and a spacer
    elements.append(create_line(width=doc.width))
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph("All drawings related to elements listed above in this transmittal were received as per the date mentioned above:", styles['Normal']))
    
    # Add a line and a spacer
    elements.append(create_line(width=doc.width))
    elements.append(Spacer(1, 12))
    
    # Comments Section
    elements.append(Paragraph("Comments (If Any):", styles['Normal']))
    
    # Add a line and a spacer
    elements.append(create_line(width=doc.width))
    elements.append(Spacer(1, 12))
    
    elements.append(Spacer(1, 24))

    # Signature Section
    elements.append(Paragraph("Name of Production Engineer: ____________________    Signature: ____________________", styles['Normal']))
    
    # Add a line and a spacer
    elements.append(create_line(width=doc.width))
    elements.append(Spacer(1, 12))

    # Footer with current date
    current_date = datetime.now().strftime('%A, %B %d, %Y')
    elements.append(Paragraph(current_date, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Build the PDF
    doc.build(elements)

    return response



from django.views import View
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from django.conf import settings
import os

class ErectionReportView(View):
    def get(self, request, *args, **kwargs):
        # Create a file-like buffer to receive PDF data
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=18
        )

        # Container for the 'Flowable' objects
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center', alignment=1))
        styles.add(ParagraphStyle(name='Right', alignment=2))
        styles.add(ParagraphStyle(name='ArabicTitle', fontName='Helvetica-Bold', fontSize=16, alignment=1))

        # Logos paths
        logo_path_left = "C:/Users/alime/Proj1/apilogin/acessDB/static/images/logo1.png"
        logo_path_right = "C:/Users/alime/Proj1/apilogin/acessDB/static/images/logo2.png"

        # Load logos
        left_logo = Image(logo_path_left, width=50, height=50)
        right_logo = Image(logo_path_right, width=50, height=50)

        # Create header with logos and text
        header_table_data = [
            [right_logo,
             Table([
                 [Paragraph("لحلول الخرسانية المبتكرة ذ م م", styles['ArabicTitle'])],
                 [Paragraph("Innovative Concrete Solutions", styles['Title'])],
                 [Paragraph("Technical Transmittal Form", styles['Title'])],
             ], colWidths=[None], spaceBefore=5, spaceAfter=5),
             left_logo]
        ]

        header_table = Table(header_table_data, colWidths=[1.5 * inch, None, 1.5 * inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        # Add header to elements
        elements.append(header_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Add a horizontal line to separate header and table
        line = Table([['']], colWidths=[doc.width])  # Use doc.width here correctly
        line.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, 0), 1, colors.black)]))
        elements.append(line)
        elements.append(Spacer(1, 0.2 * inch))

        # Add main table (rest of the code remains the same)
        main_data = [
            ['PROJECT_NO', 'Element_Tag', 'Rev.', 'Element #', 'Quantity', 'Erection Date', 'Length(mm)'],
            ['', '', '', '', 'of', '', ''],
        ]
        main_table = Table(main_data, colWidths=[1.2 * inch, 1.2 * inch, 0.6 * inch, 1.2 * inch, 1 * inch, 1.5 * inch, 1.3 * inch])
        main_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        elements.append(main_table)
        
         # Add total row
        total_row = [['Total Number Of elements : (0 Elements)', '', '', '', '', 'Total Length', '0']]
        total_table = Table(total_row, colWidths=[1.2*inch, 1.2*inch, 0.6*inch, 1.2*inch, 1*inch, 1.5*inch, 1.3*inch])
        total_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('SPAN', (0,0), (4,0)),
            ('ALIGN', (-2,-1), (-1,-1), 'RIGHT'),
        ]))
        elements.append(total_table)
        elements.append(Spacer(1, 0.2*inch))

        # Add quality check section
        quality_data = [
            ['(For Internal use)', 'Quality of products checked and Approved for Erection By :'],
            ['', 'Date:____________ Name:____________________ Signature:____________________'],
            ['', 'Comments (If Any)___________________________________________________________'],
        ]
        quality_table = Table(quality_data, colWidths=[2*inch, 6*inch])
        quality_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('SPAN', (0,0), (0,-1)),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(quality_table)
        elements.append(Spacer(1, 0.2*inch))

        # Add Erection Engineer Comments section
        comments = Paragraph("Erection Engineer Comments:", styles['Normal'])
        elements.append(comments)
        comments_lines = Table([[''] * 5] * 5, colWidths=[1.6*inch] * 5)
        comments_lines.setStyle(TableStyle([
            ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 0.2*inch),
        ]))
        elements.append(comments_lines)
        elements.append(Spacer(1, 0.2*inch))

        # Add footer
        footer_table = Table([
            [Paragraph("Friday, September 6, 2024", styles['Normal']), Paragraph("Page 1 of 1", styles['Right'])]
        ], colWidths=[7*inch, 1*inch])
        elements.append(footer_table)




        # Build the PDF
        doc.build(elements)

        # Get the value of the BytesIO buffer and write it to the response
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="erection_report.pdf"'
        response.write(pdf)
        return response
    
from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from io import BytesIO
from bidi.algorithm import get_display
import os

def ManpowerReportView(request):
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Create the PDF object, using the buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=18)

       # Styles
    styles = getSampleStyleSheet()
    
    # Instead of adding new styles, we'll modify existing ones or create new ones with unique names
    styles['Title'].alignment = 1  # Center alignment
    styles['Title'].fontSize = 14
    

    font_path = r"C:\Users\alime\Proj1\apilogin\acessDB\fonts\Arabic\fonts\AF_DIWAN.TTF"
    pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
    
    
    # Arabic text reshaping and bidirectional correction
    arabic_text = "لحلول الخرسانية المبتكرة ذ م م"
    reshaped_text = arabic_reshaper.reshape(arabic_text)
    bidi_text = get_display(reshaped_text)


    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=14, alignment=1, spaceAfter=6)
    arabic_title_style = ParagraphStyle('ArabicTitle', fontName='ArabicFont', fontSize=16, alignment=1, spaceAfter=6)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12, alignment=1)


    # Logos paths
    logo_path_left = "C:/Users/alime/Proj1/apilogin/acessDB/static/images/logo1.png"
    logo_path_right = "C:/Users/alime/Proj1/apilogin/acessDB/static/images/logo2.png"
    

    # Load logos
    left_logo = Image(logo_path_left, width=50, height=50)
    right_logo = Image(logo_path_right, width=50, height=50)

    # Create header with logos and text
    header_table_data = [
        [right_logo, 
         Table([
             [Paragraph(bidi_text, arabic_title_style)],
             [Paragraph("Innovative Concrete Solutions", title_style)],
             [Paragraph("Multiple Projects Erection Report", subtitle_style)],
         ], colWidths=[None], spaceBefore=5, spaceAfter=5),
         left_logo]
    ]

    header_table = Table(header_table_data, colWidths=[1.5 * inch, None, 1.5 * inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))

    # Container for the 'Flowable' objects
    elements = []

    # Add header to elements
    elements.append(header_table)
    elements.append(Spacer(1, 0.2 * inch))

    # Add a horizontal line to separate header and table
    line = Table([['']], colWidths=[doc.width])
    line.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, 0), 1, colors.black)]))
    elements.append(line)
    elements.append(Spacer(1, 0.2 * inch))

    # Report details
    report_details = [
        ['ReportNumber', '744', 'ReportDate', '1/1/2023'],
    ]
    report_table = Table(report_details, colWidths=[doc.width/4]*4)
    report_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(report_table)
    elements.append(Spacer(1, 0.2 * inch))

    # Manpower data
    manpower_data = [
        ['AHCC LABOURS', '', 'SUPPLY LABOURS', ''],
        ['Engineers', '8', 'S_Engineers', '0'],
        ['inspectors', '0', 'S_Inspectors', '0'],
        ['Foreman', '8', 'S_Foreman', '0'],
        ['Leader', '13', 'S_Leader', '0'],
        ['CraneOperator', '8', 'S_CraneOperator', '0'],
        ['SteelFixer', '13', 'S_SteelFixer', '0'],
        ['MoldFabricator', '0', 'S_MoldFabricator', '0'],
        ['Welder', '13', 'S_Welder', '0'],
        ['Carpentors', '0', 'S_Carpentors', '0'],
        ['Masons', '26', 'S_Masons', '0'],
        ['Reggers', '13', 'S_Riggers', '0'],
        ['Helpers', '13', 'S_Helpers', '0'],
        ['UnskilledLabours', '0', 'S_UnskilledLabours', '0'],
    ]

    manpower_table = Table(manpower_data, colWidths=[doc.width/4]*4)
    manpower_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
        ('BACKGROUND', (2, 0), (3, 0), colors.lightgrey),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    elements.append(manpower_table)

    # Footer
    elements.append(Spacer(1, 0.2 * inch))
    footer_text = "Report Prepared By: _________________ Signature: _________________ Comments (If Any): _________________"
    elements.append(Paragraph(footer_text, styles['Normal']))

    # Build the PDF
    doc.build(elements)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')





# views.py
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from .models import acessDB
from django.template.loader import render_to_string
from weasyprint import HTML
from django.templatetags.static import static

def dynamic_view(request, api_name, *args, **kwargs):
    # Handle different api_name values
    if api_name == 'technical-transmittal':
        return technical_transmittal_form(request)
    elif api_name == 'erection-report':
        return erection_report(request)
    elif api_name == 'manpower-report':
        return manpower_report(request)
    elif api_name == 'inspection-report':
        return inspection_report(request)
    elif api_name == 'delivery-order':
        do_number = kwargs.get('do_number')
        return delivery_order_view(request, do_number)
    else:
        raise Http404("Endpoint not found")
    









# views.py
from django.shortcuts import render
from django.http import HttpResponse
from .models import acessDB
from datetime import datetime
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models import Sum

def technical_transmittal_form(request):
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
    pdf_file = HTML(string=html_string).write_pdf()

    # Create a HTTP response for PDF download
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="technical_transmittal_form_{project_number}.pdf"'

    return response



# views.py
# views.py
from django.shortcuts import render
from django.http import HttpResponse
from .models import acessDB
from django.template.loader import render_to_string
from weasyprint import HTML
from datetime import datetime
from django.db.models import Sum

def inspection_report(request):
    # Fetch dynamic data from model or request
    project_number = request.GET.get('project_number')
    data = acessDB.objects.filter(p_no=project_number)
    
    # Process data
    total_elements = data.count()
    total_length = data.aggregate(total_length=Sum('vol'))['total_length'] or 0
    
    # Context for the report
    context = {
        'company_name_arabic': 'الحلول الخرسانية المبتكرة ذ م م',
        'company_name_english': 'Innovative Concrete Solutions',
        'report_title': 'Inspection Report',
        'project_number': project_number,
        'report_date': datetime.now().strftime('%m/%d/%Y %I:%M:%S %p'),
        'data': data,
        'total_elements': total_elements,
        'total_length': total_length,
    }

    # Render the HTML template
    html_string = render_to_string('acessDB/inspection_report.html', context)

    # Convert the HTML to PDF
    pdf_file = HTML(string=html_string).write_pdf()

    # Create a HTTP response for PDF download
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="inspection_report_{project_number}.pdf"'

    return response



# views.py
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.template.loader import render_to_string
from weasyprint import HTML

def manpower_report(request):
    # Dynamic data from request or model
    report_number = request.GET.get('report_number', '744')
    report_date = request.GET.get('report_date', datetime.now().strftime('%m/%d/%Y'))
    
    # Static data or example (you may fetch this from a model or other sources)
    labour_data = {
        'Engineers': {'ahcc_labours': 8, 'supply_labours': 0},
        # (other labour data...)
    }
    
    # Context for the report
    context = {
        'company_name_arabic': 'الحلول الخرسانية المبتكرة ذ م م',
        'company_name_english': 'Innovative Concrete Solutions',
        'report_title': 'Manpower Report',
        'report_number': report_number,
        'report_date': report_date,
        'labour_data': labour_data,
    }

    # Render the HTML template
    html_string = render_to_string('acessDB/manpower_report.html', context)

    # Convert the HTML to PDF
    pdf_file = HTML(string=html_string).write_pdf()

    # Create a HTTP response for PDF download
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="manpower_report_{report_number}.pdf"'

    return response

# views.py
from django.shortcuts import render
from django.http import HttpResponse
from .models import acessDB
from datetime import datetime
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models import Sum

def erection_report(request):
    # Fetch dynamic data from model or request
    project_number = request.GET.get('project_number')
    data = acessDB.objects.filter(p_no=project_number)
    
    # Process data
    total_elements = data.count()
    total_length = data.aggregate(total_length=Sum('vol'))['total_length'] or 0
    
    # Context for rendering the template
    context = {
        'company_name_arabic': 'الحلول الخرسانية المبتكرة ذ م م',
        'company_name_english': 'Innovative Concrete Solutions',
        'report_title': 'Erection Report',
        'project_number': project_number,
        'report_date': datetime.now().strftime('%m/%d/%Y %I:%M:%S %p'),
        'data': data,
        'total_elements': total_elements,
        'total_length': total_length,
    }
    
    # Render the HTML template to a string
    html_string = render_to_string('acessDB/erection_report.html', context)

    # Convert the rendered HTML to a PDF
    pdf_file = HTML(string=html_string).write_pdf()

    # Create a HTTP response to download the PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="erection_report_{project_number}.pdf"'

    return response




from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import acessDB
from django.templatetags.static import static

def delivery_order_view(request, do_number):
    # Retrieve the data based on delivery order number (you can adjust the filtering logic as needed)
    try:
        order_data = acessDB.objects.get(do=do_number)
    except acessDB.DoesNotExist:
        order_data = None  # Handle the case where the delivery order does not exist

    # Generate the URLs for the logos
    logo_path_left = static('images/logo1.png')
    logo_path_right = static('images/logo2.png')

    # Prepare context for the template
    context = {
        'order': order_data,
        'logo_path_left': logo_path_left,
        'logo_path_right': logo_path_right,
    }

    # Render the HTML template with context
    html_string = render_to_string('acessDB/delivery_order.html', context)

    # Create a PDF from the HTML string
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    # Return the PDF as a response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=delivery_order_{do_number}.pdf'
    return response


# acessDB/views.py
from django.http import HttpResponse, Http404
from django.shortcuts import render
from .models import acessDB
from django.template.loader import render_to_string
from weasyprint import HTML
from django.templatetags.static import static

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
        do_number = kwargs.get('do_number')
        if do_number is None:
            raise Http404("Delivery order number is required")
        return delivery_order_view(request, do_number)
    elif normalized_api_name == 'inspection-report':
        print("Accessing inspection_report view")
        return inspection_report(request)
    else:
        print("Endpoint not found")
        raise Http404("Endpoint not found")

