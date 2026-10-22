import os
from flask import Flask, request, jsonify

app = Flask(__name__)

class FixedSizeQueue:
    """
    고정 크기를 가지는 원형 큐(Circular Queue) 구현 클래스
    
    속성:
        capacity (int): 큐의 최대 저장 용량
        queue (list): 고정 크기 데이터 배열
        front (int): 가장 먼저 들어온 데이터의 인덱스 (출력 위치)
        rear (int): 마지막으로 들어간 데이터의 다음 인덱스 (삽입 위치)
        count (int): 현재 저장된 데이터 개수
    """
    def __init__(self, capacity: int = 5):
        # 1) 초기화
        self.capacity = max(1, int(capacity))
        self.queue = [None] * self.capacity
        self.front = 0
        self.rear = 0
        self.count = 0

    # 4) 상태 검사 (is_full, is_empty)
    def is_full(self) -> bool:
        """큐가 가득 찼는지 검사"""
        return self.count == self.capacity

    def is_empty(self) -> bool:
        """큐가 비어있는지 검사"""
        return self.count == 0

    # 2) push 와 pop
    def push(self, value) -> bool:
        """큐의 rear 위치에 데이터를 삽입"""
        if self.is_full():
            return False  # 큐가 가득 탐 (Overflow)
        
        self.queue[self.rear] = value
        self.rear = (self.rear + 1) % self.capacity  # 원형 회전
        self.count += 1
        return True

    def pop():
        """큐의 front 위치에서 데이터를 꺼내고 제거"""
        if self.is_empty():
            return None  # 큐가 빔 (Underflow)
        
        val = self.queue[self.front]
        self.queue[self.front] = None  # 삭제 처리 표시
        self.front = (self.front + 1) % self.capacity  # 원형 회전
        self.count -= 1
        return val

    # 3) 현재 데이터 개수 반환
    def size(self) -> int:
        """현재 저장된 데이터 개수(길이/크기) 반환"""
        return self.count

    # 5) 전면(Front) 데이터 확인
    def peek(self):
        """가장 앞(Front)의 데이터를 삭제하지 않고 확인"""
        if self.is_empty():
            return None
        return self.queue[self.front]

    # 6) 큐 전체 데이터 삭제
    def clear(self):
        """큐의 모든 데이터를 삭제하고 인덱스 및 개수를 초기화"""
        self.queue = [None] * self.capacity
        self.front = 0
        self.rear = 0
        self.count = 0

    # 7) 값의 index 검색
    def search_index(self, value) -> int:
        """
        특정 값이 존재할 경우 논리적 순서상 인덱스(0부터 시작) 반환
        찾지 못할 경우 -1 반환
        """
        if self.is_empty():
            return -1
        
        for i in range(self.count):
            actual_idx = (self.front + i) % self.capacity
            if self.queue[actual_idx] == value:
                return i  # 논리적 인덱스 반환
        return -1

    # 8) 값의 개수(길이/크기) - 특정 값이 몇 번 존재하는지 카운트
    def count_value(self, value) -> int:
        """큐 내에 특정 값이 포함된 개수 카운트"""
        cnt = 0
        for i in range(self.count):
            actual_idx = (self.front + i) % self.capacity
            if self.queue[actual_idx] == value:
                cnt += 1
        return cnt

    # 9) 값의 존재 여부 검사
    def contains(self, value) -> bool:
        """특정 값이 큐 안에 존재하는지 여부 반환"""
        return self.search_index(value) != -1

    # 10) Front 부터 Rear 까지 출력
    def get_front_to_rear(self) -> list:
        """Front부터 Rear 논리적 순서대로 실제 들어있는 데이터 리스트 반환"""
        result = []
        for i in range(self.count):
            actual_idx = (self.front + i) % self.capacity
            result.append(self.queue[actual_idx])
        return result

    # 11) 배열 전체를 출력
    def get_raw_array(self) -> list:
        """물리적 전체 배열 상태(None 포함) 반환"""
        return list(self.queue)

    def get_state(self) -> dict:
        """큐의 전체 상태 객체 반환"""
        return {
            "capacity": self.capacity,
            "count": self.count,
            "front": self.front,
            "rear": self.rear,
            "is_full": self.is_full(),
            "is_empty": self.is_empty(),
            "front_value": self.peek(),
            "active_elements": self.get_front_to_rear(),
            "raw_array": self.get_raw_array()
        }


# 전역 큐 인스턴스 (기본 용량: 5)
global_queue = FixedSizeQueue(capacity=5)


# STREAMING_CHUNK:Configuring Flask endpoints and request router...
@app.route('/api/queue', methods=['POST'])
def queue_controller():
    """
    클라우드 런 API 단일 통로 핸들러
    JSON 요청 구조:
    {
        "action": "init" | "push" | "pop" | "peek" | "clear" | "search" | "count" | "contains" | "status",
        "value": 검색/삽입 데이터 (선택),
        "capacity": 초기화 용량 (선택)
    }
    """
    global global_queue
    data = request.get_json() or {}
    action = data.get('action', 'status')
    val = data.get('value')
    
    response = {
        "success": True,
        "message": "",
        "action": action,
        "result": None
    }

    try:
        # 1) 초기화
        if action == "init":
            cap = int(data.get('capacity', 5))
            global_queue = FixedSizeQueue(capacity=cap)
            response["message"] = f"용량 {cap}으로 고정 길이 큐가 초기화되었습니다."

        # 2) push
        elif action == "push":
            if val is None or val == "":
                response["success"] = False
                response["message"] = "삽입할 값을 입력해주세요."
            else:
                success = global_queue.push(val)
                if success:
                    response["message"] = f"값 '{val}'이(가) 성공적으로 Push 되었습니다."
                else:
                    response["success"] = False
                    response["message"] = f"큐가 가득 차서 값 '{val}'을(를) Push할 수 없습니다. (Overflow)"

        # 2) pop
        elif action == "pop":
            popped_val = global_queue.pop()
            if popped_val is not None:
                response["result"] = popped_val
                response["message"] = f"값 '{popped_val}'이(가) Pop 되었습니다."
            else:
                response["success"] = False
                response["message"] = "큐가 비어있어 Pop할 데이터가 없습니다. (Underflow)"

        # 5) 전면(Front) 데이터 확인
        elif action == "peek":
            front_val = global_queue.peek()
            response["result"] = front_val
            response["message"] = f"Front 데이터 확인: {front_val}" if front_val is not None else "큐가 비어있습니다."

        # 6) 큐 전체 데이터 삭제
        elif action == "clear":
            global_queue.clear()
            response["message"] = "큐 전체 데이터가 삭제되었습니다."

        # 7) 값의 index 검색
        elif action == "search":
            idx = global_queue.search_index(val)
            response["result"] = idx
            if idx != -1:
                response["message"] = f"값 '{val}'의 논리적 순서 인덱스는 {idx}입니다."
            else:
                response["message"] = f"값 '{val}'을(를) 큐에서 찾을 수 없습니다."

        # 8) 값의 개수(길이/크기)
        elif action == "count":
            cnt = global_queue.count_value(val)
            response["result"] = cnt
            response["message"] = f"값 '{val}'의 존재 개수: {cnt}개"

        # 9) 값의 존재 여부 검사
        elif action == "contains":
            exists = global_queue.contains(val)
            response["result"] = exists
            response["message"] = f"값 '{val}' 존재 여부: {'존재함' if exists else '존재하지 않음'}"

        # 기타: 상태 조회
        elif action == "status":
            response["message"] = "현재 큐 상태를 조회했습니다."

        else:
            response["success"] = False
            response["message"] = f"알 수 없는 동작(action): {action}"

    except Exception as e:
        response["success"] = False
        response["message"] = f"서버 오류 발생: {str(e)}"

    # 항상 현재 큐의 전체 상태를 함께 응답으로 전송
    response["state"] = global_queue.get_state()
    return jsonify(response), 200


if __name__ == '__main__':
    # Cloud Run은 PORT 환경변수를 제공
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
def pop(self):
        """
        [2-2] Pop 연산: 큐의 맨 앞(Front)에서 요소 제거 및 반환
        시간 복잡도: O(1)
        """
        if self.is_empty():
            return None, "Queue Underflow: 큐가 비어 있습니다."
        
        item = self.queue[self.front]
        self.queue[self.front] = None  # 데이터 초기화
        self.front = (self.front + 1) % self.capacity
        self.size -= 1
        return item, f"성공적으로 '{item}' 값을 pop 했습니다."

# 전역 큐 인스턴스 (기본 용량: 5)
        elif action == 'pop':
            # pop 연산은 별도의 value 매개변수가 필요하지 않음
            result, msg = global_queue.pop()
            return jsonify({
                "status": "success" if result is not None else "error",
                "action": action,
                "result": result,
                "message": msg,
                "queue_state": global_queue.get_all_elements()
            }), 200



@app.route('/', methods=['GET'])
def home():
    """서버 작동 상태 확인용 기본 루트 엔드포인트"""
    return jsonify({
        "status": "online",
        "message": "Fixed-Size Queue Cloud Run API Server is running.",
        "endpoint": "/api/queue"
    }), 200


@app.route('/api/queue', methods=['POST'])
def queue_controller():
