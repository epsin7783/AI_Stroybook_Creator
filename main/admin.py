from django.contrib import admin
from main.models import Scenario, StoryPageImage

class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("scenario_text", "recommendations", "selected_story","story_pages","created_at")
admin.site.register(Scenario, ScenarioAdmin)

class StoryPageImageAdmin(admin.ModelAdmin):
    list_display = ("scenario", "page_number", "selected_story","original_image","enhanced_image")
admin.site.register(StoryPageImage, StoryPageImageAdmin)