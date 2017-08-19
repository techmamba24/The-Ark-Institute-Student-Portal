from django import forms

from .models import QuranPost, QuranComment, IslamicStudiesPost,IslamicStudiesComment,QuranExam, IslamicStudiesExam, QuranAttendance


class QuranPostForm(forms.ModelForm):
    class Meta:
        model = QuranPost
        fields = ('title', 'message')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'textinputclass'}),
            'message': forms.Textarea(attrs={'class': 'editable medium-editor-textarea postcontent'}),
        }


class QuranCommentForm(forms.ModelForm):

    class Meta:
        model = QuranComment
        fields = ('comment',)

        widgets = {
            'comment': forms.Textarea(attrs={'class': 'editable medium-editor-textarea'}),
        }

class IslamicStudiesPostForm(forms.ModelForm):
    class Meta:
        model = IslamicStudiesPost
        fields = ('title', 'message')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'textinputclass'}),
            'message': forms.Textarea(attrs={'class': 'editable medium-editor-textarea postcontent'}),
        }


class IslamicStudiesCommentForm(forms.ModelForm):

    class Meta:
        model = IslamicStudiesComment
        fields = ('comment',)

        widgets = {
            'comment': forms.Textarea(attrs={'class': 'editable medium-editor-textarea'}),
        }

class QuranExamForm(forms.ModelForm):

    class Meta:
        model = QuranExam
        fields = ('exam_number','exam_score')


class IslamicStudiesExamForm(forms.ModelForm):

    class Meta:
        model = IslamicStudiesExam
        fields = ('exam_number','exam_score')

class QuranAttendanceForm(forms.ModelForm):

    class Meta:
        model = QuranAttendance
        fields = ('week','attendance',)
