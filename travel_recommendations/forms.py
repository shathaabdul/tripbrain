from django import forms

class TravelPreferenceForm(forms.Form):
    age_range = forms.ChoiceField(choices=[
        ('18-30', '18-30'),
        ('30-50', '30-50'),
        ('50+', '50+')
    ])
    
    city_type = forms.ChoiceField(choices=[
        ('beach', 'Beach'),
        ('mountain', 'Mountain'),
        ('city', 'City')
    ])

    continent = forms.ChoiceField(choices=[
    ('Asia', 'Asia'),
    ('Europe', 'Europe'),
    ('Africa', 'Africa'),
    ('North America', 'North America'),
    ('South America', 'South America'),
    ('Australia', 'Australia'),
    ('Middle East', 'Middle East')
    ], label="Which continent would you like to visit?")


    companions = forms.ChoiceField(choices=[
        ('solo', 'Solo'),
        ('friends', 'Friends'),
        ('family', 'Family')
    ])

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label="Start Date"
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label="End Date"
    )

    budget = forms.ChoiceField(choices=[
        ('<2000', 'Under $2,000'),
        ('2000-5000', '$2,000 - $5,000'),
        ('>5000', 'Over $5,000')
    ], label="Budget")


    
