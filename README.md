# Custom Robot Builder
Streamlit MVP + GitHub-ready structure

이 레포는 Streamlit 기반의 UI를 위한 MVP 구조를 제공합니다. 핵심 로직은 robot_core 패키지에 분리되어 있으며, Streamlit 앱은 streamlit_app/app.py에서 UI를 구성합니다.

설치 및 실행
- 파이썬 3.8+ 권장
- 의존성 설치: pip install -r requirements.txt
- 스트림릿 실행: streamlit run repo/streamlit_app/app.py

배포/배포 파이프라인
- GitHub에 레포를 생성하고, main 브랜치에 푸시합니다.
- CI를 통해 간단한 테스트/리포지토리 구성을 확인합니다.

향후 확장 포인트
- GitHub Actions 워크플로우 추가
- 추가 모듈, 테스트, 도구 연결
