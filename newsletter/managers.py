from django.contrib.sites.managers import CurrentSiteManager
from django.db.models import Manager


class NewsletterManager(Manager):
    use_for_related_fields = True

    def default(self):
        return self.get_queryset().first()

    def visible(self):
        return self.get_queryset().filter(visible=True)


class NewsletterCurrentSiteManager(NewsletterManager, CurrentSiteManager):
    pass


class SubscriptionManager(Manager):
    use_for_related_fields = True

    def active_subscriptions(self):
        return self.get_queryset().filter(subscribed=True)
