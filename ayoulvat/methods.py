"""
fichier ded déclaration des fonctions génériques du ^rojet
"""
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)



def envoi_courriel(sujet, message_text, from_courriel, to_courriel, message_html):
    try:
        send_mail(sujet, message_text, from_courriel, to_courriel, html_message=message_html)
    except BadHeaderError:
        return HttpResponse('Header incorrect détecté.')
    return HttpResponseRedirect('')