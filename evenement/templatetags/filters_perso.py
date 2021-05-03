from django import template

register = template.Library()

"""
    fonction retournant la valeur pour une clé dans un dictionnaire.
    usage : dictionnaire|get_item:item.key 
"""
@register.filter
def get_item(dictionaire, key):
    return dictionaire.get(key)
