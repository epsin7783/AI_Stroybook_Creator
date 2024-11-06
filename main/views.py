from .models import Scenario, StoryPageImage
from .forms import ScenarioForm, SelectRecommendationForm
from django.shortcuts import render, redirect,  get_object_or_404
from django.template import loader
from django.views.generic import View
from django.http import HttpResponse
from django.core.files.base import ContentFile
import openai
import os
import base64
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class MainView(View):
    def get(self, request):
        template = loader.get_template("base.html")
        context = {}
        
        return HttpResponse(template.render(context, request))
    

# 시나리오 추천 생성 함수
def get_scenario_recommendations(scenario):
    recommendations = []
    for i in range(3):  # 세 개의 추천 시나리오 생성
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 5-7세 아이들을 위한 동화책 작가입니다. 간단하고 이해하기 쉬운 문장으로 이야기를 전달하는 것을 목표로 합니다."},
                {"role": "user", "content": f"{scenario} 이 이야기를 5-7세 어린이가 이해할 수 있는 쉬운 언어로, 4-5문장의 간결한 동화 형식으로 다시 작성해 주세요. 각 문장은 짧고 따뜻한 느낌을 주도록 하세요."}
            ]
        )
        recommendations.append(response.choices[0].message['content'].strip())
    return recommendations

# 10페이지 동화책 생성 함수
def generate_story_pages(selected_story):
    story_pages = []
    for i in range(1, 11):  # 10페이지 분량 생성
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 5-7세 아이들을 위한 동화책 작가입니다. 각 페이지는 간단하고 따뜻한 느낌의 2~3문장으로 구성되어야 합니다."},
                {"role": "user", "content": f"{selected_story} 이야기를 10페이지 동화책으로 만들어주세요. 지금은 {i}번째 페이지입니다. 이 페이지의 내용을 2~3문장으로 간단하게 작성해주세요. 각 페이지가 독립적인 이야기 흐름을 가질 수 있도록 해주세요."}
            ],
            # max_tokens=50  # 페이지마다 짧은 내용 생성
        )
        page_content = response.choices[0].message['content'].strip()
        story_pages.append(page_content)  # 각 페이지 내용을 배열에 추가
    return story_pages

# 시나리오 입력 및 추천 뷰
def scenario_view(request):
    if request.method == "POST":
        form = ScenarioForm(request.POST)
        if form.is_valid():
            # 폼 데이터를 가져와서 Scenario 모델에 저장
            scenario_text = form.cleaned_data["scenario"]
            recommendations = get_scenario_recommendations(scenario_text)
            
            # Scenario 모델 인스턴스 생성 및 저장 (추천 시나리오 포함)
            scenario_instance = Scenario.objects.create(
                scenario_text=scenario_text,
                recommendations=recommendations
            )
            
            # 추천 결과와 함께 선택 폼으로 리다이렉트
            return redirect('select_recommendation', scenario_id=scenario_instance.id)
    else:
        form = ScenarioForm()
    return render(request, "scenario_form.html", {"form": form})

# 추천 시나리오 선택 및 동화책 생성 뷰
def select_recommendation(request, scenario_id):
    scenario_instance = Scenario.objects.get(id=scenario_id)
    
    if request.method == "POST":
        form = SelectRecommendationForm(request.POST)
        form.fields['selected_recommendation'].choices = [(rec, rec) for rec in scenario_instance.recommendations]
        
        if form.is_valid():
            # 선택된 추천 시나리오 저장
            selected_story = form.cleaned_data["selected_recommendation"]
            scenario_instance.selected_story = selected_story
            
            # 10페이지 분량의 동화책 생성 및 저장
            story_pages = generate_story_pages(selected_story)
            scenario_instance.story_pages = story_pages
            scenario_instance.save()
            
            return render(request, "story_pages.html", {
                "story_pages": story_pages,
                "selected_story": selected_story
            })
    else:
        form = SelectRecommendationForm()
        form.fields['selected_recommendation'].choices = [(rec, rec) for rec in scenario_instance.recommendations]

    return render(request, "select_recommendation.html", {
        "form": form,
        "scenario_instance": scenario_instance
    })
    
    

def save_user_drawing(request, scenario_id, page_number):
    scenario = get_object_or_404(Scenario, id=scenario_id)

    if request.method == "POST":
        # 그림 데이터 수신 및 저장
        image_data = request.POST.get("image_data")
        if image_data:
            format, imgstr = image_data.split(';base64,')
            img_data = base64.b64decode(imgstr)
            img_file = ContentFile(img_data, name=f'scenario_{scenario_id}_page_{page_number}.png')

            # StoryPageImage 모델 인스턴스 생성 및 저장
            story_image = StoryPageImage.objects.create(
                scenario=scenario,
                page_number=page_number,
                original_image=img_file
            )

            # DALL-E 보정
            enhanced_image_url = enhance_image_with_dalle(story_image.original_image.path)
            if enhanced_image_url:
                # DALL-E 보정 결과 저장
                response = request.get(enhanced_image_url)
                enhanced_img = ContentFile(response.content, name=f'scenario_{scenario_id}_page_{page_number}_enhanced.png')
                story_image.enhanced_image.save(enhanced_img.name, enhanced_img)
                story_image.save()

            return redirect("story_pages", scenario_id=scenario_id)
    return render(request, "save_drawing.html")

def enhance_image_with_dalle(image_path):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    response = openai.Image.create(
        prompt="A child-friendly, fairytale-style drawing",
        image=image_data,
        n=1,
        size="1024x1024"
    )

    if response and response['data']:
        return response['data'][0]['url']
    return None