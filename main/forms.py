from django import forms

class ScenarioForm(forms.Form):
    scenario = forms.CharField(
        label = "동화책 시나리오를 입력하세요",
        widget=forms.Textarea(attrs={'row':5, 'cols':50})
    )
    

class SelectRecommendationForm(forms.Form):
    selected_recommendation = forms.ChoiceField(
        label="추천된 시나리오 중 하나를 선택하세요",
        choices=[],  # 뷰에서 추천 시나리오로 동적으로 채울 예정
        widget=forms.RadioSelect
    )