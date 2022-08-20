from django.utils.translation import gettext as _
# fichier de définition des strings par langue du projet

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
flash['fr_fr']['inscr_event_error']         = _("attention, une erreur nous a empeché de t'inscrire à l'évènement {}")

flash['fr_fr']['plan_new_success']          = _("nouveau planning ajouté")
flash['fr_fr']['plan_new_error']            = _("problème de création du planning")
flash['fr_fr']['plan_mod_success']          = _("planning modifié")
flash['fr_fr']['plan_mod_error']            = _("problème de modification du planning")
flash['fr_fr']['plan_sup_success']          = _("planning supprimé")
flash['fr_fr']['plan_sup_error']            = _("attention: il y a encore des créneaux dans ce planning")

flash['fr_fr']['poste_new_success']         = _('nouveau poste ajouté')
flash['fr_fr']['poste_new_error']           = _("le poste n'a pas pu etre créé")
flash['fr_fr']['poste_mod_success']         = _('poste modifié')
flash['fr_fr']['poste_mod_error']           = _("le poste n'a pas pu etre modifié")
flash['fr_fr']['poste_sup_success']         = _('poste supprimé')
flash['fr_fr']['poste_sup_error']           = _('attention: il y a encore des créneaux dans ce poste')

flash['fr_fr']['creneau_new_success']       = _('nouveau créneau ajouté')
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
# text_template['fr_fr']['']        = _("")
#######################################################
#fr_fr
text_template['fr_fr'] = {}

# boutons générique
text_template['fr_fr']['button_add']           = _('Ajouter')
text_template['fr_fr']['button_mod']           = _('Modifier')
text_template['fr_fr']['button_del']           = _('Supprimer')
text_template['fr_fr']['button_null']           = _('Annuler')
text_template['fr_fr']['button_yes']           = _('Oui')
text_template['fr_fr']['button_no']           = _('Non')

#benevole > evenements
text_template['fr_fr']['events_welcome']        = _("Bienvenue")
text_template['fr_fr']['events_welcome_2']      = _("Bienvenue sur le site AYOULVAT. Tu vas pouvoir t'inscrire comme bénévole sur des évènements.")
text_template['fr_fr']['events_retour']         = _("Pour revenir sur cette page click sur 'Evenements' dans la barre du haut.")
text_template['fr_fr']['events_profile']        = _("Pour éditer tes informations, click sur 'mon profil' dans la barre du haut.")
text_template['fr_fr']['events_list']           = _("Voici la liste des evenements")
text_template['fr_fr']['events_yours']          = _("Tes évènements")
text_template['fr_fr']['events_yours_h']        = _("Choisis un association que tu veux représenter, et cliques sur la photo de l'évènement pour y choisir des créneaux:")
text_template['fr_fr']['events_evt_begin']      = _("du :")
text_template['fr_fr']['events_evt_end']        = _("au :")
text_template['fr_fr']['events_assoperso']      = _("sélectionne l'asso que tu représenteras à")
text_template['fr_fr']['events_yourasso']       = _("ton asso")
text_template['fr_fr']['events_not_yours']      = _("Evenements à venir")
text_template['fr_fr']['events_not_yours_h']    = _("Evenements disponible aux quels tu ne participes pas encore:")

#benevole > connexion
text_template['fr_fr']['disconnected']          = _("tu es déconnecté")
text_template['fr_fr']['connection']            = _("Connexion")
text_template['fr_fr']['subscription']          = _("Inscription")

#benevole > navbar
text_template['fr_fr']['administrator']         = _("Administrateur")
text_template['fr_fr']['organiser']             = _("Organisateur")
text_template['fr_fr']['responsible']           = _("Responsable")
text_template['fr_fr']['welcome']               = _("Bienvenue")
text_template['fr_fr']['evt_blocked']           = _("Evènement Bloqué")
text_template['fr_fr']['evt_blocked_h']         = _("L'administrateur n'a pas encore ouvert les inscriptions")
text_template['fr_fr']['evt_ended']             = _("Evènement Terminé")
text_template['fr_fr']['evt_ended_h']           = _("L'événement est terminé")
text_template['fr_fr']['enrolments_tocome']     = _("Inscriptions à Venir")
text_template['fr_fr']['enrolments_tocome_h']   = _("les inscriptions ouvrirons le")
text_template['fr_fr']['enrolments_ongoing']    = _("Inscriptions En Cours, fin le")
text_template['fr_fr']['enrolments_ongoing_h']  = _("les inscriptions seront closes le")
text_template['fr_fr']['enrolments_ended']      = _("Inscriptions Closes")
text_template['fr_fr']['enrolments_ended_h']    = _("les inscriptions sont closes depuis le")
text_template['fr_fr']['volunteer_list']        = _("Liste des bénévoles")
text_template['fr_fr']['volunteer_add']         = _("Ajouter un bénévole")
text_template['fr_fr']['volunteer_mod']         = _("Editer un bénévole")
text_template['fr_fr']['volunteer_sup']         = _("supprimer un bénévole")
text_template['fr_fr']['nav_action']            = _("Action")
text_template['fr_fr']['nav_django_admin']      = _("django admin")
text_template['fr_fr']['nav_events']            = _("Evenements")
text_template['fr_fr']['nav_event']             = _("Evenement")
text_template['fr_fr']['nav_disconnect']        = _("Déconnexion")
text_template['fr_fr']['nav_connect']           = _("Connexion")
text_template['fr_fr']['nav_profile']           = _("Profil")
text_template['fr_fr']['nav_plannings']          = _("Plannings")
text_template['fr_fr']['nav_plannings_h']        = _("Plannings des équipes et tes créneaux")
text_template['fr_fr']['nav_teams']              = _("Equipes")
text_template['fr_fr']['nav_teams_h']            = _("Equipes et planning de l'évènement")
text_template['fr_fr']['nav_planning_perso']    = _("Planning")
text_template['fr_fr']['nav_planning_perso_h']  = _("Ton planning personnel sur l'évènement")
text_template['fr_fr']['nav_participate']       = _("Participer")
text_template['fr_fr']['nav_participate_h']     = _("Participer à l'évènement en tant que bénévole")
text_template['fr_fr']['nav_asso_details']      = _("détails de l'association")

#benevole > footer
text_template['fr_fr']['foot_help']      = _("besoins d'aide? un renseignement?")
#benevole > inscription
# text_template['fr_fr']['subscription']          = _("Inscription") déjà créé

#benevole > profil
text_template['fr_fr']['profile_block']         = _("Profil")
text_template['fr_fr']['profile_title']         = _("Mon Profile")
text_template['fr_fr']['back']                  = _("Retour")
text_template['fr_fr']['record']                = _("Enregistrer")
text_template['fr_fr']['validate']              = _("Valider")

#evenement > creneau affiche
text_template['fr_fr']['slot']                  = _('créneau')
text_template['fr_fr']['free']                  = _('libre')
text_template['fr_fr']['busy']                  = _('occupé')

#evenement > creneau bouton
text_template['fr_fr']['click_to_release_t']    = _('Mon Créneau, cliquer pour le libérer')
text_template['fr_fr']['slot_busy_t']           = _('créneau occupé')
text_template['fr_fr']['reserved_adult_t']      = _('poste réservé adulte')
text_template['fr_fr']['reserved_adult']        = _('Réservé Adultes')
text_template['fr_fr']['slot_available_t']      = _("Céneau Disponible, Cliquer pour s'y incrire")
text_template['fr_fr']['slot_available']        = _('Disponible')
text_template['fr_fr']['already_busy_t']        = _('tu es déjà occupé sur cet horaire')
text_template['fr_fr']['slot_mine_t']           = _('Mon Créneau')
text_template['fr_fr']['slot_closed_t']         = _('poste non ouvert')
text_template['fr_fr']['slot_closed']           = _('Réservé')
text_template['fr_fr']['volunteer_infos_t']     = _('infos bénévole:')
text_template['fr_fr']['volunteer_email_t']     = _('email :')
text_template['fr_fr']['volunteer_phone_t']     = _('tel :')

#evenement > equipe ajoute
text_template['fr_fr']['team_add_t']            = _("Ajout d'une équipe")

#evenement > equipe edite
text_template['fr_fr']['team_mod_t']            = _('éditer cette equipe')
text_template['fr_fr']['team_mod']              = _("édition équipe: ")

#evenement > equipe explique
text_template['fr_fr']['team']                  = _('Equipe')
text_template['fr_fr']['team_help']             = _("Choisis un planning dans le menu de gauche pour t'insrire sur un créneau")

#evenement > error message
text_template['fr_fr']['error_msg_warning']     = _('Attention :')

#evenement > grid cellules
#on est ici
#text_template['fr_fr']['']           = _('')

#evenement > page evenement
text_template['fr_fr']['evenement_title']       = _('Evenement : Les équipes et leurs plannings associés')
text_template['fr_fr']['evenement_title_h']     = _('les planning des différentes équipes pour l\'évènement')
text_template['fr_fr']['evenement_equipe']      = _('équipe')
text_template['fr_fr']['evenement_equipe_h']    = _('description')
text_template['fr_fr']['evenement_no_equipe']   = _('pas encore d\'équipe définie')

#association

#administration
