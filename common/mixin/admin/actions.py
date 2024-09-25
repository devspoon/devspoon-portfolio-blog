from django.db import transaction


class CustomActionsAdminMixin:
    # actions = [
    #     "copy_selected_items",
    # ]

    def copy_selected_items(self, request, queryset):
        # 트랜잭션을 사용하여 데이터 일관성을 보장
        with transaction.atomic():
            for item in queryset:
                # 기존 항목의 데이터를 복사하여 새 항목 생성
                item.pk = None  # 기본 키를 None으로 설정하여 새 객체로 인식하게 함
                item.title = f"[copy] - {item.title}"  # 제목에 "[copy] - " 추가
                item.save()  # 새 항목 저장

        self.message_user(request, "The selected items have been copied.")

    copy_selected_items.short_description = "Copy selected items"

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions["delete_selected"]
        return actions

    