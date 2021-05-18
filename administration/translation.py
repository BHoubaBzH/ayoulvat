from administration.models import Formule
from modeltranslation.translator import register, TranslationOptions


@register(Formule)
class FormuleTraductionOptions(TranslationOptions):
    """
        champs Formule à traduire
    """
    fields = ('nom', 'description')


class LogsTraductionOptions(TranslationOptions):
    """
        logs traduction : rien 
    """
    pass
