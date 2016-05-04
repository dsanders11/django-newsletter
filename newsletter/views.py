from django.http import JsonResponse

from django.views.generic import (
    ListView, DetailView,
    ArchiveIndexView, DateDetailView,
    TemplateView, FormView
)

from .models import Newsletter, Subscription


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context



class SubscriptionView(ListView):
    # Logged in user - show all subscriptions for this account
    # Non-logged in user - show all subscriptions for this email
    # Anyone else, don't show anything

    template_name = "newsletter/subscription_list.html"
    model = Subscription

    def get_queryset(self):
        request = self.request

        return Subscription.objects.all()
