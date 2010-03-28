# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
import time, datetime, calendar
import simplejson as json

from chartstats.forms import DefaultDateForm

#TODO
# * rename to BaseChart and move to chart_base.py
# * create middle subclasses for various chart types and various forms
# * create exceptions raised in case of trying to use the base class directly
# * create unittests
# * create a report registry view, that contains a list of reports

class DateChartView(object):
  form = DefaultDateForm
  template = 'chartstats/chart.html'
  name = 'Date based report'
  yaxis = 'Products'
  xaxis = 'Time'
  table = 'products_product'
  date_field = 'created'
  colors = ['#659dc2',  '#dba255']
  labels = ['Products']

  def __call__(self, request, *args, **kwargs):
    """
    Has to be callable to be able to be invoked right within urls.py
    """
    if request.method == 'GET':
      form = self.form()
      report_data = "" 
      sql = ""
    else:
      form = self.form(request.POST)
      if form.is_valid():
        params = { 
            'date_field': self.date_field,
            'table': self.table,
            }
        # dynamically append all form field data do params
        for key in form.cleaned_data.keys():
          params[key] = form.cleaned_data[key]
        report_data = self.fetch_data(params)
        flot_settings = self.flot_settings(params)
        # debug
        sql = self.construct_query(params)
    flot_settings =''
    #TODO
    context = { 
        'form':form, 
        'data':report_data,
        'flot':json.dumps(flot_settings),
        'title':self.name,
        'yaxis':self.yaxis,
        'colors':self.colors,
        'sql':sql }
    return render_to_response(self.template, context, context_instance=RequestContext(request))

  def construct_query(self, params):
    """
    Method for creating sql query must return a LIST of strings
    """
    # łorning - to zapytanie bangla tylko na postgreSQL :>
    q = """
    SELECT COUNT(*), date_trunc('day', %(date_field)s) AS date 
    FROM %(table)s 
    WHERE %(date_field)s >= '%(start_date)s' AND %(date_field)s <= '%(end_date)s' 
    GROUP BY date_trunc('day', %(date_field)s) 
    ORDER BY date ASC;
    """ % params
    return [q]

  def fetch_data(self, params):
    """
    Method that uses given query to fetch and format data. Returns a LIST of 
    valid flot arrays.
    """
    from django.db import connection
    cursor = connection.cursor()
    data_list = []
    queries = self.construct_query(params)
    for query in queries:
      cursor.execute(query)
      data = cursor.fetchall()
      for i,d in enumerate(data):
        data[i] = [d[0], calendar.timegm(d[1].timetuple())*1000] 
      data_list.append(",".join("["+str(dt[1])+","+str(dt[0])+"]" for dt in data))
    return data_list

  def flot_settings(self, params):
    """
    Method for creating flot settings object.
    """
    flot_settings_dict = {
        'xaxis': '{mode: \'time\', timeformat: \"%d %b\" }',
        'yaxis': '{autoscaleMargin: 0.4, min: 0 }',
        'selection': '{ mode: "xy" }',
        'grid':'{labelMargin: 8,hoverable: true, clickable: true, color: "#bbb", borderWidth: 0.5}',
        'colors': "[\""+self.colors[0]+"\", \""+self.colors[1]+"\"]",
        'legend': '{position: "ne", margin: 2, noColumns: 2, backgroundOpacity: 0.3 }',
        }
    return flot_settings_dict

  #TODO
  def data_settings(self, params):
    """
    Method for creating settings for each plot on the chart.
    """
    data_settings_dict = {
        'label': 'none',
        }
    return data_settings_dict

class SalesByDate(DateChartView):
  name = _("Daily income for given date range")
  yaxis = _("Sales (EUR)")
  def construct_query(self,params):
    # łorning - to zapytanie bangla tylko na postgreSQL :>
    q = """
    SELECT sum(ord.price), ord.created::date
    FROM orders_order ord 
    WHERE ord.created::date >= '%(start_date)s' AND ord.created::date <= '%(end_date)s' 
    GROUP BY ord.created::date
    ORDER BY ord.created::date ASC;
    """ % params
    print q
    return [q]
