import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from django.http import HttpResponse, FileResponse
import csv, os, cgi, cgitb; cgitb.enable()

from datetime import datetime

from .models import Supplier, Item, Order

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


def createCSV(order_number=None, all_models=False):
    # Prepare httpresponse object to write csv file
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="history.csv"'}
    )

    # order_number kwarg determines the scope of the order data to return
    if order_number:
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
    writer.writerow(['Date', 'Order Number', 'Item', 'Qty'])
    for order in orders:
        writer.writerow([order.date, order.order_number, order.item, order.order_qty])

    return response


def readCSV():

    form = cgi.FieldStorage()
    fileitem = form['file']

    # Test if the file was opened
    if fileitem.filename:
        fn = os.path.basename(fileitem.filename.replace('\', '/''))
        open('/tmp/' + fn , 'wb').write(fileitem.file.read())
        message = 'The file "' + fn + '" was uploaded successfully'
    else:
        message = 'No file was uploaded'


    with open(fileitem, 'r') as file:
        csv = csv.reader(file)
        active_table = 0
        for row in csv:
            if row[0] == '':
                continue
            elif  row[0] == 'SUPPLIERS' or 'Name':
                active_table = 0
                continue
            elif row[0] == 'ITEMS' or 'Supplier':
                active_table = 1
                continue
            elif row[0] == 'ORDERS' or 'Date':
                active_table = 2
                continue
            
            if active_table == 0:
                Supplier.objects.create(name=row[0], email=row[1], send_email=row[2], phone=row[3])
            elif active_table == 1:
                Item.objects.create(supplier=row[0], brand=row[1], unit=row[2], package=row[3], package_qty=row[4], quota=row[5], storage=row[6], latest_qty=row[7])
            else:
                Order.objects.create(item=row[0], date=row[1], order_number=row[2], order_qty=row[3])
            
    return None