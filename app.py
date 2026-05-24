import streamlit as st
import numpy as np
import pandas as pd

# --- 核心计算逻辑 ---
def calculate_tensile_strength(a, b, c):
    """只计算抗拉强度的公式"""
    ts = (67.64 + 1.46 * a - 0.8463 * b - 4.8 * c + 
          0.555 * a * b - 0.8225 * a * c - 0.1725 * b * c - 
          4.24 * (a ** 2) - 2.66 * (b ** 2) - 1.63 * (c ** 2))
    return ts

# --- 蒙特卡洛多解搜索算法 ---
def find_multiple_solutions(target_ts, tolerance, num_samples=50000):
    """
    在指定范围内随机生成大量样本，筛选出符合目标的组合
    """
    # 1. 在指定的绝对范围内生成随机样本
    a_samples = np.random.uniform(0.1, 0.3, num_samples)
    b_samples = np.random.uniform(1.0, 3.0, num_samples)
    c_samples = np.random.uniform(0.0, 90.0, num_samples)
    
    # 2. 批量计算所有样本的抗拉强度 (利用 numpy 的向量化计算，速度极快)
    ts_values = calculate_tensile_strength(a_samples, b_samples, c_samples)
    
    # 3. 筛选出与目标值误差在“容差 (tolerance)”范围内的结果
    # 因为浮点数很难绝对等于目标值，所以我们允许一定的误差，比如目标是100，容差是0.5，那么99.5到100.5都算合格
    valid_indices = np.where(np.abs(ts_values - target_ts) <= tolerance)[0]
    
    # 4. 整理结果为 DataFrame 表格
    results = []
    for idx in valid_indices:
        results.append({
            "A (层厚/mm)": a_samples[idx],
            "B (比例)": b_samples[idx],
            "C (角度/°)": c_samples[idx],
            "实际计算抗拉强度": ts_values[idx],
            "误差绝对值": abs(ts_values[idx] - target_ts)
        })
        
    df = pd.DataFrame(results)
    # 如果有结果，按误差从小到大排序，把最接近的排在最前面
    if not df.empty:
        df = df.sort_values(by="误差绝对值").reset_index(drop=True)
    return df

# --- 网页界面布局 ---
st.set_page_config(page_title="材料力学性能工具", page_icon="🧪", layout="wide")
st.title("🧪 材料参数设计与反推系统")

# 创建标签页
tab1, tab2 = st.tabs(["🎯 抗拉强度多解反推 (指定范围)", "➡️ 常规正向计算"])

# --- 标签页 1：抗拉强度多解反推 ---
with tab1:
    st.header("输入单一目标，探索多种参数组合")
    st.markdown("系统将在您限定的参数边界内 (A: 0.1~0.3, B: 1~3, C: 0~90)，为您寻找满足抗拉强度的所有可行解。")
    
    col1, col2 = st.columns(2)
    with col1:
        target_ts = st.number_input("请输入您期望的 **抗拉强度 (Tensile)** 目标值：", value=50.0)
    with col2:
        # 设置容差，避免条件过于严苛导致无解
        tolerance = st.number_input("允许的误差范围 (容差)：", value=0.5, step=0.1, help="例如设置目标为50，容差0.5，则算出49.5~50.5之间的解都会被展示出来。")
        
    if st.button("开始全量搜索", type="primary"):
        with st.spinner("正在遍历参数空间..."):
            # 执行搜索，默认生成 10万个 随机组合进行筛选
            result_df = find_multiple_solutions(target_ts, tolerance, num_samples=100000)
            
            if result_df.empty:
                st.warning(f"⚠️ 搜索完成，但在设定的范围内未能找到抗拉强度在 {target_ts - tolerance} 到 {target_ts + tolerance} 之间的组合。\n\n建议尝试：调整目标值，或放大误差范围。")
            else:
                st.success(f"✅ 搜索成功！为您找到了 **{len(result_df)}** 组满足条件的工艺参数搭配。")
                st.info("💡 提示：表格已按照**误差从小到大**排序。您可以点击列表头进行重新排序，或者点击右上角下载数据。")
                
                # 在网页上展示美观的数据表格
                st.dataframe(
                    result_df.style.format({
                        "A (层厚/mm)": "{:.4f}",
                        "B (比例)": "{:.4f}",
                        "C (角度/°)": "{:.2f}",
                        "实际计算抗拉强度": "{:.4f}",
                        "误差绝对值": "{:.4f}"
                    }),
                    use_container_width=True,
                    height=400
                )

# --- 标签页 2：正向计算 ---
with tab2:
    st.header("手动输入验证")
    col3, col4, col5 = st.columns(3)
    with col3:
        a_input = st.number_input("A (层厚/mm)", value=0.2, format="%f")
    with col4:
        b_input = st.number_input("B (比例)", value=2.0, format="%f")
    with col5:
        c_input = st.number_input("C (角度/°)", value=45.0, format="%f")
        
    if st.button("计算该组合抗拉强度"):
        ts = calculate_tensile_strength(a_input, b_input, c_input)
        st.metric(label="计算结果：抗拉强度 (Tensile)", value=f"{ts:.4f}")
