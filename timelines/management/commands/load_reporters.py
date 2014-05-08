from django.core.management.base import BaseCommand
from django.conf import settings
from rapidsms.models import Backend, Connection, Contact
from timelines.models import Reporter
import phonenumbers
import xlrd
from rapidsms.router import send


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.order = {
            'name': 0,
            'phone': 1,
            'facility': 2,
            'village': 3
        }
        vhts = self.read_reporters(args[0])
        vhts = vhts[1:]
        for vht in vhts:
            phone = str(int(vht[self.order['phone']]))
            if (not phone.startswith('0')) and (not phone.startswith('256')):
                phone = '0%s' % phone
            phone = self.format_msisdn(phone)
            if not phone:
                continue

            conn, createad = Connection.objects.get_or_create(
                backend=Backend.objects.get(name=getattr(settings, 'DEFAUL_BACKEND', 'message_tester')),
                identity=phone
            )
            if not conn:
                continue
            contact = Contact.objects.filter(connection=conn)
            if contact:
                contact = contact[0]
            else:
                contact = Contact.objects.create()
                contact.connection_set.add(conn)
            contact.name = vht[self.order['name']]
            contact.save()

            # check Reporters
            r, created = Reporter.objects.get_or_create(contact=contact)
            if r:
                r.village = vht[self.order['village']]
                r.facility = vht[self.order['facility']]
                r.role = 'VHT'
                r.save()
                send(
                    'Hello %s, you have been successfully registered as a VHT '
                    'with Mother Reminder' % vht[self.order['name']],
                    conn
                )

    def read_reporters(self, filename):
        wb = xlrd.open_workbook(filename)
        l = []
        num_of_sheets = 1
        for i in xrange(num_of_sheets):
            sh = wb.sheet_by_index(i)
            for rownum in range(sh.nrows):
                vals = sh.row_values(rownum)
                l.append(vals)
        return l

    def format_msisdn(self, msisdn=None):
        """ given a msisdn, return in E164 format """
        assert msisdn is not None
        num = phonenumbers.parse(msisdn, getattr(settings, 'COUNTRY', 'UG'))
        is_valid = phonenumbers.is_valid_number(num)
        if not is_valid:
            return None
        return phonenumbers.format_number(
            num, phonenumbers.PhoneNumberFormat.E164).replace('+', '')
