import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import datetime

from .models import Order

def createOrder():
    # Fetch database objects by date
    things = Order.objects.filter(date=datetime.datetime.now(), item__supplier__name='Cash and Carry')

    # Create Bytestream buffer
    buffer = io.BytesIO()
    b = True

    # Create a canvas
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    for thing in things:
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
            textob.textLine("Order Placed: " + str(datetime.datetime.now()))
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
    pdf = buffer.getvalue()
    return pdf


def downloadHistory(orders, order_date):
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
    return buffer