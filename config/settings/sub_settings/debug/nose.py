import os

# ref : https://nose.readthedocs.io/en/latest/usage.html#configuration

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
TEST_OUTPUT_DIR = os.environ.get("TEST_OUTPUT_DIR", ".")

NOSE_ARGS = [
    '--verbosity=2',
    '--nologcapture',
    '--with-coverage',
    '--cover-package=app1,app2,app3',
    # '--cover-package=.'
    '--with-spec',
    '--spec-color',
    '--with-xunit',
    '--xunit-file=%s/unittests.xml' % TEST_OUTPUT_DIR,
    '--cover-html',
    '--cover-xml',
    '--cover-xml-file=%s/coverage.xml' % TEST_OUTPUT_DIR,
    '--cover-inclusive',
    # '--cover-html-dir=reports/cover'
    '--exe',
]

'''
--cover-html : html 문서를 만들어준다.
--cover-inclusive : 작업 디렉토리의 모든 파일을 스캔하는 범위를 나타냅니다(테스트되지 않는 파일을 찾는 데 유용함).
환경 설정 파일 .coveragerc 을 만들고 아래와 같이 입력한다.
[run]
omit = ../*migrations* # 실행시 migrations 폴더는 테스트하지 않겠다는 뜻(테스트 필요가 없는 대표 폴더)
'''