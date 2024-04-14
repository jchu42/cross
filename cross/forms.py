from django import forms
from .models import UserData
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class RegisterForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100)
    password1 = forms.CharField(label="Password", max_length=100)
    password2 = forms.CharField(label="Confirm Password", max_length=100)
    def clean(self):
        cleaned_data = super().clean()

        if User.objects.filter(username=cleaned_data["username"]).exists():
            raise forms.ValidationError("Error: Username already exists")
        
        if cleaned_data["password1"] != cleaned_data["password2"]:
            raise forms.ValidationError("Error: Passwords don't match")

class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100)
    password = forms.CharField(label="Password", max_length=100)
    def clean(self):
        cleaned_data = super().clean()
        user = authenticate(username=cleaned_data["username"], password=cleaned_data["password"])
        if user is None:
            raise forms.ValidationError("Error: Username and Password don't match")

class PuzzleBox(forms.Form):
    def __init__(self, spacingx=0, spacingy=0, length=0, puzzle=[], *args, **wargs):
        super(PuzzleBox, self).__init__(*args, **wargs)

        
        # stupid way to make it 12x12
        while len(puzzle) < 12:
            puzzle.append("")
        for x, line in enumerate(puzzle):
            while len(puzzle[x]) < 12:
                puzzle[x] += "_"

        for y, line in enumerate(puzzle):
            for x, char in enumerate(line):
                coords = str(x) + "," + str(y)
                if char == "_":
                    self.fields[coords] = forms.CharField(max_length=1, required=False)
                    self.fields[coords].widget.attrs['class'] = 'empty'
                elif x >= spacingx and x < spacingx + length and y >= spacingy and y < spacingy + length:
                    self.fields[coords] = forms.CharField(max_length=1, required=False)
                    self.fields[coords].widget.attrs['class'] = 'awawa'
                else:
                    self.fields[coords] = forms.CharField(max_length=1, required=False)

        

