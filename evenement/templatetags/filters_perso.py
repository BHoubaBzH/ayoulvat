from django import template

register = template.Library()


@register.filter
def get_item(dictionaire, key):
    """
        fonction retournant la valeur pour une clé dans un dictionnaire.
        usage : dictionnaire|get_item:item.key 
    """
    return dictionaire.get(key)


