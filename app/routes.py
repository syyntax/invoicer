from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from app import db
from app.models import CompanySettings, Recipient, Invoice, LineItem
from app.forms import CompanySettingsForm, RecipientForm, InvoiceForm
from app.utils import generate_pdf
from datetime import datetime
import json

main = Blueprint('main', __name__)

# Middleware to ensure company settings are configured
@main.before_request
def check_company_settings():
    if not CompanySettings.query.first() and request.endpoint != 'main.settings':
        flash('Please set up your company details first.', 'warning')
        return redirect(url_for('main.settings'))

@main.route('/')
def index():
    company_settings = CompanySettings.query.first() # Still pass settings if base.html is used, or just for context
    return render_template('index.html', company=company_settings)

@main.route('/invoices')
def invoice_list():
    invoices = Invoice.query.order_by(Invoice.date_created.desc()).all()
    company_settings = CompanySettings.query.first()
    return render_template('invoices/list.html', invoices=invoices, company=company_settings)

@main.route('/invoices/new', methods=['GET', 'POST'])
@main.route('/invoices/<int:invoice_id>/edit', methods=['GET', 'POST'])
def create_edit_invoice(invoice_id=None):
    form = InvoiceForm()
    invoice = None
    if invoice_id:
        invoice = Invoice.query.get_or_404(invoice_id)
        if request.method == 'GET':
            form.recipient.data = invoice.recipient
            form.date_created.data = invoice.date_created
            form.date_due.data = invoice.date_due
            form.status.data = invoice.status

    if form.validate_on_submit():
        if not invoice:
            # Generate unique invoice number
            last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
            new_invoice_num_int = (int(last_invoice.invoice_number.split('-')[1]) + 1) if last_invoice and '-' in last_invoice.invoice_number else 1
            invoice_number = f"INV-{new_invoice_num_int:04d}" # INV-0001, INV-0002 etc.
            invoice = Invoice(invoice_number=invoice_number)

        invoice.recipient = form.recipient.data
        invoice.date_created = form.date_created.data
        invoice.date_due = form.date_due.data
        invoice.status = form.status.data

        # Handle line items from JavaScript POST payload
        line_items_data = json.loads(request.form.get('line_items_json', '[]'))
        invoice.line_items.clear() # Clear existing line items before re-adding for edit
        total_due = 0.0

        for item_data in line_items_data:
            quantity = float(item_data['quantity'])
            unit_price = float(item_data['unit_price'])
            item_total = quantity * unit_price
            line_item = LineItem(
                description=item_data['description'],
                quantity=quantity,
                unit_price=unit_price,
                total=item_total
            )
            invoice.line_items.append(line_item)
            total_due += item_total

        invoice.total_due = total_due

        if not invoice.id: # If new invoice, add to session
            db.session.add(invoice)
        db.session.commit()
        flash(f'Invoice {invoice.invoice_number} saved successfully!', 'success')
        return redirect(url_for('main.view_invoice', invoice_id=invoice.id))
    
    # Pre-populate line items for edit mode
    current_line_items = []
    if invoice:
        for li in invoice.line_items:
            current_line_items.append({
                'description': li.description,
                'quantity': li.quantity,
                'unit_price': li.unit_price,
                'total': li.total
            })
    
    company_settings = CompanySettings.query.first()
    return render_template(
        'invoices/create_edit.html',
        form=form,
        invoice=invoice,
        line_items_json=json.dumps(current_line_items), # Pass existing line items as JSON string
        company=company_settings
    )

@main.route('/invoices/<int:invoice_id>')
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    company_settings = CompanySettings.query.first()
    return render_template('invoices/view.html', invoice=invoice, company=company_settings)

@main.route('/invoices/<int:invoice_id>/delete', methods=['POST'])
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    db.session.delete(invoice)
    db.session.commit()
    flash(f'Invoice {invoice.invoice_number} deleted successfully!', 'success')
    return redirect(url_for('main.invoice_list'))

@main.route('/invoices/<int:invoice_id>/status', methods=['POST'])
def update_invoice_status(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    new_status = request.form.get('status')
    if new_status in ['PAID', 'OUTSTANDING']:
        invoice.status = new_status
        db.session.commit()
        flash(f'Invoice {invoice.invoice_number} status updated to {new_status}.', 'success')
    else:
        flash('Invalid status provided.', 'danger')
    return redirect(url_for('main.view_invoice', invoice_id=invoice.id))

@main.route('/invoices/<int:invoice_id>/export/html')
def export_invoice_html(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    company_settings = CompanySettings.query.first()
    rendered_html = render_template('invoices/invoice_template_for_pdf.html', invoice=invoice, company=company_settings)
    response = make_response(rendered_html)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = f'attachment; filename=invoice_{invoice.invoice_number}.html'
    return response

@main.route('/invoices/<int:invoice_id>/export/pdf')
def export_invoice_pdf(invoice_id):
    pdf_bytes = generate_pdf(invoice_id)
    invoice = Invoice.query.get_or_404(invoice_id)
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=invoice_{invoice.invoice_number}.pdf'
    return response

@main.route('/recipients')
def recipient_list():
    recipients = Recipient.query.order_by(Recipient.client_name).all()
    company_settings = CompanySettings.query.first()
    return render_template('recipients/list.html', recipients=recipients, company=company_settings)

@main.route('/recipients/new', methods=['GET', 'POST'])
@main.route('/recipients/<int:recipient_id>/edit', methods=['GET', 'POST'])
def create_edit_recipient(recipient_id=None):
    form = RecipientForm()
    recipient = None
    if recipient_id:
        recipient = Recipient.query.get_or_404(recipient_id)
        if request.method == 'GET':
            form.client_name.data = recipient.client_name
            form.address_line1.data = recipient.address_line1
            form.address_line2.data = recipient.address_line2
            form.city.data = recipient.city
            form.state.data = recipient.state
            form.zip_code.data = recipient.zip_code
            form.email.data = recipient.email
            form.phone.data = recipient.phone

    if form.validate_on_submit():
        if not recipient:
            recipient = Recipient()
        
        form.populate_obj(recipient)
        
        try:
            if not recipient.id:
                db.session.add(recipient)
            db.session.commit()
            flash(f'Recipient "{recipient.client_name}" saved successfully!', 'success')
            return redirect(url_for('main.recipient_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving recipient: {e}', 'danger')

    company_settings = CompanySettings.query.first()
    return render_template('recipients/create_edit.html', form=form, recipient=recipient, company=company_settings)

@main.route('/recipients/<int:recipient_id>/delete', methods=['POST'])
def delete_recipient(recipient_id):
    recipient = Recipient.query.get_or_404(recipient_id)
    if recipient.invoices:
        flash(f'Cannot delete recipient "{recipient.client_name}" because they have associated invoices.', 'danger')
        return redirect(url_for('main.recipient_list'))
    
    db.session.delete(recipient)
    db.session.commit()
    flash(f'Recipient "{recipient.client_name}" deleted successfully!', 'success')
    return redirect(url_for('main.recipient_list'))


@main.route('/settings', methods=['GET', 'POST'])
def settings():
    company_settings = CompanySettings.query.first()
    form = CompanySettingsForm(obj=company_settings) # Populate form with existing data

    if form.validate_on_submit():
        if not company_settings:
            company_settings = CompanySettings()
            db.session.add(company_settings)
        form.populate_obj(company_settings)
        db.session.commit()
        flash('Company settings updated successfully!', 'success')
        return redirect(url_for('main.settings'))

    return render_template('settings/company_settings.html', form=form, company=company_settings)