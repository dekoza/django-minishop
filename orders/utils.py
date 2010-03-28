from products.models import Product
from django.http import HttpResponseRedirect

def log_change(request, object, message):
  """
  Insert log into django admin log
  """
  from django.contrib.admin.models import LogEntry
  from django.contrib.contenttypes.models import ContentType
  print 'msg',message
  print 'ob name',object.name
  LogEntry.objects.log_action(
      user_id = 1,
      content_type_id = ContentType.objects.get_for_model(object).pk,
      object_id       = object.pk,
      object_repr     = object.name,
      change_message     = message,
      action_flag = 2,
      )

def conditional_redirect(request, dest):
  """
  Redirects to given destination. If there is 'next' variable present in GET dictionary
  the function redirects to the address stored in 'next' variable.
  """
  redirect_to = request.REQUEST.get('next', False)
  if redirect_to:
    return HttpResponseRedirect(redirect_to)
  else:
    return HttpResponseRedirect(dest)

