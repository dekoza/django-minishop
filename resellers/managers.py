# -*- coding: utf-8 -*-
from django.db import models
from decimal import Decimal
import datetime, calendar

class HistoryManager(models.Manager):
    def income_daily(self, start=datetime.date.today()+datetime.timedelta(weeks=-1),
                     end=datetime.date.today(), partner=None):
        """
        Calculate daily reseller income and return set of
        lists: [js timestamp, daily income] - suitable for js charts
        """
        start_s = start.strftime("%Y-%m-%d")
        end_s = end.strftime("%Y-%m-%d")
        oneday = datetime.timedelta(days=1)
        day = start
        from django.db import connection
        cursor = connection.cursor()
        sql = """
        SELECT rh.created::date, sum(rh.income)
        FROM resellers_partnerhistory rh
        WHERE rh.created::date >= '%s' AND rh.created::date <= '%s'
        AND rh.partner_id = %d
        GROUP BY rh.created::date
        ORDER BY rh.created::date ASC
        """ % (start_s, end_s, partner.pk)
        cursor.execute(sql)
        query_result = cursor.fetchall()
        result = []
        while day < end:
            if query_result and query_result[0][0] == day:
                # cool new way to make this faster - use results as stack!
                q_day_data = query_result.pop(0)
            else:
                q_day_data = []
            if len(q_day_data) > 0:
                result.append([int(self._make_js_timestamp(day)), float(q_day_data[0])])
            else:
                result.append([int(self._make_js_timestamp(day)), 0.0])
            day += oneday
        return result

    def total_income(self, partner):
        from django.db import connection
        cursor = connection.cursor()
        sql = """
        SELECT sum(rh.income)
        FROM resellers_partnerhistory rh
        WHERE rh.partner_id = %d
        """ % partner.pk
        result = cursor.execute(sql)
        if not result:
            result = 0
        else:
            result = result[0]
        return result

    def unpaid_income(self, partner):
        from django.db import connection
        cursor = connection.cursor()
        if not partner.last_paid: # never payed, display total income instead
            return self.total_income(partner)
        last_paid = partner.last_paid.strftime("%Y-%m-%d")
        #TODO: sprawdzić czy przy dacie nie ma być >=
        sql = """
        SELECT sum(rh.income)
        FROM resellers_partnerhistory rh
        WHERE rh.partner_id = %d AND rh.created::date > '%s'
        """ % (partner.pk, last_paid)
        result = cursor.execute(sql)
        if not result:
            result = 0
        else:
            result = result[0]
        return result

    def earned_today(self, partner):

        from django.db import connection
        cursor = connection.cursor()
        today = datetime.date.today().strftime("%Y-%m-%d")
        #TODO: sprawdzić czy przy dacie nie ma być >=
        sql = """
        SELECT sum(rh.income)
        FROM resellers_partnerhistory rh
        WHERE rh.partner_id = %d AND rh.created::date = '%s'
        """ % (partner.pk, today)
        result = cursor.execute(sql)
        if not result:
            result = 0
        else:
            result = result[0]
        return result

    def _make_js_timestamp(self, dt_object):
        return calendar.timegm(dt_object.timetuple())*1000
