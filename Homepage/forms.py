from django import forms
from .models import QuestionAnswer, UnansweredQuestion, FixedQuestions

class AddQuestionForm(forms.ModelForm):
    class Meta:
        model = QuestionAnswer
        fields = ['question', 'answer']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control'}),
        }

# class AddQuestionForm(forms.ModelForm):
#     class Meta:
#         model = QuestionAnswer
#         fields = ['question', 'answer_type', 'answers']
#         widgets = {
#             'question': forms.TextInput(attrs={'class': 'form-control'}),
#             'answers': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 5,
#                 'placeholder': '?? ?????? ???????? ???? ?? ????? ?? ??? ????.'
#             }),
#         }
#
#     def clean_answers(self):
#         answer_type = self.cleaned_data.get('answer_type')
#         answers = self.cleaned_data.get('answers')
#
#         if answer_type == 'multiple' and not answers:
#             raise forms.ValidationError("??? ????? ???????? ????????.")
#         if answer_type == 'single' and '\n' in answers:
#             raise forms.ValidationError("??????? ??????? ?? ???? ?? ????? ??? ???? ??????.")
#
#         return answers

class QuestionForm(forms.Form):
    question = forms.CharField(label='Your question', max_length=255)

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Upload an Excel file')

class UnansweredQuestionForm(forms.ModelForm):
    class Meta:
        model = UnansweredQuestion
        fields = ['question']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EditUnAnswerQuestionForm(forms.ModelForm):
    class Meta:
        model = UnansweredQuestion
        fields = ['question']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'})
        }

class FixedQuestionForm(forms.ModelForm):
    class Meta:
        model = FixedQuestions
        fields = ['question', 'answer']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control'}),
        }