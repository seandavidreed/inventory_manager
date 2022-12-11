import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from django.http import HttpResponse, FileResponse
import csv, re

import datetime

from .models import Supplier, Item, Order

def createPDF(order_number=None, supplier=None, orders=None):
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
        textob.textOut(str(order.item.brand + ' ' + order.item.unit))
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


def createCSV(order_number=None, supplier=None, all_models=False):
    # Prepare httpresponse object to write csv file
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="history.csv"'}
    )

    # order_number kwarg determines the scope of the order data to return
    if order_number and supplier:
        orders = Order.objects.filter(order_number=order_number, item__supplier__name=supplier).exclude(order_qty=0)
    elif order_number:
        orders = Order.objects.filter(order_number=order_number)
    else:
        orders = Order.objects.all()

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


def readCSV(fileitem):

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
            new_item = Item(supplier=new_supplier)
            new_supplier.save()
            new_item.save()
        elif active_table == 1:
            item = Item.objects.get(supplier__name=fields[0])
            item.brand = fields[1]
            item.unit = fields[2]
            item.package = fields[3]
            item.package_qty = fields[4]
            item.quota = fields[5]
            item.storage = fields[6]
            item.latest_qty = fields[7]
            new_order = Order(item=item, date=datetime.datetime.now())
            item.save()
            new_order.save()
        else:
            print(fields[2])
            order = Order.objects.get(item__id=item.id)
            date = datetime.datetime.strptime(fields[2], "%Y-%m-%d")
            order.date = datetime.date.strftime(date, "%Y-%m-%d")
            order.order_number = fields[3]
            order.order_qty = fields[4]
            order.save()
            
    return None