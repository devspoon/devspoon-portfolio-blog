import os
from uuid import uuid4
from django.utils import timezone

def date_upload_to_for_image(instance, filename):
    # upload_to="%Y/%m/%d" 처럼 날짜로 세분화
    ymd_path = timezone.now().strftime("%Y/%m/%d")
    # 길이 32 인 uuid 값
    uuid_name = uuid4().hex
    # 확장자 추출
    extension = os.path.splitext(filename)[-1].lower()
    # 결합 후 return
    return "/".join(
        [
            'images_',
            ymd_path,
            uuid_name + extension,
        ]
    )


def date_upload_to_for_file(instance, filename):
    # upload_to="%Y/%m/%d" 처럼 날짜로 세분화
    ymd_path = timezone.now().strftime("%Y/%m/%d")
    # 길이 32 인 uuid 값
    uuid_name = uuid4().hex
    # 확장자 추출
    extension = os.path.splitext(filename)[-1].lower()
    # 결합 후 return
    return "/".join(
        [
            'files_',
            ymd_path,
            uuid_name + extension,
        ]
    )