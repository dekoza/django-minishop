from django.conf.urls.defaults import *

urlpatterns = patterns('customers.views',
    url(r'^zarejestruj-sie/$', 'register', name="register"),
    url(r'^activate/(?P<activation_key>\w+)/$', 'activate', name='registration_activate'),
    url(r'^profil/$', 'profile', name="profile"),
    url(r'^profil/edytuj/$', 'profile_edit', name="profile_edit"),
    url(r'^profil/haslo/$', 'password_change', name="profile_password"),
    url(r'^profil/adres/$', 'address_list', name="profile_address"),
    url(r'^profil/adres/(?P<address_id>\d+)/$', 'address_edit', name="profile_address_edit"),
    url(r'^profil/adres/(?P<address_id>\d+)/delete/$', 'address_delete', name="profile_address_delete"),
    url(r'^profil/adres/dodaj/$', 'address_add', name="profile_address_add"),
    url(r'^profil/historia$', 'profile_history', name="profile_history"),
    url(r'^favorites/$', 'favorites', name="favorites"),
    url(r'^zaloguj/$', 'login_user', name="login"),
    url(r'^wyloguj/$', 'logout_user', name="logout"),
    )

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^password_reset/$', 'password_reset', {'template_name':'customers/password_reset.html', 'email_template_name':'customers/password_reset_email.html'}, name="password_reset"),
    url(r'^password_reset/done/$', 'password_reset_done', {'template_name':'customers/password_reset_done.html'}, name="password_reset_done"),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm', {'template_name':'customers/password_reset_confirm.html'}, name="password_reset_confirm"),
    url(r'^reset/done/$', 'password_reset_complete', {'template_name':'customers/password_reset_complete.html'}, name="password_reset_done"),
)
