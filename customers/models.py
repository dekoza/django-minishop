from django.db import models
from django.db.models import Q
from django.contrib.comments.models import Comment
import datetime
import random
import re
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

class LastAddress(Exception):
    pass

# Create your models here.

CUSTOMER_TYPES = (
        ('1', _('Private')),
        ('2', _('Corporate')),
)

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class CustomerManager(models.Manager):
    # most manager stuff taken from django.registration by ubernostrum

    def activate_user(self, activation_key):
        from customers.signals import user_activated
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = self.model.ACTIVATED
                profile.save()
                user_activated.send(sender=self.model, user=user)
                return user
        return False

    def create_inactive_user(self, username, password, email, first_name, last_name, send_email=True):
        from customers.signals import user_registered

        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()

        registration_profile = self.create_profile(new_user)

        if send_email:
            from django.core.mail import send_mail
            current_site = Site.objects.get_current()

            #subject = render_to_string('customers/activation_email_subject.txt', { 'site': current_site })
            subject = _("Account activation at biolander.com")
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())

            message = render_to_string('customers/activation_email.txt',
                                                                 { 'activation_key': registration_profile.activation_key,
                                                                     'user': new_user,
                                                         #            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                                                    # 'site': current_site
                                                                     })

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [new_user.email])
        user_registered.send(sender=self.model, user=new_user)
        return new_user
    create_inactive_user = transaction.commit_on_success(create_inactive_user)

    def create_profile(self, user):
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        activation_key = sha_constructor(salt+user.username).hexdigest()
        return self.create(user=user, activation_key=activation_key)

    def delete_expired_users(self):
        for profile in self.all():
            if profile.activation_key_expired():
                user = profile.user
                if not user.is_active:
                    user.delete()



class Customer(models.Model):
    ACTIVATED = u"ALREADY_ACTIVATED"
    #TODO: remove company name and customer type
    type = models.PositiveIntegerField(choices=CUSTOMER_TYPES, default=1, verbose_name=_("type"), null=True, blank=True)
    company_name = models.CharField(max_length=200, null=True, blank=True, verbose_name=_("company name"))
    birthdate = models.DateField(null=True, blank=True, verbose_name=_("birth date"))
    user = models.ForeignKey(User, unique=True, verbose_name=_("user"))
    activation_key = models.CharField(max_length=40, editable=False)
    objects = CustomerManager()
    newsletter = models.BooleanField(default=False, verbose_name=_("newsletter"))

    def get_type(self):
        if self.type:
            return CUSTOMER_TYPES[int(self.type)-1][1]

    def activation_key_expired(self):
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
                                                             (self.user.date_joined + expiration_date <= datetime.datetime.now())
    activation_key_expired.boolean = True

    def __unicode__(self):
        if self.user:
            return self.user.first_name+" "+self.user.last_name
        else:
            return 'Customer with incomplete data'

    def delete(self):
        self.user.delete()

    def joined(self):
        if self.user:
            return self.user.date_joined.strftime("%d-%m-%Y")
    joined.admin_order_field = 'user__date_joined'

    def first_name(self):
        if self.user:
            return self.user.first_name
    first_name.admin_order_field = 'user__first_name'

    def last_name(self):
        if self.user:
            return self.user.last_name
    last_name.admin_order_field = 'user__last_name'

    def email(self):
        if self.user:
            return self.user.email
    email.admin_order_field = 'user__email'

    def active(self):
        if self.user:
            return self.user.is_active
    active.boolean = True

    def shipping_address(self):
        try:
            return self.address_set.get(is_shipping=True, deleted=False)
        except Customer.MultipleObjectsReturned:
            return self.address_set.filter(is_shipping=True, deleted=False)[0]
        except:
            return self.billing_address()

    def is_partner(self):
        from resellers.models import Partner
        if Partner.objects.filter(user=self.user).count():
            return True
        else:
            return False

    def is_active_partner(self):
        from resellers.models import Partner
        try:
            partner = Partner.objects.get(user=self.user)
        except:
            return False
        if partner.is_active:
            return True
        else:
            return False

    def billing_address(self):
        try:
            return self.address_set.get(is_billing=True, deleted=False)
        except Customer.MultipleObjectsReturned:
            return self.address_set.filter(is_billing=True, deleted=False)[0]
        except:
            if len(self.address_set.filter(is_shipping=True, deleted=False)):
                return self.shipping_address()
            else:
                return None


class AddressManager(models.Manager):
    def get_query_set(self):
        return super(AddressManager, self).get_query_set().filter(deleted=False)

class Address(models.Model):
    customer = models.ForeignKey(Customer, verbose_name=_("customer"))
    first_name = models.CharField(max_length=200, verbose_name=_("first name"), blank=True, null=True)
    last_name = models.CharField(max_length=200, verbose_name=_("last name"), blank=True, null=True)
    company_name = models.CharField(max_length=200, verbose_name=_("company name"), blank=True, null=True)
    nip = models.CharField(max_length=13, null=True, blank=True, verbose_name=_("nip"))
    city = models.CharField(max_length=200, verbose_name=_("city"))
    street = models.CharField(max_length=200, verbose_name=_("street"))
    house_number = models.CharField(max_length=200, verbose_name=_("house/flat number"))
    postal_code = models.CharField(max_length=200, verbose_name=_("postal code"))
    phone_number = models.CharField(max_length=200, verbose_name=_("phone number"))
    # address type
    is_corporate = models.BooleanField(default=False, verbose_name=_("address type"))
    # main billing address?
    is_billing = models.BooleanField(default=False, verbose_name=_("is main billing address"))
    # main shipping address?
    is_shipping = models.BooleanField(default=False, verbose_name=_("is main shipping address"))
    deleted = models.BooleanField(default=False, verbose_name=_("the adress has beed deleted by the customer"), editable=False)

    @property
    def display(self):
        if self.is_corporate:
            result = """ %(company_name)s <br />
            NIP: %(nip)s <br />
            %(postal_code)s, %(city)s <br />
            %(street)s %(house_number)s
            """ % self.__dict__
        else:
            if not self.first_name and not self.last_name:
                self.first_name = self.customer.user.first_name
                self.last_name = self.customer.user.last_name
            result = """ %(first_name)s %(last_name)s <br />
            %(postal_code)s, %(city)s <br />
            %(street)s %(house_number)s
            """ % self.__dict__
        return result

    @property
    def display_pdf(self):
        if self.is_corporate:
            result = """ %(company_name)s 
            NIP: %(nip)s 
            %(postal_code)s, %(city)s 
            %(street)s %(house_number)s
            """ % self.__dict__
        else:
            if not self.first_name and not self.last_name:
                self.first_name = self.customer.user.first_name
                self.last_name = self.customer.user.last_name
            result = """ %(first_name)s %(last_name)s 
            %(postal_code)s, %(city)s 
            %(street)s %(house_number)s
            """ % self.__dict__
        return result

    objects = models.Manager()
    published = AddressManager()

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')
        ordering = ('-is_billing','-is_shipping','city')

    def __unicode__(self):
        return self.city+", "+self.street+" "+self.house_number

    def save(self, clean=False):
        if not clean:
            billing_addresses = self.customer.address_set.filter(is_billing=True, deleted=False)
            if self.is_billing and len(billing_addresses) > 0:
                billing_addresses.update(is_billing=False)
            shipping_addresses = self.customer.address_set.filter(is_shipping=True, deleted=False)
            if self.is_shipping and len(shipping_addresses) > 0:
                shipping_addresses.update(is_shipping=False)
        else:
            self.is_shipping = False
            self.is_billing = False
        if self.is_corporate:
            self.first_name = ""
            self.last_name = ""
        else:
            self.nip = ""
            self.company_name = ""
        super(Address, self).save()

    def delete(self, force=False):
        if not force:
            other_addresses = self.customer.address_set.exclude(Q(pk=self.pk) | Q(deleted=True))
            if len(other_addresses) > 0 and self.is_shipping:
                try:
                    billing_address = self.customer.address_set.exclude(pk=self.pk).get(is_billing=True, deleted=False)
                except:
                    billing_address = other_addresses[0]
                billing_address.is_shipping = True
                billing_address.save()
            if len(other_addresses) > 0 and self.is_billing:
                try:
                    shipping_address = self.customer.address_set.exclude(pk=self.pk).get(is_shipping=True, deleted=False)
                except:
                    shipping_address = other_addresses[0]
                shipping_address.is_billing = True
                shipping_address.save()
            if len(other_addresses) == 0:
                raise LastAddress
            self.deleted = True
            self.save(clean=True)

def notify_about_comment(sender, **kwargs):
    comment = kwargs['comment']
    subject = _("Nowy komentarz do produktu %s" % comment.content_object.name)
    subject = ''.join(subject.splitlines())
    message = render_to_string('email/new_comment.html', {'comment':comment,})
    from django.core.mail import send_mail
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
              settings.SHOP_STAFF_EMAILS)

from django.contrib.comments.signals import comment_was_posted

# cholera wie czemu wysyla sygnaly po dwa razy, ponizej chamowate
# obejscie, za pomoca argumentu dispatch_uid, wiecej info tu:
# http://www.mail-archive.com/django-users@googlegroups.com/msg71068.html
comment_was_posted.connect(notify_about_comment, Comment,
                           dispatch_uid='comment.post_comment')
