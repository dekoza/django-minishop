# -*- coding: utf-8 -*-
from discounts.models import Voucher
from resellers.models import Partner
import re
from decimal import Decimal
from django.conf import settings

DEFAULT_PARTNER_DISCOUNT = getattr(settings, 'DEFAULT_PARTNER_DISCOUNT', Decimal("5.00"))
STATIC_CODES = getattr(settings, 'STATIC_CODES', {'default_static_fjkalej8r3r83jr': Decimal("5.00")})

class CodeValidator():
    #TODO: zmienić calculated_amount na without_shipping
    """
    Takes two init arguments: request object and a cart object.
    Checks for latest code or for code stored in session and checks 
    code validity. Recalculates discounts.
    """
    def __init__(self, request, cart):
        self.request = request
        self.cart = cart
        self.partner = None
        self.code = self._get_code()
        if self.code: # code is valid, let's do some magic
            self._remember_code()
            self.calculated_amount = self._calculate_items()
            self.total_calculated_amount = self._calculate_total()
        else:
            self.calculated_amount = 0
            self.total_calculated_amount = 0

    def _get_code(self):
        """Check POST data for code and test it validity, if it's not
        present or is invalid check session for code and do the same"""
        fresh = self.request.POST.get('code', False)
        if self._is_valid(fresh):
            return fresh
        else:
            old = self.request.session.get('voucher_code', False)
            if self._is_valid(old):
                return old
            else:
                return False

    def _is_static_code(self, code):
        if code.lower() in STATIC_CODES.keys():
            return True
        else:
            return False

    def _is_partner_code(self, code):
        """Simple regex to check for ab-0001 code format"""
        regex = re.compile(r'^\w{2}-\d{4}$')
        if not code:
            return False
        if regex.search(code):
            return True
        else:
            return False

    def _evaluate_static_code(self, code):
        try:
            self.amount = STATIC_CODES[code.lower()]
            return True
        except:
            return False

    def _evaluate_partner_code(self, code):
        """Check for existing partner and get the amount of discount"""
        try:
            partner = Partner.objects.get(code=code)
            # prevent from using your own partner code to discount your own
            # order
            if partner.user == request.user:
                return False
            self.partner = partner
            self.amount = DEFAULT_PARTNER_DISCOUNT
            return True
        except:
            return False

    def _evaluate_voucher_code(self, code):
        """Check for existing voucher and fetch it's discount"""
        try:
            voucher = Voucher.objects.get(code=code)
            self.amount = voucher.amount
            return True
        except:
            return False

    def _is_valid(self, code):
        """Choose code validation method and evaluate it"""
        if not code:
            return False

        if self._is_partner_code(code):
            return self._evaluate_partner_code(code)
        elif self._is_static_code(code):
            return self._evaluate_static_code(code)
        else:
            return self._evaluate_voucher_code(code)

    def _remember_code(self):
        """Store code and discount rate in sesssion"""
        self.request.session['voucher_code'] = self.code
        self.request.session['voucher'] = self.amount

    def _calculate_items(self):
        """Discount for items, without shipping"""
        price = self.cart.items_cost
        return float(price)/100*float(self.amount)

    def _calculate_total(self):
        """Discount for items and shipping"""
        price = self.cart.total_cost
        return float(price)-float(self.calculated_amount)

    def kill(self):
        """Remove code from session data. If code is a voucher, remove
        the voucher from database"""
        code = self.request.session.get('voucher_code', None)
        if self._is_partner_code(code):
            try:
                del self.request.session['voucher']
                del self.request.session['voucher_code']
            except:
                pass
        elif code:
            try:
                del self.request.session['voucher']
                del self.request.session['voucher_code']
                v = Voucher.objects.get(code=code)
                v.delete()
            except:
                pass
