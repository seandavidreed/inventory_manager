import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from django.http import HttpResponse, FileResponse
import csv

from datetime import datetime

from .models import Order

def createPDF(order_number=None, supplier=None, orders=None):
    # Order Number and Supplier arguments are provided when function is used to attach PDF to email.
    # Orders argument is provided when function is used to download order history.
    # If function is used improperly, an exception is raised
    if order_number and supplier:
        orders = Order.objects.filter(order_number=order_number, item__supplier__name=supplier).exclude(order_qty=0)
        if not orders:
            return None
        order_date = datetime.now().strftime("%m/%d/%Y")
    elif orders:
        order_date = datetime.strftime(orders[0].date, "%m/%d/%Y")
    else:
        raise Exception('Improperly supplied arguments!' \
            ' Usage: use order_number and supplier together for email attachment; use orders alone for order history download')

    # Create Bytestream buffer
    buffer = io.BytesIO()
    b = True

    # Create a canvas
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    for order in orders:
        if b is True:
            # Create a text object
            textob = p.beginText()
            textob.setTextOrigin(inch, inch)

            # Create Letterhead
            textob.setFont("Courier", 18)
            textob.textLine("Woodland Espresso")
            p.setLineWidth(0.05*inch)
            p.line(1*inch, 1.1*inch, 7.5*inch, 1.1*inch)

            # Display order date
            textob.setFont("Courier", 12)
            textob.textLine("Order Placed: " + order_date)
            textob.textLine()

            # Table Headers (currently hard-coded: probably should change)
            textob.setFont("Courier-Bold", 12)
            textob.textOut("Item")
            textob.moveCursor(5*inch, 0)
            textob.textOut("Order Qty")
            textob.moveCursor(-5*inch, 0)
            textob.textLine()
            b = False

        # Populate document with data from database
        textob.setFont("Courier", 12)
        textob.textOut(str(order.item))
        textob.moveCursor(5*inch, 0)
        textob.textOut(str(order.order_qty))
        textob.textOut(' ' + str(order.item.package))
        textob.moveCursor(-5*inch, 0)
        textob.textLine()
        if textob.getCursor()[1] >= 712:
            b = True
            p.drawText(textob)
            p.showPage()

    # Render PDF document
    p.drawText(textob)
    p.showPage()
    p.save()

    buffer.seek(0)
    
    return buffer


def createCSV(order_number=None):
    # Prepare httpresponse object to write csv file
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="history.csv"'}
    )

    # kwarg determines scope of the function - how much order data to return
    if order_number:
        orders = Order.objects.filter(order_number=order_number)
    else:
        orders = Order.objects.all()

    # Write headers to csv
    writer = csv.writer(response)
    writer.writerow(['Date', 'Order Number', 'Item', 'Qty'])

    # Write each row of order data
    for order in orders:
        writer.writerow([order.date, order.order_number, order.item, order.order_qty])
    
    return response