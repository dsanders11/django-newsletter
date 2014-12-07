from django.db import models


class SubscriptionManager(models.Manager):
    def get_queryset(self):
        return super(SubscriptionManager, self).get_queryset().select_related()
