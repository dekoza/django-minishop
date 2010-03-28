from xml.dom.minidom import Document
from products.models import *
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils.html import strip_tags
from django.conf import settings
import datetime
# Create your views here.

DOMAIN = getattr(settings, "SITE_DOMAIN", "http://biolander.com")

def xml_kangoo(request):
    today = datetime.date.today().strftime("%Y-%m-%d")
    doc = Document()
    products = doc.createElement("products")
    products.setAttribute("xmlns", "http://www.sklepy24.pl")
    products.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    products.setAttribute("xsi:schemaLocation", "http://www.w3.org/2001/XMLSchema-instance")
    products.setAttribute("date", today)
    doc.appendChild(products)

    shop_products = Product.published.all()

    for pr in shop_products:
        product = doc.createElement("product")
        product.setAttribute("id", pr.slug)
        products.appendChild(product)
        # elementy produktu
        name_elem = doc.createElement("name")
        product.appendChild(name_elem)
        name = doc.createTextNode(escape(pr.name))
        name_elem.appendChild(name)

        url_elem = doc.createElement("url")
        product.appendChild(url_elem)
        url = doc.createTextNode(DOMAIN+reverse("product_page", kwargs={"slug":pr.slug}))
        url_elem.appendChild(url)

        brand_elem = doc.createElement("brand")
        product.appendChild(brand_elem)
        brand = doc.createTextNode(escape(pr.manufacturer.name))
        brand_elem.appendChild(brand)

        categories_elem = doc.createElement("categories")
        product.appendChild(categories_elem)
        for cat in pr.categories.all():
            category_elem = doc.createElement("category")
            categories_elem.appendChild(category_elem)
            category = doc.createTextNode(escape(cat.name))
            category_elem.appendChild(category)

        pr_photos = pr.photos_set.all()
        if len(pr_photos):
            photo_elem = doc.createElement("photo")
            product.appendChild(photo_elem)
            photo = doc.createTextNode(escape(DOMAIN+pr.photos_set.all()[0].image.url).encode('ascii', 'xmlcharrefreplace'))
            photo_elem.appendChild(photo)

        description_elem = doc.createElement("description")
        product.appendChild(description_elem)
        description = doc.createTextNode(escape(strip_tags(pr.description)))
        description_elem.appendChild(description)

        price_elem = doc.createElement("price")
        product.appendChild(price_elem)
        price = doc.createTextNode(str(pr.price).replace(".", ",").rstrip("0").rstrip(",").strip())
        price_elem.appendChild(price)

    return HttpResponse(doc.toxml(), mimetype="text/xml")

def xml_okazje(request):
    today = datetime.date.today().strftime("%Y-%m-%d")
    doc = Document()
    okazje = doc.createElement("okazje")
    doc.appendChild(okazje)
    offers = doc.createElement("offers")
    okazje.appendChild(offers)

    shop_products = Product.published.all()

    for pr in shop_products:
        offer = doc.createElement("offer")
        offers.appendChild(offer)
        # elementy produktu
        id_elem = doc.createElement("id")
        offer.appendChild(id_elem)
        id = doc.createTextNode(pr.slug)
        id_elem.appendChild(id)

        name_elem = doc.createElement("name")
        offer.appendChild(name_elem)
        name = doc.createTextNode(escape(pr.name))
        name_elem.appendChild(name)

        url_elem = doc.createElement("url")
        offer.appendChild(url_elem)
        url = doc.createTextNode(DOMAIN+reverse("product_page", kwargs={"slug":pr.slug}))
        url_elem.appendChild(url)

        brand_elem = doc.createElement("producer")
        offer.appendChild(brand_elem)
        brand = doc.createTextNode(escape(pr.manufacturer.name))
        brand_elem.appendChild(brand)

        category_elem = doc.createElement("category")
        offer.appendChild(category_elem)
        path = pr.categories.all()[0].get_ancestors()[1:]
        path_txt = "/".join([ p.name for p in path])
        path_txt += "/"+pr.categories.all()[0].name
        category = doc.createTextNode(escape(path_txt))
        category_elem.appendChild(category)

        photo_elem = doc.createElement("image")
        offer.appendChild(photo_elem)
        pr_photos = pr.photos_set.all()
        if len(pr_photos):
            photo = doc.createTextNode(escape(DOMAIN+pr_photos[0].image.url).encode('ascii', 'xmlcharrefreplace'))
            photo_elem.appendChild(photo)

        description_elem = doc.createElement("description")
        offer.appendChild(description_elem)
        description = doc.createTextNode(escape(strip_tags(pr.description)))
        description_elem.appendChild(description)

        price_elem = doc.createElement("price")
        offer.appendChild(price_elem)
        price = doc.createTextNode(str(pr.price).replace(".", ",").rstrip("0").rstrip(",").strip())
        price_elem.appendChild(price)

    return HttpResponse(doc.toxml(), mimetype="text/xml")
