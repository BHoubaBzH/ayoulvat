# ficher présent dans la sidebar, donc dans tout le projet

from django import template
from django.template.defaultfilters import stringfilter



register = template.Library()

@register.filter
def get_item(dictionaire, key):
    """
        fonction retournant la valeur pour une clé dans un dictionnaire.
        usage : dictionnaire|get_item:item.key 
    """
    return dictionaire.get(key)

@register.filter 
def has_group(user, group_name):
    """
        fonction permettant de trouver si le user appartient a un groupe
    """
    return user.groups.filter(name=group_name).exists() 

@register.filter(name='annees_split', is_safe=True)
@stringfilter
def annees_split(value, delimiter=None):
    """
        garde la string jusqu'au paramète donné et transforme en integer le resultat sur 2 digits
    """
    return f"{int(value.split(delimiter)[0]):02d}"
