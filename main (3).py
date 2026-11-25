#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI MVP version of the custom robot builder game (emoji-based status output).
- 3DOF planar arm model (base at (0,0))
- Easy/Medium/Hard difficulty mapping via Korean labels (상/중/하)
- No GUI dependencies; runs in a terminal
- Includes a tiny AI assistant with credit-based hints
"""
import math
import time
import random

# ---------- 로봇 모델 (3DOF 팔 + 베이스) ----------
class Robot3DOF:
    def __init__(self):
        self.base = (0.0, 0.0)
        self.l1 = 120.0
        self.l2 = 90.0
        self.l3 = 60.0
        self.theta1 = math.radians(60.0)
        self.theta2 = math.radians(-25.0)
        self.theta3 = 0.0
        self.energy = 0.0
        self.picked = False
        self.phi_target = 0.0  # 끝단 방향

    def forward(self):
        x0, y0 = self.base
        x1 = x0 + self.l1 * math.cos(self.theta1)
        y1 = y0 - self.l1 * math.sin(self.theta1)
        x2 = x1 + self.l2 * math.cos(self.theta1 + self.theta2)
        y2 = y1 - self.l2 * math.sin(self.theta1 + self.theta2)
        x3 = x2 + self.l3 * math.cos(self.theta1 + self.theta2 + self.theta3)
        y3 = y2 - self.l3 * math.sin(self.theta1 + self.theta2 + self.theta3)
        return (x0, y0), (x1, y1), (x2, y2), (x3, y3)

    def ik_solve(self, target):
        # target: (x,y) relative to base
        x, y = target
        # inverse kinematics (elbow-down, 2DOF for base + shoulder, then theta3 to align end effector)
        L1, L2, L3 = self.l1, self.l2, self.l3
        d = math.hypot(x, y)
        if d > (L1 + L2 + L3) or d < abs(L1 - L2 - L3):
            return None, None, None
        cos2 = (x*x + y*y - L1*L1 - L2*L2) / (2 * L1 * L2)
        cos2 = max(-1.0, min(1.0, cos2))
        sin2 = math.sqrt(max(0.0, 1.0 - cos2*cos2))
        theta2 = math.atan2(sin2, cos2)
        k1 = L1 + L2 * cos2
        k2 = L2 * sin2
        theta1 = math.atan2(y, x) - math.atan2(k2, k1)
        # 마지막 관절(theta3)으로 end-effector 방향(phi_target) 맞춤
        theta3 = self.phi_target - (theta1 + theta2)
        return theta1, theta2, theta3

    def set_angles(self, t1, t2, t3):
        delta1 = abs(t1 - self.theta1)
        delta2 = abs(t2 - self.theta2)
        delta3 = abs(t3 - self.theta3)
        self.energy += (delta1 + delta2 + delta3) * 2.0
        self.theta1 = t1
        self.theta2 = t2
        self.theta3 = t3

    def reset(self):
        self.theta1 = math.radians(60.0)
        self.theta2 = math.radians(-25.0)
        self.theta3 = 0.0
        self.energy = 0.0
        self.picked = False
        self.phi_target = 0.0

# ---------- 유틸 ----------
DIFF_KR = ["상", "중", "하"]  # UI 표기
DIFF_INTERNAL = {"상": "Hard", "중": "Medium", "하": "Easy"}

def clamp(v, a, b):
    return max(a, min(b, v))

def approach_angle(current, target, step):
    diff = target - current
    # -pi..pi 보정
    while diff > math.pi:
        diff -= 2*math.pi
    while diff < -math.pi:
        diff += 2*math.pi
    delta = max(-step, min(step, diff))
    return current + delta

# ---------- AI 어시스턴트 (간단한 크레딧 힌트) ----------
class SimpleAIAssistant:
    def __init__(self, initial_credits=2):
        self.credits = initial_credits
        self.memory = {}

    def provide_hint(self, difficulty):
        if self.credits < 1:
            return "크레딧이 부족합니다. 의뢰를 성공시키면 AI 크레딧이 증가합니다."
        self.credits -= 1
        if difficulty == "Easy":
            return "힌트: 목표 좌표를 먼저 정하고, 엔드 이펙터 방향(phi_target)을 간단히 정해보세요."
        elif difficulty == "Medium":
            return "힌트: 모듈 인터페이스를 정리하고, 피킹/배출 루프를 명확히 하세요."
        else:
            return "힌트: 의도 추론을 돕기 위해, 좌표 대신 간단한 목표 목록으로 시도해보세요."

    def earn(self, amount=2):
        self.credits += amount

# ---------- 메인(CLI) ----------
def print_status(robot, target_pos, credits, ai):
    (bx, by), (x1, y1), (x2, y2), (xe, ye) = robot.forward()
    # 간단한 상태 라인에 이모티콘 출력
    print(f"상태: 🟢 대기 | L1={robot.l1:.1f}, L2={robot.l2:.1f}, L3={robot.l3:.1f} | θ1={math.degrees(robot.theta1):.1f}°, θ2={math.degrees(robot.theta2):.1f}°, θ3={math.degrees(robot.theta3):.1f}° | end=({xe:.1f},{ye:.1f})")
    print(f"타깃: {target_pos}  크레딧: {credits}  AI 크레딧: {ai.credits}")
    print("------------------------------")

def main():
    robot = Robot3DOF()
    target = (180.0, 0.0)  # 2D 타깃 좌표
    ai = SimpleAIAssistant(initial_credits=2)
    difficulty_label = "하"  # 기본 Easy/중/상 매핑: 하=Easy, 중=Medium, 상=Hard
    internal = DIFF_INTERNAL["하"]  # Easy

    print("로봇 제작 CLI MVP 시작 🧰🤖")
    print("난이도 선택: 상/중/하 (UI 로 표시되듯이 작동) - 기본은 하(Easy)로 시작합니다")
    print("명령어: length, phi, target, start, ai, status, reset, diff, exit")
    print("예: length 140 100 60 / phi 15 / target 120 40 / start")
    print("현재 난이도: 하(Easy)")

    while True:
        cmd = input("> ").strip()
        if not cmd:
            continue
        parts = cmd.split()
        key = parts[0].lower()
        if key == 'length' and len(parts) == 4:
            try:
                robot.l1 = float(parts[1]); robot.l2 = float(parts[2]); robot.l3 = float(parts[3])
                print("팔 길이가 설정되었습니다.")
            except:
                print("잘못된 값입니다. 예: length 120 90 60")
        elif key == 'phi' and len(parts) == 2:
            try:
                deg = float(parts[1]); robot.phi_target = math.radians(deg)
                print(f"End-effector 방향을 {deg}°로 설정했습니다.")
            except:
                print("잘못된 각도입니다. 예: phi 30")
        elif key == 'target' and len(parts) == 3:
            try:
                tx = float(parts[1]); ty = float(parts[2]); target = (tx, ty)
                print(f"타깃 좌표를 {target}으로 설정했습니다.")
            except:
                print("타깃 좌표는 숫자로 입력해주세요. 예: target 120 40")
        elif key == 'start':
            # 간단한 시뮬레이션 루프
            print("시뮬레이션 시작 🟢")
            steps = 0
            while steps < 200:
                steps += 1
                # IK로 타깃 도달 여부 계산
                t1, t2, t3 = robot.ik_solve((target[0] - robot.base[0], target[1] - robot.base[1]))
                if t1 is None:
                    # 도달 불가 -> 조금 보정
                    robot.theta1 += math.radians(2)
                    robot.theta2 += math.radians(-1)
                    robot.theta3 += math.radians(0.5)
                else:
                    new_t1 = approach_angle(robot.theta1, t1, 0.15)
                    new_t2 = approach_angle(robot.theta2, t2, 0.15)
                    new_t3 = approach_angle(robot.theta3, t3, 0.15)
                    robot.set_angles(new_t1, new_t2, new_t3)

                    # End effector position 추정
                    (b0,b1,b2,be) = robot.forward()
                    dist = math.hypot(be[0] - target[0], be[1] - target[1])
                    if dist < 12:
                        robot.picked = True
                        print("피킹 성공! 목표 도달")
                        break
                print_status(robot, target, 0, ai)
                time.sleep(0.05)
            if not robot.picked:
                print("시뮬레이션 끝. 목표에 도달하지 못했습니다.")
            # 완료 후 보상/에너지 출력
            print_status(robot, target, 0, ai)
        elif key == 'ai':
            hint = ai.provide_hint(internal)
            print(f"AI 힌트: {hint} (크레딧 남음: {ai.credits})")
        elif key == 'status':
            print_status(robot, target, 0, ai)
        elif key == 'reset':
            robot.reset()
            print("로봇 초기화 완료")
        elif key == 'diff':
            # 단순히 난이도를 상/중/하로 바꿉니다
            if internal == 'Easy':
                internal = 'Medium'
                difficulty_label = '중'
            elif internal == 'Medium':
                internal = 'Hard'
                difficulty_label = '상'
            else:
                internal = 'Easy'
                difficulty_label = '하'
            print(f"난이도 변경: {difficulty_label}")
        elif key == 'exit' or key == 'quit':
            print("프로그램 종료합니다.")
            break
        else:
            print("알 수 없는 명령어입니다. 예: start, ai, diff")

if __name__ == '__main__':
    main()
