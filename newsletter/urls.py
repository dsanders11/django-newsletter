from surlex.dj import surl

from django.conf.urls import url

from .views import (
#    subscriptions
)

urlpatterns = [
    # Newsletter list and detail view
#    surl('^$', NewsletterListView.as_view(), name='newsletter_list'),
#    surl(
#        '^<newsletter_slug:s>/$',
#        NewsletterDetailView.as_view(), name='newsletter_detail'
#    ),

    # List of all subscriptions for an email
#    url(
#        '^subscription/(?P<signature>\w*)$',
#        subscriptions,
#        name='subscriptions_list'
#    ),

    # Newsletter action views
#    surl(
#        '^<newsletter_slug:s>/<action=subscribe|update|unsubscribe>/$',
#        NewsletterActionView.as_view(),
#        name='newsletter_action'
#    ),
#
#    # Action email sent view
#    surl(
#        '^<newsletter_slug:s>/<action=subscribe|update|unsubscribe>/email-sent/$',
#        NewsletterActionView.as_view(
#            template_name='newsletter/subscription_%(action)s_email_sent.html'
#        ),
#        name='newsletter_action_email_sent'
#    ),
#
#    # Perform action views
#    surl(
#        '^subscription/<action=subscribe|update|unsubscribe>/<signature:s>$',
#        SubscriptionActionView.as_view(), name='newsletter_perform_action'
#    ),
#
#    # Action success view
#    surl(
#        '^subscription/<action=subscribe|update|unsubscribe>/success/<signature:s>$',
#        SubscriptionActionView.as_view(
#            template_name='newsletter/subscription_%(action)s_success.html'
#        ),
#        name='newsletter_action_success'),
]
