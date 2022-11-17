import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import datetime

from .models import Order

def createPDF(supplier=None, orders=None):
    # Supplier argument is provided when function is used to attach PDF to email.
    # Orders argument is provided when function is used to download order history.
    as_email = False
    if supplier is not None:
        as_email = True
        orders = Order.objects.filter(date=datetime.datetime.now(), item__supplier__name=supplier).exclude(order_qty=0)
        if not orders:
            return None
        order_date = str(datetime.datetime.now())
    else:
        order_date = str(orders[0].date)

    # Create Bytestream buffer
    buffer = io.BytesIO()
    b = True

    # Create a canvas
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    for thing in orders:
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
        textob.textOut(str(thing.item))
        textob.moveCursor(5*inch, 0)
        textob.textOut(str(thing.order_qty))
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
    if as_email is True:
        return buffer.getvalue()
    else:
        return buffer