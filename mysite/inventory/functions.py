import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import lightskyblue, black

from django.http import HttpResponse
import csv, re

import datetime

from .models import Supplier, Item, Order

def create_pdf(order_number=None, supplier=None, orders=None):
    # Order Number and Supplier arguments are provided when function is used to attach PDF to email.
    # Orders argument is provided when function is used to download order history.
    # If function is used improperly, an exception is raised
    if order_number and supplier:
        orders = Order.objects.filter(order_number=order_number, item__supplier__name=supplier).exclude(order_qty=0)
        if not orders:
            return None
        order_date = datetime.datetime.now().strftime("%m/%d/%Y")
    elif orders:
        order_date = datetime.datetime.strftime(orders[0].date, "%m/%d/%Y")
    else:
        raise Exception('Improperly supplied arguments!' \
            ' Usage: use order_number and supplier together for email attachment; use orders alone for order history download')

    # Create Bytestream buffer
    buffer = io.BytesIO()
    b = True

    # Create a canvas
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    for index, order in enumerate(orders):
        if b is True:
            # Create a text object
            p.setFillColor(black)
            textob = p.beginText()
            textob.setTextOrigin(inch, inch)

            # Create Letterhead
            textob.setFont("Helvetica", 18)
            textob.textLine("Woodland Espresso")
            p.setLineWidth(0.05*inch)
            p.line(1*inch, 1.1*inch, 7.5*inch, 1.1*inch)

            # Display order date
            textob.setFont("Helvetica", 12)
            textob.textLine("Order Placed: " + order_date)
            textob.textLine()

            # Table Headers
            textob.setFont("Helvetica-Bold", 12)
            textob.textOut("Item")
            textob.moveCursor(5.5*inch, 0)
            textob.textOut("Order Qty")
            textob.moveCursor(-5.5*inch, 0)
            textob.textLine()
            b = False

        # Create blue striping on every other line
        if index % 2 == 0:
            p.setFillColor(lightskyblue, alpha=0.3)
            p.rect(textob.getX(), textob.getY() - 10.5, height=14.5, width=6.5*inch, fill=1, stroke=False)
        p.setFillColor(black)

        # Populate document with data from database
        textob.setFont("Courier", 12)
        if order.item.brand:
            item_string = str(order.item.brand + ' ' + order.item.unit)
        else:
            item_string = str(order.item.unit)
        textob.textOut(item_string)
        textob.moveCursor(5.5*inch, 0)
        textob.textOut(str(order.order_qty))
        textob.textOut(' ' + str(order.item.package))
        textob.moveCursor(-5.5*inch, 0)
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


def create_csv(order_number=None, supplier=None, all_models=False):

    # order_number kwarg determines the scope of the order data to return
    if order_number and supplier:
        orders = Order.objects.filter(order_number=order_number, item__supplier__name=supplier).exclude(order_qty=0)
        content_disposition = 'attachment; filename={date}_order_{number}.csv'.format(date=orders[0].date, number=order_number)
    elif order_number:
        orders = Order.objects.filter(order_number=order_number)
        content_disposition = 'attachment; filename={date}_order_{number}.csv'.format(date=orders[0].date, number=order_number)
    else:
        orders = Order.objects.all()
        content_disposition = 'attachment; filename=all_data.csv'

    # Prepare httpresponse object to write csv file
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': content_disposition}
    )

    # Prepare writer object
    writer = csv.writer(response)
    
    # Write data from Supplier and Item models if all_models is True
    if all_models:
        suppliers = Supplier.objects.all()
        items = Item.objects.all()

        writer.writerow(['SUPPLIERS'])
        writer.writerow(['Name', 'Email', 'Send Email', 'Phone'])
        for supplier in suppliers:
            writer.writerow([supplier.name, supplier.email, supplier.send_email, supplier.phone])
        
        writer.writerow([])
        writer.writerow(['ITEMS'])
        writer.writerow(['Supplier', 'Brand', 'Unit', 'Package', 'Package Qty', 'Quota', 'Storage', 'Latest Qty'])
        for item in items:
            writer.writerow([item.supplier, item.brand, item.unit, item.package, item.package_qty, item.quota, item.storage, item.latest_qty])

    # Write data from Order models
    writer.writerow([])
    writer.writerow(['ORDERS'])
    writer.writerow(['Brand', 'Unit', 'Date', 'Order Number', 'Qty'])
    for order in orders:
        writer.writerow([order.item.brand, order.item.unit, order.date, order.order_number, order.order_qty])

    return response


def read_csv(fileitem):

    fileitem.seek(0)
    fileitem = fileitem.read().decode('utf-8')
    rows = fileitem.split('\r\n')
    active_table = 0

    for row in rows:
        fields = row.split(',')
        if fields[0] == '':
            continue
        elif fields[0] == 'SUPPLIERS' or fields[0] == 'Name':
            active_table = 0
            continue
        elif fields[0] == 'ITEMS' or fields[0] == 'Supplier':
            active_table = 1
            continue
        elif fields[0]  == 'ORDERS' or fields[0] == 'Brand':
            active_table = 2
            continue
        
        if active_table == 0:
            new_supplier = Supplier(name=fields[0], email=fields[1], send_email=fields[2], phone=fields[3])
            new_supplier.save()
        elif active_table == 1:
            supplier = Supplier.objects.get(name=fields[0])
            new_item = Item(supplier=supplier, brand=fields[1], unit=fields[2], package=fields[3], \
                package_qty=fields[4], quota=fields[5], storage=fields[6], latest_qty=fields[7])     
            new_item.save()
        else:
            item = Item.objects.get(brand=fields[0], unit=fields[1])
            date = datetime.datetime.strptime(fields[2], "%Y-%m-%d")
            new_order = Order(item=item, date=datetime.date.strftime(date, "%Y-%m-%d"), order_number=fields[3], order_qty=fields[4])
            new_order.save()
            
    return None