from django.conf import settings
from ayoulvat import settings as set

# variables globales a destination du processor template
# ce processor custom a été ajouté au fichier settings et est évalué a chaque appel de template
def custom_constants(request):
    return {
        'global_site_name': set.SITENAME,
        }
