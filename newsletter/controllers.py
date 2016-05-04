from django.utils.decorators import classonlymethod


class SubmissionController(object):
    @classonlymethod
    def get_extra_headers(cls, submission):
        pass

    @classonlymethod
    def get_unsubscribe_link(cls, submission):
        pass

    @classonlymethod
    def submit(cls, submission):
        pass


class SubscriptionController(object):
    @classonlymethod
    def send_activation_email(cls, action):
        pass
