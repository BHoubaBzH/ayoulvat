from datetime import datetime
from django.forms import MultiWidget, TextInput


# Django splitDateTime widget, no JS, using modern HTML for time and date selectors
class SplitDateTimeMultiWidget(MultiWidget):
    def __init__(self, widgets=None, attrs=None):
        if widgets is None:
            if attrs is None:
                attrs = {}
            if not 'date_attrs' in attrs:
                attrs['date_attrs'] = {}

            if not 'time_attrs'in attrs:
                attrs['time_attrs'] = {}

            date_attrs = attrs['date_attrs'].copy()
            time_attrs = attrs['time_attrs'].copy()

            date_attrs['type'] = 'date'
            time_attrs['type'] = 'time'
            # time_attrs['step'] = '1800'
            time_attrs['min'] = '0'
            time_attrs['max'] = '60'

            widgets = [
                TextInput(attrs=date_attrs),
                TextInput(attrs=time_attrs),
            ]
        super().__init__(widgets, )

    # nabbing from https://docs.djangoproject.com/en/3.1/ref/forms/widgets/#django.forms.MultiWidget.decompress
    def decompress(self, value):
        if value:
            return [value.date(), value.strftime('%H:%M')]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        date_str, time_str = super().value_from_datadict(data, files, name)
        # DateField expects a single string that it can parse into a date.

        if date_str == time_str == '':
            return None

        if time_str == '':
            time_str = '00:00'

        my_datetime = datetime.strptime(date_str + ' ' + time_str, "%Y-%m-%d %H:%M")
        # return make_aware(my_datetime)
        return my_datetime