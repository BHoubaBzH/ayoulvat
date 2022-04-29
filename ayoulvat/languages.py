from django.utils.translation import gettext as _
# fichier de définition des constantes du projet

language = 'fr_fr'
flash = {}
text_template = {}
#######################################################
# messages flash
#######################################################
#fr_fr
flash['fr_fr']= {}
flash['fr_fr']['inscr_creneau_success']     = _("tu viens de t'inscrire sur un créneau, Merci!")
flash['fr_fr']['inscr_creneau_error']       = _("attention, une erreur nous a empeché de t'inscrire à l'évènement")
flash['fr_fr']['free_creneau_success']      = _("le créneau est libéré")

flash['fr_fr']['message_sent_success']      = _("Message envoyé")
flash['fr_fr']['message_sent_error']        = _("erreur d'envoi du message")

flash['fr_fr']['profile_up_success']        = _("Profil mis à jour")
flash['fr_fr']['inscr_event_success']       = _("Bravo! Tu es maintenant inscrit à l'évènement {}")
flash['fr_fr']['inscr_event_error']       = _("attention, une erreur nous a empeché de t'inscrire à l'évènement {}")

flash['fr_fr']['plan_new_success']          = _("nouveau planning ajouté")
flash['fr_fr']['plan_new_error']            = _("problème de création du planning")
flash['fr_fr']['plan_mod_success']          = _("planning modifié")
flash['fr_fr']['plan_mod_error']            = _("problème de modification du planning")
flash['fr_fr']['plan_sup_success']          = _("planning supprimé")
flash['fr_fr']['plan_sup_error']            = _("attention: il y a encore des créneaux dans ce planning")

flash['fr_fr']['poste_new_success']          = _('nouveau poste ajouté')
flash['fr_fr']['poste_new_error']           = _("le poste n'a pas pu etre créé")
flash['fr_fr']['poste_mod_success']         = _('poste modifié')
flash['fr_fr']['poste_mod_error']           = _("le poste n'a pas pu etre modifié")
flash['fr_fr']['poste_sup_success']         = _('poste supprimé')
flash['fr_fr']['poste_sup_error']           = _('attention: il y a encore des créneaux dans ce poste')

flash['fr_fr']['creneau_new_success']        = _('nouveau créneau ajouté')
flash['fr_fr']['creneau_new_error']         = _("le créneau n'a pas pu etre créé")
flash['fr_fr']['creneau_mod_success']       = _('créneau modifié')
flash['fr_fr']['creneau_mod_error']         = _("problème de modification du créneau")
flash['fr_fr']['creneau_sup_success']       = _('créneau supprimé')
flash['fr_fr']['creneau_sup_error']         = _("problème de supression du créneau")

flash['fr_fr']['event_new_success']         = _("")
flash['fr_fr']['event_new_error']           = _("")
flash['fr_fr']['event_mod_success']         = _("")
flash['fr_fr']['event_new_error']           = _("")
flash['fr_fr']['event_sup_success']         = _("")
flash['fr_fr']['event_new_error']           = _("")

flash['fr_fr']['asso_new_success']          = _("")
flash['fr_fr']['asso_new_error']            = _("")
flash['fr_fr']['asso_mod_success']          = _("")
flash['fr_fr']['asso_new_error']            = _("")
flash['fr_fr']['asso_sup_success']          = _("")
flash['fr_fr']['asso_new_error']            = _("")


#######################################################
# textes templates
#######################################################
#fr_fr
text_template['fr_fr'] = {}
#benevole > page evenements
text_template['fr_fr']['evenements_welcome']        = _("Bienvenue")
text_template['fr_fr']['evenements_welcome_2']      = _("Bienvenue sur le site AYOULVAT. Tu vas pouvoir t'inscrire comme bénévole sur des évènements.")
text_template['fr_fr']['evenements_retour']         = _("Pour revenir sur cette page click sur 'Evenements' dans la barre du haut.")
text_template['fr_fr']['evenements_profil']         = _("Pour éditer tes informations, click sur 'mon profil' dans la barre du haut.")
text_template['fr_fr']['evenements_liste']          = _("Voici la liste des evenements")
text_template['fr_fr']['evenements_yours']          = _("Tes évènements")
text_template['fr_fr']['evenements_yours_h']        = _("Choisis un association que tu veux représenter, et cliques sur la photo de l'évènement pour y choisir des créneaux:")
text_template['fr_fr']['evenements_evt_begin']      = _("du :")
text_template['fr_fr']['evenements_evt_end']        = _("au :")
text_template['fr_fr']['evenements_assoperso']      = _("sélectionne l'asso que tu représenteras à")
text_template['fr_fr']['evenements_tonasso']        = _("ton asso")
text_template['fr_fr']['evenements_not_yours']      = _("Evenements à venir")
text_template['fr_fr']['evenements_not_yours_h']    = _("Evenements disponible aux quels tu ne participes pas encore:")
#evenement > page evenement
text_template['fr_fr']['evenement_title'] = _('Evenement : Les équipes et leurs plannings associés')
text_template['fr_fr']['evenement_title_h'] = _('les planning des différentes équipes pour l\'évènement')
text_template['fr_fr']['evenement_equipe'] = _('équipe')
text_template['fr_fr']['evenement_equipe_h'] = _('description')
text_template['fr_fr']['evenement_no_equipe'] = _('pas encore d\'équipe définie')
#benevole > navbar