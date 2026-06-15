from django.contrib import admin
from .models import Score


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = (
        'periodo', 'score_geral', 'score_liquidez', 'score_rentabilidade',
        'score_endividamento', 'score_operacional', 'classificacao', 'modelo_ia_usado'
    )
    list_filter = ('classificacao', 'periodo__empresa')
    readonly_fields = ('created_at', 'updated_at', 'narrativa_ia')
