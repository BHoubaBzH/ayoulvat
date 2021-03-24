from django.apps import AppConfig


class BenevoleConfig(AppConfig):
    name = 'benevole'

    # gestion des signaux
    def ready(self):
        import benevole.signals