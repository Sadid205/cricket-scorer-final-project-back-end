from django.apps import apps
def get_over():
    Over = apps.get_model('over','Over')
    return Over
