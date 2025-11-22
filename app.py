# app.py (main.py와 같은 위치에 생성)

# 1. Flask 및 웹 요청 관련 도구 임포트
from flask import Flask, request, jsonify
from datetime import date

# 2. main.py에서 했던 것처럼 모든 리포지토리와 서비스 임포트
from src.models.common import UserRole
from src.exceptions.custom_exceptions import ValidationError
from src.repositories.memory_repository import (InMemoryUserRepository,
                                                InMemoryCaravanRepository,
                                                InMemoryReservationRepository,
                                                InMemoryPaymentRepository,
                                                InMemoryReviewRepository)
from src.services.user_service import UserService
from src.services.caravan_service import CaravanService
# ... (Reservation, Payment, Review 서비스도 모두 임포트) ...

# 3. Flask 앱 인스턴스 생성
app = Flask(__name__)

# === 4. [DI] 모든 의존성 주입 (main.py의 DI 부분을 그대로 가져옴) ===
# (이 객체들은 서버가 실행되는 동안 메모리에 계속 상주합니다)
user_repo = InMemoryUserRepository()
caravan_repo = InMemoryCaravanRepository()
# ... (다른 리포지토리들도 생성) ...

user_service = UserService(user_repo=user_repo)
caravan_service = CaravanService(caravan_repo=caravan_repo)
# ... (다른 서비스들도 생성) ...

# === 5. API 엔드포인트(라우트) 생성 ===


@app.route("/")
def hello_world():
    """서버가 살아있는지 확인하는 기본 페이지"""
    return "🚐 CaravanShare API 서버가 실행 중입니다!"


@app.route("/users/register", methods=["POST"])
def register_user_route():
    """
    [MVP 1-1] 사용자 회원가입 API
    POST /users/register

    요청 JSON 예시:
    {
        "username": "NewGuest",
        "role": "GUEST" 
    }
    """
    try:
        # 1. 웹(JSON)으로부터 데이터를 받음
        data = request.get_json()

        username = data.get("username")
        role_str = data.get("role")

        # 2. 입력값 검증
        if not username or not role_str:
            raise ValidationError("username과 role은 필수입니다.")

        # 3. 문자열을 UserRole Enum으로 변환
        try:
            role = UserRole[role_str.upper()]
        except KeyError:
            raise ValidationError("role은 HOST 또는 GUEST여야 합니다.")

        # 4. 핵심 로직 실행 (우리가 만든 UserService 호출)
        user = user_service.register_user(username=username, role=role)

        # 5. 성공 응답 반환 (JSON)
        # (주의: user 객체는 dataclass라 바로 JSON이 안될 수 있음. 여기서는 간단히 dict로 변환)
        response_data = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.name
        }
        return jsonify(response_data), 201  # 201: '생성됨' 상태 코드

    except ValidationError as e:
        # 6. 비즈니스 로직 에러 처리 (예: 중복 아이디)
        return jsonify({"error": e.message}), 400  # 400: '잘못된 요청' 상태 코드
    except Exception as e:
        # 7. 기타 서버 에러 처리
        return jsonify({"error": "서버 내부 오류", "details": str(e)}), 500


# === 6. 서버 실행 ===
if __name__ == "__main__":
    # 'python app.py'로 직접 실행할 경우,
    # debug=True 모드로 실행 (코드가 변경되면 서버가 자동 재시작됨)
    app.run(debug=True, port=5000)

    # app.py 파일 맨 아래, app.run()의 바로 위에 추가하세요.


@app.route("/caravans/search", methods=["GET"])
def search_caravans_route():
    """
    [MVP 1-2] 카라반 검색 API
    GET /caravans/search?capacity=3&user=GuestName

    요청 쿼리 스트링 예시:
    ?capacity=3
    ?capacity=3&user_id=... (실제로는 인증된 유저 ID를 사용해야 함)
    """
    try:
        # 1. 웹(Query String)으로부터 데이터를 받음
        # ❗️ GET 요청은 request.args['key']를 사용합니다.
        capacity_str = request.args.get("capacity")

        # ❗️(임시) 실제로는 인증 시스템에서 유저 ID를 가져와야 하지만,
        # ❗️ 여기서는 쿼리 스트링에서 유저 이름을 받아 임시 유저 객체를 만듭니다.
        username = request.args.get("user")
        if not username:
            raise ValidationError("테스트를 위해 user 이름을 쿼리 파라미터로 보내주세요.")

        # 임시 게스트 객체 (UserService에서 찾지 않고 바로 생성)
        temp_guest = User(username=username, role=UserRole.GUEST)

        # 2. 입력값 검증
        if not capacity_str:
            raise ValidationError("capacity 쿼리 파라미터는 필수입니다.")

        min_capacity = int(capacity_str)

        # 3. 핵심 로직 실행 (CaravanService 호출)
        caravans = caravan_service.search_caravans(guest=temp_guest,
                                                   min_capacity=min_capacity)

        # 4. 성공 응답 반환 (JSON)
        # (dataclass 리스트를 dict 리스트로 변환)
        from dataclasses import asdict
        response_data = [asdict(caravan) for caravan in caravans]

        return jsonify(response_data), 200  # 200: 'OK'

    except (ValidationError, ValueError) as e:  # ValueError (int 변환 실패)
        # 5. 비즈니스 로직 에러 처리
        return jsonify({"error": str(e)}), 400  # 400: '잘못된 요청'
    except Exception as e:
        # 6. 기타 서버 에러 처리
        return jsonify({"error": "서버 내부 오류", "details": str(e)}), 500


# app.py 파일의 맨 마지막에 이 코드를 추가하세요.

# === 6. 서버 실행 ===
if __name__ == "__main__":
    # Replit이 Preview를 띄울 수 있도록 host='0.0.0.0'으로 설정합니다.
    app.run(host='0.0.0.0', port=5000, debug=True)
