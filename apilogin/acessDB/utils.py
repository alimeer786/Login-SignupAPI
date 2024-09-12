from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Line
from django.contrib.staticfiles import finders
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from bidi.algorithm import get_display
import arabic_reshaper

def generate_multiple_projects_erection_report(data, report_date, fields, left_logo_path, right_logo_path, p_no, total_vol):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch
    )
    elements = []

    # Ensure the font path is correct and the font supports Arabic characters
    font_path = r"C:\Users\alime\Proj1\apilogin\acessDB\fonts\Arabic\fonts\AF_DIWAN.TTF"
    pdfmetrics.registerFont(TTFont('ArabicFont', font_path))

    # Arabic text reshaping and bidirectional correction
    arabic_text = "لحلول الخرسانية المبتكرة ذ م م"
    reshaped_text = arabic_reshaper.reshape(arabic_text)
    bidi_text = get_display(reshaped_text)

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=14, alignment=1, spaceAfter=6)
    arabic_title_style = ParagraphStyle('ArabicTitle', fontName='ArabicFont', fontSize=16, alignment=1, spaceAfter=6)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12, alignment=1)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=10, alignment=1)
    custom_text_style = ParagraphStyle('CustomText', parent=styles['Normal'], fontSize=12, alignment=1, spaceAfter=6)

    # Locate logo paths
    left_logo_path = finders.find(left_logo_path)
    right_logo_path = finders.find(right_logo_path)

    # Add logos to header
    left_logo = Image(left_logo_path, width=2.2 * inch, height=1.5 * inch)
    right_logo = Image(right_logo_path, width=2.2 * inch, height=1.5 * inch)

    # Create a header table with logos and text
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

    elements.append(header_table)
    elements.append(Spacer(1, 0.1 * inch))

    # Add a horizontal line to separate header and table
    line = Drawing(doc.width, 0.5)  # Line width and height
    line.add(Line(0, 0, doc.width, 0, strokeColor=colors.black))
    elements.append(line)
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"Report Date: {report_date}", header_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Create table for column headers
    header_data = [fields]

    # Set column widths to evenly distribute across the full page width
    column_widths = [doc.width / len(fields)] * len(fields)

    # Create header table with no visible lines
    header_table = Table(header_data, colWidths=column_widths, repeatRows=1)
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),  # Header background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.grey),  # Header text color
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center alignment for all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold font for header
        ('FONTSIZE', (0, 0), (-1, 0), 10),  # Header font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('LEFTPADDING', (0, 0), (-1, 0), -70), 
    ]))

    # Create data rows
    data_rows = [[str(row.get(field, '')) for field in fields] for row in data]

    # Create data table with alternating row colors
    data_table = Table(data_rows, colWidths=column_widths)

    # Alternating row colors (light grey and white)
    alternating_row_styles = []
    for i, row in enumerate(data_rows):
        color = colors.white if i % 2 == 0 else colors.lightgrey
        alternating_row_styles.append(('BACKGROUND', (0, i), (-1, i), color))
    
    # Apply styles to data table
    data_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),  # Text color for rows
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font for rows
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # Font size for rows
        ('TOPPADDING', (0, 0), (-1, -1), 3),  # Padding for cells
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ] + alternating_row_styles))

    # Add the horizontal line between the header and data table
    line_drawing = Drawing(doc.width, 0.1 * inch)
    line_drawing.add(Line(0, 0, doc.width, 0, strokeColor=colors.black, strokeWidth=1))

    elements.append(header_table)
    elements.append(line_drawing)
   
    custom_text = f"THE VOLUME OF ELEMENTS FOR PROJECT NUMBER {p_no} Equals =======================> {total_vol}"
    elements.append(Paragraph(custom_text, custom_text_style))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(data_table)

    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
