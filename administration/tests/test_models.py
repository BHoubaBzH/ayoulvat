from django.test import TestCase
from datetime import datetime
from administration.models import *


class FormuleTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Formule.objects.create(nom='The Formule ', cout='50', description="test du model formule")

    def test_nom(self):
        formule = Formule.objects.all().first()
        field_label = formule._meta.get_field('nom').verbose_name
        self.assertEqual(field_label, 'nom')

    def test_cout(self):
        formule = Formule.objects.all().first()
        field_label = formule._meta.get_field('cout').verbose_name
        self.assertEqual(field_label, 'cout')

    def test_commentaire(self):
        formule = Formule.objects.all().first()
        field_label = formule._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')

    def test_nom_max_length(self):
        formule = Formule.objects.all().first()
        max_length = formule._meta.get_field('nom').max_length
        self.assertEqual(max_length, 100)

class LogsTest(TestCase):
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        now = datetime.now
        Logs.objects.create(jour=now.strftime("%d-%m-%Y"), heure=now.strftime("%H:%M:%S"), description="message de log pour les tests")
