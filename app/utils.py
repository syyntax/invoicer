from flask import render_template
from weasyprint import HTML, CSS
from app.models import CompanySettings, Invoice
import os

def generate_pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    company_settings = CompanySettings.query.first()

    # Render HTML template for PDF. This template `invoice_template_for_pdf.html`
    # should be designed to be print-friendly.
    rendered_html = render_template(
        'invoices/invoice_template_for_pdf.html',
        invoice=invoice,
        company=company_settings
    )

    # Basic CSS for PDF styling. You can customize this or point to a CSS file.
    pdf_css = CSS(string='''
        @page { size: A4; margin: 1cm; }
        body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.5; color: #333; }
        h1, h2, h3, h4, h5, h6 { font-weight: bold; margin-top: 0; margin-bottom: 0.5em; }
        h1 { font-size: 20pt; }
        h2 { font-size: 16pt; }
        .container { max-width: 900px; margin: 0 auto; padding: 0; }
        .header, .footer { text-align: center; margin-bottom: 20px; }
        .invoice-details, .company-details, .recipient-details { margin-bottom: 20px; border: 1px solid #eee; padding: 10px; border-radius: 5px;}
        .table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .table th, .table td { border: 1px solid #eee; padding: 8px; text-align: left; vertical-align: top; }
        .table th { background-color: #f8f8f8; font-weight: bold; }
        .total-section { text-align: right; margin-top: 20px; }
        .total-section h4 { font-size: 14pt; margin: 5px 0; }
        .total-section .grand-total { font-size: 18pt; font-weight: bold; color: #007bff; }
        p { margin: 0 0 0.5em 0; }
        address { font-style: normal; }
    ''')

    pdf_bytes = HTML(string=rendered_html).write_pdf(stylesheets=[pdf_css])
    return pdf_bytes