# -*- coding: utf-8 -*-
import reportlab
import datetime
from cStringIO import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors, enums
from reportlab.lib.units import cm, mm
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.platypus import *

DEBUG = 0

SELLER = u"""
    Seller info here.
"""

class InvoicePageTemplate(PageTemplate):
    def __init__(self, id, pagesize=A4):
        self.pageWidth = pagesize[0]
        self.pageHeight = pagesize[1]
        frames = []
        frames.append(Frame(x1=0*mm, y1=285*mm, width=210*mm, height=12*mm, showBoundary=DEBUG))
        frames.append(Frame(x1=15*mm, y1=245*mm, width=100*mm, height=4*cm, showBoundary=DEBUG))
        frames.append(Frame(x1=15*mm, y1=205*mm, width=100*mm, height=4*cm, showBoundary=DEBUG))
        frames.append(Frame(x1=115*mm, y1=245*mm, width=8*cm, height=4*cm, showBoundary=DEBUG))
        frames.append(Frame(x1=115*mm, y1=205*mm, width=8*cm, height=4*cm, showBoundary=DEBUG))
        frames.append(Frame(x1=15*mm, y1=20*mm, width=180*mm, height=185*mm, showBoundary=DEBUG))
        PageTemplate.__init__(self, id, frames)

    def beforeDrawPage(self, canv, doc):
        canv.drawImage(settings.PROJECT_PATH+'/fvat_logo.jpg', 15*mm, 12*cm, 18*cm, 71*mm)

class Invoice():
    def __init__(self, order, rodzaj='original'):
        self.order = order
        r = {'original':u"Oryginał", 'copy':u"Kopia"}
        self.INVOICE_INFO = u"""Faktura VAT %(number)s %(rodzaj)s
        Data wystawienia: %(invoice_time)s, Kozy
        Data sprzedaży: %(order_created)s
        """ % {
                'rodzaj': r[rodzaj],
                'number': self.order.invoice_number,
                'invoice_time': self.order.created.strftime("%d-%m-%Y"),
                'order_created': self.order.created.strftime("%d-%m-%Y"),
                }

        pdfmetrics.registerFont(TTFont('Arial-Bold', settings.PROJECT_PATH+'/fonts/arialbd.ttf'))
        pdfmetrics.registerFont(TTFont('Arial', settings.PROJECT_PATH+'/fonts/arial.ttf'))
        from orders.pdf import styles
        self.styles = {
                'normal': styles.normal,
                'normal_bold':styles.bold,
                'head':styles.head,
                'bold_center':styles.bold_center,
                'right':styles.right,
                'center':styles.center,
                }

    def _get_address(self, type='billing'):
        """
        Render addresses on the invoice
        """
        elements = []
        if type == 'billing':
            address = self.order.user.get_profile().billing_address()
        else:
            address = self.order.user.get_profile().shipping_address()
        #elements.append(Spacer(width=2*cm, height=2*cm))
        for line in address.display_pdf.splitlines():
            elements.append(Paragraph(line, self.styles['normal_bold']))
        return elements

    def _get_items_table(self):
        data = []
        ts = [
            ('ALIGN', (1,1), (-1,-1), 'CENTER'),
            ('GRID',(0,0),(-1,-1), 0.5, colors.grey),
            ('VALIGN',(0,0),(-1,-1), 'MIDDLE'),
            #('SPAN',(0,-3),(3,-3)),
            #('SPAN',(0,-2),(3,-2)),
            #('SPAN',(0,-1),(3,-1)),
        ]
        head = [
            'Lp.',
            'Nazwa towaru',
            'Ilość',
            'Cena j. netto [zł]',
            'Wartość netto [zł]',
            'VAT [%]',
            'kwota VAT [zł]',
            'Wartość brutto [zł]'
        ]
        head_p = []
        for h in head:
            head_p.append(Paragraph(h, self.styles['bold_center']))
        data.append(head_p)
        for i, item in enumerate(self.order.ordereditem_set.all()):
            row = [
                Paragraph(str(i+1)+".", self.styles['normal']), 
                Paragraph(item.description.replace("&"," "), self.styles['normal']),
                Paragraph(str(item.quantity), self.styles['normal']),
                Paragraph("%.2f" % item.price_nett(), self.styles['normal']),
                Paragraph("%.2f" % item.price_total_nett(), self.styles['normal']),
                Paragraph('22', self.styles['normal']),
                Paragraph("%.2f" % item.price_tax(), self.styles['normal']),
                Paragraph("%.2f" % item.get_price_total(), self.styles['normal']),
            ]
            data.append(row)
        if self.order.shipping_price > 0:
            shipping = [
                Paragraph(str(self.order.ordereditem_set.count()+1), self.styles['normal']),
                Paragraph('Koszt dostawy', self.styles['normal']),
                Paragraph('1', self.styles['normal']),
                Paragraph("%.2f" % self.order.shipping_price_nett(), self.styles['normal']),
                Paragraph("%.2f" % self.order.shipping_price_nett(), self.styles['normal']),
                Paragraph('22', self.styles['normal']),
                Paragraph("%.2f" % self.order.shipping_price_tax(), self.styles['normal']),
                Paragraph("%.2f" % self.order.shipping_price, self.styles['normal']),
            ]
            data.append(shipping)
        return Table(data, colWidths=[1*cm, 7*cm, 1*cm, 2*cm, 2*cm, 1*cm, 2*cm, 2*cm], style=ts)

    def _table_footer(self):
        ts = [
            ('ALIGN', (1,1), (-1,-1), 'CENTER'),
            ('GRID',(4,0),(-1,-1), 0.5, colors.grey),
            ('LINEABOVE',(0,0),(-1,0), 0, colors.grey),
            ('VALIGN',(0,0),(-1,-1), 'MIDDLE'),
            #('SPAN',(0,0),(0,-1)),
            ('SPAN',(0,0),(3,0)),
            ('SPAN',(0,1),(3,1)),
        ]
        footer = [
            [
                Paragraph('Rabat:', self.styles['right']),
                '', '', '',
                Paragraph("%.2f" % self.order.discount_nett(), self.styles['normal']),
                Paragraph('22', self.styles['normal']),
                Paragraph("%.2f" % self.order.discount_tax(), self.styles['normal']),
                Paragraph("%.2f" % float(self.order.discount), self.styles['normal']),
            ],
            [
                Paragraph('Razem:', self.styles['right']),
                '', '', '',
                Paragraph("%.2f" % self.order.discounted_price_nett(), self.styles['normal']),
                Paragraph('22', self.styles['normal']),
                Paragraph("%.2f" % self.order.discounted_price_tax(), self.styles['normal']),
                Paragraph("%.2f" % self.order.discounted_price(), self.styles['normal']),
            ],
        ]
        return Table(footer, colWidths=[1*cm, 7*cm, 1*cm, 2*cm, 2*cm, 1*cm, 2*cm, 2*cm], style=ts)

    def _head(self):
        elements = []
        # sprzedawca
        elements.append(FrameBreak())
        elements.append(Paragraph("Sprzedawca:", self.styles['normal']))
        for line in SELLER.splitlines():
            p = Paragraph(line, self.styles['normal_bold'])
            elements.append(p)
        # adres billingowy
        elements.append(FrameBreak())
        elements.append(Paragraph("Nabywca:", self.styles['normal']))
        elements += self._get_address('billing')
        # dane fvat
        elements.append(FrameBreak())
        for line in self.INVOICE_INFO.splitlines():
            p = Paragraph('<para align="right">'+line+'</para>', self.styles['normal_bold'])
            elements.append(p)
        # adres shipping
        elements.append(FrameBreak())
        elements.append(Paragraph("Adresat:", self.styles['normal']))
        elements += self._get_address('shipping')
        elements.append(FrameBreak())
        elements.append(Paragraph(u"Zamówienie: "+self.order.name, self.styles['head']))
        return elements

    def _signatures(self):
        dots = "."
        for d in range(0,80):
            dots += "."

        ts = [
            ('ALIGN', (0,0),(-1,-1), 'CENTER'),
            #('GRID',(0,0),(-1,-1), 0, colors.grey),
        ]

        data = [
            [ Paragraph(dots, self.styles['center']),Paragraph(dots, self.styles['center'])],
            [ Paragraph(u"Osoba upoważniona do odbioru", self.styles['center']),Paragraph(u"Osoba upoważniona do wystawienia", self.styles['center'])],
        ]
        return Table(data, colWidths=[9*cm, 9*cm], style=ts)

    def pdf(self):
        buffer = StringIO()
        elements = []

        # page templates
        pagetemplates = []
        pagetemplates.append(InvoicePageTemplate(id='FirstPage'))
        document = BaseDocTemplate(buffer, pagesize=A4, pageTemplates=pagetemplates)
        # head
        elements += self._head()
        elements.append(self._get_items_table())
        elements.append(self._table_footer())
        #elements.append(Spacer(width=2*cm, height=5*mm))
        elements.append(Paragraph(u"Razem do zapłaty: "+str(self.order.discounted_price())+u" zł", self.styles['head']))
        #elements.append(Spacer(width=2*cm, height=10*mm))
        elements.append(self._signatures())
        document.build(elements)
        result = buffer.getvalue()
        buffer.close()
        return result
