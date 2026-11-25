import streamlit as st
import matplotlib.pyplot as plt
from robot_core.robot import Robot3DOF
import numpy as np
import math

# Simple drawing helper
def draw_robot(robot):
    (b0, b1, b2, be) = robot.forward()
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.set_xlim(-500, 500)
    ax.set_ylim(-500, 500)
    ax.axis('off')
    # bones
    ax.plot([b0[0], b1[0]], [b0[1], b1[1]], 'b-', lw=4)
    ax.plot([b1[0], b2[0]], [b1[1], b2[1]], 'b-', lw=4)
    ax.plot([b2[0], be[0]], [b2[1], be[1]], 'b-', lw=4)
    ax.scatter(be[0], be[1], color='red', s=40)
    return fig

def main():
    st.set_page_config(page_title="Custom Robot Builder - Streamlit MVP", layout="wide")
    st.title("Custom Robot Builder - Streamlit MVP")

    with st.sidebar:
        diff = st.selectbox("난이도", ["상 Hard", "중 Medium", "하 Easy"], index=2)
        # internal difficulty mapping
        diff_map = {"상 Hard": "Hard", "중 Medium": "Medium", "하 Easy": "Easy"}
        internal = diff_map[diff]
        st.markdown("---")
        st.subheader("팔 파라미터")
        l1 = st.slider("L1", 60, 200, 120)
        l2 = st.slider("L2", 60, 200, 90)
        l3 = st.slider("L3", 40, 140, 60)
        phi_deg = st.slider("End-effector 방향 φ (deg)", -180, 180, 0)
        ai_credits = st.number_input("AI 크레딧", min_value=0, value=2, step=1)

    # 로봇 인스턴스 생성
    robot = Robot3DOF(l1=l1, l2=l2, l3=l3, phi_target=math.radians(phi_deg))
    # 간단한 시뮬레이션 썸네일 그림
    fig = draw_robot(robot)
    st.pyplot(fig)

    # 현재 엔드 이펙터 좌표와 상태 텍스트
    end = robot.forward()[-1]
    st.write(f"엔드 이펙터 좌표: {end}")
    st.write(f"난이도(내부): {internal} / UI: {diff}")

    if st.button("AI 힌트 받기 (1 크레딧)"):
        if ai_credits < 1:
            st.warning("AI 크레딧이 부족합니다.")
        else:
            st.success("힌트: 의도 추론과 파라미터 선택의 균형이 중요합니다.")

if __name__ == "__main__":
    main()
