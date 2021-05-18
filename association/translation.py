from association.models import Abonnement, Association
from administration.models import Formule
from modeltranslation.translator import register, TranslationOptions


@register(Association)
class AssociationTraductionOptions(TranslationOptions):
    fields  = ('ville', 'pays', 'description')

@register(Abonnement)
class AbonnementTraductionOptions(TranslationOptions):
    fields = ('description',)
