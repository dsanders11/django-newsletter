import logging

from django.conf import settings

from django.contrib.sites.models import Site

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from django.db import models

from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from . import managers


logger = logging.getLogger(__name__)

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


@python_2_unicode_compatible
class Newsletter(models.Model):
    site = models.ManyToManyField(Site, default=Site.objects.all)

    title = models.CharField(_('newsletter title'), max_length=200)
    slug = models.SlugField(db_index=True, unique=True)
    email = models.EmailField(_('e-mail'), help_text=_('Sender e-mail'))
    sender = models.CharField(
        _('sender'), max_length=200, help_text=_('Sender name')
    )
    visible = models.BooleanField(
        _('visible'), default=True, db_index=True,
        help_text=_('Visible on site')
    )

    objects = managers.NewsletterManager()

    # Automatically filter the current site
    on_site = managers.NewsletterCurrentSiteManager()

    class Meta:
        verbose_name = _('newsletter')
        verbose_name_plural = _('newsletters')

    def get_absolute_url(self):
        return reverse(
            'newsletter_detail', args=[], kwargs={'newsletter_slug': self.slug}
        )

    def subscribe_url(self):
        return reverse(
            'newsletter_subscribe_request', args=[],
            kwargs={'newsletter_slug': self.slug}
        )

    def unsubscribe_url(self):
        return reverse(
            'newsletter_unsubscribe_request', args=[],
            kwargs={'newsletter_slug': self.slug}
        )

    def update_url(self):
        return reverse(
            'newsletter_update_request', args=[],
            kwargs={'newsletter_slug': self.slug}
        )

    def archive_url(self):
        return reverse(
            'newsletter_archive', args=[],
            kwargs={'newsletter_slug': self.slug}
        )

    @property
    def from_email(self):
        return u'%s <%s>' % (self.sender, self.email)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Subscription(models.Model):
    create_date = models.DateTimeField(editable=False, auto_now_add=True)
    subscribe_date = models.DateTimeField(_("subscribe date"), blank=True)
    unsubscribe_date = models.DateTimeField(
        _("unsubscribe date"), null=True, blank=True
    )

    newsletter = models.ForeignKey('Newsletter', editable=False, verbose_name=_('newsletter'))
    ip = models.GenericIPAddressField(_("IP address"), blank=True, null=True)
    user = models.ForeignKey(
        AUTH_USER_MODEL, blank=True, null=True, editable=False,
        verbose_name=_('user')
    )
    name_field = models.CharField(
        _('name'), db_column='name', max_length=30, blank=True,
        help_text=_('optional')
    )
    email = models.EmailField(_('e-mail'), db_index=True)
    subscribed = models.BooleanField(
        _('subscribed'), blank=True, db_index=True
    )

    objects = managers.SubscriptionManager()

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        unique_together = (
            ('user', 'newsletter'),
            ('email', 'newsletter')
        )
        index_together = (
            ('newsletter', 'email', 'subscribed')
        )

    def get_name(self):
        return self.user.get_full_name() if self.user else self.name_field

    def set_name(self, name):
        if not self.user:
            self.name_field = name
        else:
            raise ValueError("Can't set name for subscription with user")
    name = property(get_name, set_name)

    @property
    def to_email(self):
        if self.name:
            return u'%s <%s>' % (self.name, self.email)

        return u'%s' % (self.email)

    def subscribe_activate_url(self):
        return reverse('newsletter_update_activate', args=[], kwargs={
            'newsletter_slug': self.newsletter.slug,
            'email': self.email,
            'action': 'subscribe',
        })

    def unsubscribe_activate_url(self):
        return reverse('newsletter_update_activate', args=[], kwargs={
            'newsletter_slug': self.newsletter.slug,
            'email': self.email,
            'action': 'unsubscribe',
        })

    def update_activate_url(self):
        return reverse('newsletter_update_activate', args=[], kwargs={
            'newsletter_slug': self.newsletter.slug,
            'email': self.email,
            'action': 'update',
        })

    def subscribe(self, commit=True):
        assert self.subscribed == False

        self.subscribe_date = now()
        self.subscribed = True

        if commit:
            self.save()

    def unsubscribe(self, commit=True):
        assert self.subscribed == True

        self.unsubscribe_date = now()
        self.subscribed = False

        if commit:
            self.save()

    def clean(self):
        super(Subscription, self).clean()

        if self.subscribed and not self.subscribe_date:
            raise ValidationError({
                'subscribe_date': _("Must set a subscribe date if subscription is subscribed")
            })

        if not self.subscribed and not self.unsubscribe_date:
            raise ValidationError({
                'unsubscribe_date': _("Must set an unsubscribe date if subscription is not subscribed")
            })

    def __str__(self):
        if self.name:
            return _(u"%(name)s <%(email)s> to %(newsletter)s") % {
                'name': self.name,
                'email': self.email,
                'newsletter': self.newsletter
            }

        else:
            return _(u"%(email)s to %(newsletter)s") % {
                'email': self.email,
                'newsletter': self.newsletter
            }


@python_2_unicode_compatible
class SubscriptionAction(models.Model):
    ACTION_SUBSCRIBE = 0
    ACTION_UPDATE = 1
    ACTION_UNSUBSCRIBE = 2

    ACTIONS = (
        (ACTION_SUBSCRIBE, _("Subscribe")),
        (ACTION_UPDATE, _("Update")),
        (ACTION_UNSUBSCRIBE, _("Unsubscribe")),
    )

    time = models.DateTimeField(editable=False, auto_now=True)

    subscription = models.ForeignKey(Subscription, verbose_name=_('subscription'))
    action = models.IntegerField(_('action'), choices=ACTIONS)
    ip = models.GenericIPAddressField(_("IP address"), blank=True, null=True)
    name = models.CharField(
        _('name'), max_length=30, blank=True, help_text=_('optional')
    )
    email = models.EmailField(_('e-mail'))

    class Meta:
        verbose_name = _('subscription action')
        verbose_name_plural = _('subscription actions')

    def __str__(self):
        if action == self.ACTION_SUBSCRIBE:
            return _(u"Subscribe %(email)s to %(newsletter)s") % {
                'email': self.email,
                'newsletter': self.subscription.newsletter
            }
        elif action == self.ACTION_UPDATE:
            return _(u"Update subscription to %(newsletter)s") % {
                'newsletter': self.subscription.newsletter
            }
        elif action == self.ACTION_UNSUBSCRIBE:
            return _(u"Unsubscribe %(email)s from %(newsletter)s") % {
                'email': self.email,
                'newsletter': self.subscription.newsletter
            }
        else:
            return _(u"%(action)s for %(email)s on %(newsletter)s") % {
                'action': self.action,
                'email': self.email,
                'newsletter': self.subscription.newsletter
            }


@python_2_unicode_compatible
class Message(models.Model):
    newsletter = models.ForeignKey(
        'Newsletter', verbose_name=_('newsletter'),
        default=Newsletter.on_site.default
    )

    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'))

    date_create = models.DateTimeField(
        verbose_name=_('created'), auto_now_add=True, editable=False
    )
    date_modify = models.DateTimeField(
        verbose_name=_('modified'), auto_now=True, editable=False
    )

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        unique_together = ('slug', 'newsletter')

    @classmethod
    def get_default(cls):
        try:
            return cls.objects.order_by('-date_create').all()[0]
        except IndexError:
            return None

    def __str__(self):
        try:
            return _(u"%(title)s in %(newsletter)s") % {
                'title': self.title,
                'newsletter': self.newsletter
            }
        except Newsletter.DoesNotExist:
            logger.warning('No newsletter has been set for this message yet.')
            return self.title


@python_2_unicode_compatible
class Article(models.Model):
    message = models.ForeignKey(
        Message, verbose_name=_('message'), related_name='articles'
    )

    title = models.CharField(max_length=200, verbose_name=_('title'))
    text = models.TextField(verbose_name=_('text'))

    url = models.URLField(
        verbose_name=_('link'), blank=True, null=True
    )

    class Meta:
        verbose_name = _('article')
        verbose_name_plural = _('articles')
        order_with_respect_to = 'message'

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Submission(models.Model):
    STATE_FAILED = 0
    STATE_PREPARED = 1
    STATE_SENDING = 2
    STATE_SENT = 3

    STATES = (
        (STATE_FAILED, _('failed')),
        (STATE_PREPARED, _('prepared')),
        (STATE_SENDING, _('sending')),
        (STATE_SENT, _('sent')),
    )

    newsletter = models.ForeignKey(
        Newsletter, verbose_name=_('newsletter'), editable=False
    )
    message = models.ForeignKey(
        Message, verbose_name=_('message'), editable=True
    )

    subscriptions = models.ManyToManyField(
        Subscription,
        help_text=_('If you select none, the system will automatically find '
                    'the subscribers for you.'),
        blank=True, db_index=True, verbose_name=_('recipients'),
        limit_choices_to={'subscribed': True}
    )

    publish_date = models.DateTimeField(
        _('publication date'), blank=True, null=True,
        default=now, db_index=True
    )
    publish = models.BooleanField(
        _('publish'), default=True, help_text=_('Publish in archive.'),
        db_index=True
    )

    state = models.IntegerField(
        _('state'), default=STATE_PREPARED, choices=STATES
    )

    class Meta:
        verbose_name = _('submission')
        verbose_name_plural = _('submissions')

    def get_absolute_url(self):
        assert self.newsletter.slug
        assert self.message.slug

        return reverse(
            'newsletter_archive_detail', args=[], kwargs={
                'newsletter_slug': self.newsletter.slug,
                'year': self.publish_date.year,
                'month': self.publish_date.month,
                'day': self.publish_date.day,
                'slug': self.message.slug
            }
        )

    def clean(self):
        super(Submission, self).clean()

        self.newsletter = self.message.newsletter

    def __str__(self):
        return _(u"%(newsletter)s on %(publish_date)s") % {
            'newsletter': self.message,
            'publish_date': self.publish_date
        }


@python_2_unicode_compatible
class SubmissionRecipient(models.Model):
    STATE_FAILED = 0
    STATE_QUEUED = 1
    STATE_WILL_RETRY= 2
    STATE_SENT = 3

    STATES = (
        (STATE_FAILED, _('failed')),
        (STATE_QUEUED, _('queued')),
        (STATE_WILL_RETRY, _('will retry')),
        (STATE_SENT, _('sent')),
    )

    submission = models.ForeignKey(
        Submission, verbose_name=_('submission'), related_name='recipients'
    )
    user = models.ForeignKey(
        AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
        verbose_name=_('user')
    )
    name = models.CharField(_('name'), max_length=30, blank=True)
    email = models.EmailField(_('e-mail'))
    state = models.IntegerField(
        _('state'), default=STATE_QUEUED, choices=STATES
    )
    retry_count = models.PositiveSmallIntegerField(_('retries'))

    class Meta:
        verbose_name = _('submission recipient')
        verbose_name_plural = _('submission recipients')

    def __str__(self):
        return _(u"%(newsletter)s on %(publish_date)s") % {
            'newsletter': self.message,
            'publish_date': self.publish_date
        }
