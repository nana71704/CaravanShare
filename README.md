 🚀 Caravan Share 서비스 접속 주소

* **서비스 URL:** https://web-production-79b14.up.railway.app/  

* **실행 방법:** gunicorn을 사용하여 Procfile에 명시된 대로 서버를 실행합니다.

-----
🚀 1. 프로젝트 개요 및 기술 스택

이 섹션은 프로젝트의 목적과 사용된 핵심 기술을 명시합니다.

| 분류 | 내용 |
| :--- | :--- |
| 프로젝트명 | Caravan Share 서비스 |
| 목적 | 사용자 간 캐러밴 공유 및 예약 관리 시스템 구축 |
| 백엔드 언어 | Python 3.10+ |
| 프레임워크 | Flask** (웹 프레임워크), Gunicorn (프로덕션 WSGI 서버) |
| 데이터베이스 | SQLite (개발용) / 설정 시 Postgres, MySQL 등으로 확장 가능 |

-----
 🏗️ 2. 프로젝트 아키텍처 및 폴더 구조

본 프로젝트는 계층형 아키텍처(Layered Architecture)를 채택하여 비즈니스 로직과 데이터 접근 계층을 명확히 분리하여 설계되었습니다.

```
CaravanShare/
├── src/
│ ├── models/          # 데이터 구조 정의 (예: Caravan, User, Reservation 클래스)
│ ├── services/        # 핵심 비즈니스 로직 (예: 예약 가능 여부 검증, 가격 계산)
│ ├── repositories/    # 데이터 접근 계층 (CRUD 작업 담당)
│ └── exceptions/      # 커스텀 예외 정의
├── main.py            # 진입점(Entry Point) 및 라우팅(Controller)
├── tests/             # 테스트 코드
├── requirements.txt   # 라이브러리 목록 (배포 필수)
└── Procfile           # 서버 실행 명령어 (배포 필수)
```

-----
🛠️ 3. 환경 구축 및 배포 문제 해결 상세 기록

본 프로젝트는 IaaS/PaaS 환경에 배포 가능한 형태로 코드를 준비하는 과정에서 발생했던 다양한 기술적 문제를 해결하며 안정화되었습니다.

*A. 초기 설정 문제 해결 (Replit 환경)**

| 문제 | 발생 원인 | 해결 방법 |
| :--- | :--- | :--- |
| 로컬 서버 `Not Found` 오류 | Flask 기본 포트(5000)와 Replit 예상 포트(8080) 불일치 및 기본 라우트(`@app.route('/')`) 부재. | `main.py`에서 서버 실행 포트를 \*\*`host='0.0.0.0', port=8080`\*\*으로 명시하고, 기본 응답 메시지를 반환하는 루트 라우트를 추가하여 해결. |
| Git Push 실패| Replit과 GitHub 간의 인증 연결 끊김 발생. | Replit의 Settings 탭에서 GitHub 계정을 재연결(Sign in)하여 권한을 복구함. |

B. Railway 배포 시 라이브러리 충돌 및 빌드 오류 해결

Railway 배포를 위해 `requirements.txt`와 Procfile 파일을 정의했으나, 빌드 과정에서 호환성 오류가 연속적으로 발생했습니다.

| 문제 | 오류 메시지 | 해결 방법 |
| :--- | :--- | :--- |
| 1차 충돌 (WSGI 서버 미설치)| `/bin/bash: line 1: gunicorn: command not found` | `requirements.txt` 파일에 `gunicorn`을 추가하여 Railway가 서버 구동 엔진을 설치하도록 명시. |
| 2차 충돌 (C/C++ 컴파일 오류) | `error: command '/usr/bin/c++' failed` (greenlet 설치 중) | `greenlet==3.0.3` 버전이 시스템 환경과 충돌하여 발생. 버전 정보(`==3.0.3`)를 제거하여 `greenlet`의 최신 호환 버전을 설치하도록 유도하여 해결. |
| 3차 충돌 (SQLAlchemy 비호환성) | `AssertionError: class 'sqlalchemy.elements.SQLCoreOperations' ...` | `Flask-SQLAlchemy`와 `SQLAlchemy` 간의 비호환성 문제. 두 라이브러리 모두 버전 정보를 제거하여 설치 시 최신 호환 버전이 자동으로 선택되도록 수정. |
| 4차 충돌 (`typing-extensions`)** | `AttributeError: attribute '__default__' of 'typing.ParamSpec' objects is not writable` | `typing-extensions==4.10.0` 버전과 `SQLAlchemy`의 충돌 문제. `typing-extensions`의 버전 정보도 제거**하여 모든 의존성 문제가 해결된 최적의 환경을 구축함. |

-----

🌐 4. 서비스 접속 정보 및 제출 요구사항 충족 근거

| 요구사항 | 충족 여부 및 상세 설명 |
| :--- | :--- |
| GitHub Repository URL 제출 | **✅ 완료:** `https://github.com/nana71704/CaravanShare` |
| EC2/Compute Engine 인스턴스에 앱 배포 (Level 1) | △ 대안 배포:** 시간 부족으로 AWS/GCP 대신 Railway PaaS에 배포하였으나, `Procfile`과 `requirements.txt`를 통해 VM 인스턴스 환경에서 즉시 배포 가능하도록 설계됨. |
|Public IP로 접속 가능 (Level 1) | ✅ 완료: Railway가 제공하는 퍼블릭 URL을 통해 서비스 접속 가능. |
| README에 접속 URL 명시 (Level 1) | ✅ 완료 아래에 접속 URL 명시. |
| Level 2: HTTPS 적용 (10점) | ✅ 충족: Railway PaaS 환경을 활용하여 플랫폼에서 자동으로 SSL/TLS 인증서를 발급받아 접속 시 HTTPS를 제공함. |
| Level 2: PM2 또는 systemd로 프로세스 관리 | △ 간접 충족:Railway는 내부적으로 프로세스 관리 기능을 제공하며, 서버 실행 시 `gunicorn` 프로세스를 사용하여 관리함. |

  * 서비스 URL (24시간 작동):* https://web-production-79b14.up.railway.app/ 

로컬 개발 서버 실행 방법

1.  저장소 복제: `git clone [GitHub URL]`
2.  의존성 설치: `pip install -r requirements.txt`
3.  서버 실행: `python main.py` 또는 `gunicorn --bind 0.0.0.0:8000 main:app`


**이 내용을 `README.md` 파일에 복사하여 Railway 주소만 채워 넣으신 후, GitHub에 최종 푸시하시면 됩니다.**
