from django.db import models


class Scenario(models.Model):
    scenario_text = models.TextField("동화책 시나리오")
    recommendations = models.JSONField("추천 시나리오", default=list)  # 추천된 시나리오들을 JSON 형태로 저장
    selected_story = models.TextField("선택된 시나리오", blank=True, null=True)  # 사용자가 선택한 시나리오
    story_pages = models.JSONField("동화책 페이지", default=list)  # 10페이지 분량의 동화책 내용
    created_at = models.DateTimeField(auto_now_add=True)
    
class StoryPageImage(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="images")
    page_number = models.IntegerField("페이지 번호")
    original_image = models.ImageField(upload_to="original_images/")
    enhanced_image = models.ImageField(upload_to="enhanced_images/", blank=True, null=True)