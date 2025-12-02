# TODO

- 프로젝트 구조 잡기: `main.py`, `Dockerfile`, `pyproject.toml`(또는 requirements) 최소 구성 생성
- 시스템 프롬프트 구현: `PLAN.md`에 제시된 리뷰어 프롬프트를 코드/리소스 파일에 정리하고 불러오기
- 입력 처리 로직 작성: 프로젝트명·PR 번호·git diff를 CLI 또는 stdin으로 받아 파싱
- 리뷰 생성 파이프라인 설계: 입력 컨텍스트를 묶어 LLM 호출(또는 모의 로직)로 전달하고 응답 포맷(주요 이슈/추가 개선 아이디어) 보장
- Clean Architecture 적용: controller/service/domain/entity 계층으로 책임 분리
- 로깅 및 에러 처리 추가: 구조화된 로깅과 오류 메시지 정의
- 테스트 작성: 핵심 모듈에 대한 단위 테스트(입력 파싱, 포맷팅, 프롬프트 조립 등)
- Docker 빌드 스크립트 확정: 이미지 빌드·실행 커맨드 검증
- GitLab CI 연동 준비: 파이프라인에서 실행될 엔트리포인트와 종속성 확인
