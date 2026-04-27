import streamlit as st
import numpy as np
from scipy.optimize import fsolve

# --- 核心计算逻辑 ---
def calculate_properties(a, b, c):
    ts = (67.64 + 1.46 * a - 0.8463 * b - 4.8 * c + 
          0.555 * a * b - 0.8225 * a * c - 0.1725 * b * c - 
          4.24 * (a ** 2) - 2.66 * (b ** 2) - 1.63 * (c ** 2))
    
    fs = (110.39 - 4.77 * a + 1.22 * b - 6.41 * c - 
          2.02 * a * b - 10.64 * a * c + 4.83 * b * c - 
          7.63 * (a ** 2) + 2.42 * (b ** 2) + 2.68 * (c ** 2))
    
    ilss = (12.85 - 0.93 * a + 1.62 * b - 0.3975 * c + 
            0.98 * a * b + 2.67 * a * c + 0.12 * b * c - 
            1.38 * (a ** 2) + 0.37 * (b ** 2) + 2.95 * (c ** 2))
    return ts, fs, ilss

def error_equations(vars, target_ts, target_fs, target_ilss):
    a, b, c = vars
    ts, fs, ilss = calculate_properties(a, b, c)
    return [ts - target_ts, fs - target_fs, ilss - target_ilss]

# --- 网页界面布局 ---
st.set_page_config(page_title="材料力学性能工具", page_icon="🧪", layout="centered")
st.title("🧪 材料力学性能综合计算器")
st.markdown("通过输入工艺参数预测力学性能，或根据目标性能反推所需工艺参数。")

# 创建两个标签页
tab1, tab2 = st.tabs(["➡️ 正向计算 (成分 -> 性能)", "⬅️ 逆向反推 (性能 -> 成分)"])

# --- 标签页 1：正向计算 ---
with tab1:
    st.header("输入工艺参数")
    col1, col2, col3 = st.columns(3)
    with col1:
        a_input = st.number_input("A (层厚/mm)", value=1.0, format="%f")
    with col2:
        b_input = st.number_input("B (比例)", value=1.0, format="%f")
    with col3:
        c_input = st.number_input("C (角度/°)", value=0.0, format="%f")
        
    if st.button("计算力学性能", type="primary"):
        ts, fs, ilss = calculate_properties(a_input, b_input, c_input)
        st.success("计算完成！")
        
        # 使用 Metric 组件美观展示结果
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric(label="抗拉强度 (Tensile)", value=f"{ts:.4f}")
        res_col2.metric(label="弯曲强度 (Flexural)", value=f"{fs:.4f}")
        res_col3.metric(label="层间剪切强度 (ILSS)", value=f"{ilss:.4f}")

# --- 标签页 2：逆向反推 ---
with tab2:
    st.header("输入期望性能指标")
    col4, col5, col6 = st.columns(3)
    with col4:
        target_ts = st.number_input("目标 抗拉强度", value=100.0)
    with col5:
        target_fs = st.number_input("目标 弯曲强度", value=100.0)
    with col6:
        target_ilss = st.number_input("目标 ILSS", value=10.0)
        
    if st.button("反推工艺参数", type="primary"):
        initial_guess = [1.0, 1.0, 1.0]
        solution, info, ier, mesg = fsolve(error_equations, initial_guess, 
                                           args=(target_ts, target_fs, target_ilss), 
                                           full_output=True)
        if ier == 1:
            st.success("逆向求解成功！建议的工艺参数如下：")
            sol_col1, sol_col2, sol_col3 = st.columns(3)
            sol_col1.metric(label="推荐 A (层厚)", value=f"{solution[0]:.4f}")
            sol_col2.metric(label="推荐 B (比例)", value=f"{solution[1]:.4f}")
            sol_col3.metric(label="推荐 C (角度)", value=f"{solution[2]:.4f}")
            
            st.info("💡 提示：逆向求解可能存在多组解或由于目标值不合理导致误差。请结合实际工艺经验评估推荐参数。")
        else:
            st.error(f"求解失败：您输入的目标性能组合在物理模型下可能无解。\n\n算法提示：{mesg}")