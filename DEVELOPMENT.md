# 개발자 가이드

## CI/CD 설정

이 프로젝트는 GitHub Actions를 사용하여 자동화된 테스트를 실행합니다.

### GitHub Secrets 설정

로컬에서의 테스트와 GitHub Actions에서의 테스트 모두 KIPRIS API 키가 필요합니다. API 키는 안전하게 관리됩니다:

#### 로컬 개발 환경
```bash
# .env 파일 생성 (프로젝트 루트 또는 src/)
echo "KIPRIS_API_KEY=your_api_key_here" > .env
```

#### GitHub Actions 설정
1. GitHub 리포지토리로 이동
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret** 클릭
4. 이름: `KIPRIS_API_KEY`
5. 값: 실제 KIPRIS API 키
6. **Add secret** 클릭

### 보안 주의사항
- ✅ API 키는 GitHub Secrets에 안전하게 저장됩니다
- ✅ Secrets는 암호화되어 저장되며 로그에 노출되지 않습니다
- ✅ Pull Request에서도 secret 값은 노출되지 않습니다
- ❌ 절대 코드에 API 키를 하드코딩하지 마세요
- ❌ `.env` 파일은 커밋하지 마세요 (이미 .gitignore에 포함됨)

### CI 워크플로우

`.github/workflows/test.yml` 파일에서 정의된 워크플로우가 다음 상황에서 실행됩니다:

- **Push**: `main` 또는 `develop` 브랜치
- **Pull Request**: `main` 또는 `develop` 브랜치 대상

#### 실행되는 테스트
1. **Linting**: `ruff check`로 코드 스타일 검사
2. **Format check**: `ruff format --check`로 포맷 검사
3. **Unit tests**: `pytest`로 테스트 실행
4. **Coverage**: 테스트 커버리지 계산

#### 지원하는 Python 버전
- Python 3.11
- Python 3.12

### 로컬에서 CI 테스트 실행

GitHub Actions와 동일한 환경에서 로컬에서도 테스트할 수 있습니다:

```bash
# linting
ruff check src/

# formatting check
ruff format --check src/

# tests with coverage
pytest test/ -v --cov=src/mcp_kipris --cov-report=term-missing
```

### Codecov 설정 (선택사항)

테스트 커버리지를 Codecov에 업로드하려면:

1. [Codecov](https://codecov.io/)에서 GitHub 리포지토리 연동
2. Codecov에서 제공하는 token을 복사
3. GitHub Secrets에 `CODECOV_TOKEN`으로 추가
4. README에 이미 추가된 codecov badge가 자동으로 커버리지를 표시합니다

Codecov token이 없어도 테스트는 실행되며, 커버리지 리포트는 GitHub Actions 요약 페이지에서 확인할 수 있습니다.

## 로컬 개발

### 의존성 설치
```bash
pip install -e .
```

### 코드 스타일
이 프로젝트는 다음 도구를 사용합니다:
- **ruff**: formatting, linting (black, flake8, isort 대체)
- **pytest**: testing framework

### 커밋 전 체크리스트
- [ ] `ruff check src/` 통과
- [ ] `ruff format src/` 적용
- [ ] `pytest test/` 통과
- [ ] 테스트 커버리지 확인
