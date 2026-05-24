import streamlit as st
import numpy as np
import pandas as pd

# --- 核心计算逻辑 (包含三个完整公式) ---
def calculate_properties(a, b, c):
    """正向计算：输入 A, B, C，同时得出三个性能"""
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

# --- 蒙特卡洛多解搜索算法 ---
def find_multiple_solutions(target_type, target_value, tolerance, num_samples=100000):
    """
    在指定范围内随机生成大量样本，根据用户选择的“核心目标”，筛选出符合条件的组合。
    """
    # 1. 在指定的工艺范围内生成随机样本 (A: 0.1~0.3, B: 1~3, C: 0~90)
    a_samples = np.random.uniform(0.1, 0.3, num_samples)
    b_samples = np.random.uniform(1.0, 3.0, num_samples)
    c_samples = np.random.uniform(0.0, 90.0, num_samples)
    
    # 2. 批量计算所有样本的三个性能指标 (使用 numpy 向量化计算，极速处理十万条数据)
    ts_values, fs_values, ilss_values = calculate_properties(a_samples, b_samples, c_samples)
    
    # 3. 根据用户选择的单一目标，锁定误差数组
    if target_type == "抗拉强度 (Tensile)":
        errors = np.abs(ts_values - target_value)
    elif target_type == "弯曲强度 (Flexural)":
        errors = np.abs(fs_values - target_value)
    else: # ILSS
        errors = np.abs(ilss_values - target_value)
        
    # 4. 筛选出误差在“容差 (tolerance)”范围内的合格索引
    valid_indices = np.where(errors <= tolerance)[0]
    
    # 5. 将合格的数据整理成表格
    results = []
    for idx in valid_indices:
        results.append({
            "A (层厚/mm)": a_samples[idx],
            "B (比例)": b_samples[idx],
            "C (角度/°)": c_samples[idx],
            "抗拉强度计算值": ts_values[idx],
            "弯曲强度计算值": fs_values[idx],
            "ILSS计算值": ilss_values[idx],
            "目标误差绝对值": errors[idx]
        })
        
    df = pd.DataFrame(results)
    # 按目标误差从小到大排序
    if not df.empty:
        df = df.sort_values(by="目标误差绝对值").reset_index(drop=True)
    return df

# --- 网页界面布局 ---
st.set_page_config(page_title="材料力学性能工具", page_icon="🧪", layout="wide")
st.title("🧪 材料参数设计与反推系统")

tab1, tab2 = st.tabs(["➡️ 正向计算 (成分 -> 性能)", "🎯 单指标反推多组解 (指定范围)"])

# --- 标签页 1：正向计算 ---
with tab1:
    st.header("手动输入验证")
    st.markdown("输入 A、B、C，系统将直接计算出三种强度的预测值。")
    col1, col2, col3 = st.columns(3)
    with col1:
        a_input = st.number_input("A (层厚/mm) ", value=0.2, format="%f")
    with col2:
        b_input = st.number_input("B (比例) ", value=2.0, format="%f")
    with col3:
        c_input = st.number_input("C (角度/°) ", value=45.0, format="%f")
        
    if st.button("计算全部力学性能", type="primary"):
        ts, fs, ilss = calculate_properties(a_input, b_input, c_input)
        st.success("✅ 计算完成！")
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric(label="抗拉强度 (Tensile)", value=f"{ts:.4f}")
        res_col2.metric(label="弯曲强度 (Flexural)", value=f"{fs:.4f}")
        res_col3.metric(label="层间剪切强度 (ILSS)", value=f"{ilss:.4f}")

# --- 标签页 2：单指标反推多解 ---
with tab2:
    st.header("输入单一目标，探索多种参数组合")
    st.markdown("系统将在您限定的参数边界内 (A: 0.1~0.3, B: 1~3, C: 0~90)，为您寻找满足指定目标的**所有可行解**。")
    
    # 核心升级：让用户选择目标类型
    target_type = st.selectbox(
        "1. 请选择您要设定的目标性能：",
        ["抗拉强度 (Tensile)", "弯曲强度 (Flexural)", "层间剪切强度 (ILSS)"]
    )
    
    col4, col5 = st.columns(2)
    with col4:
        target_value = st.number_input(f"2. 请输入期望的 {target_type} 值：", value=50.0)
    with col5:
        tolerance = st.number_input("3. 允许的误差范围 (容差)：", value=0.5, step=0.1)
        
    if st.button("🚀 开始全量搜索", type="primary"):
        with st.spinner("正在遍历十万种参数组合..."):
            # 执行搜索
            result_df = find_multiple_solutions(target_type, target_value, tolerance, num_samples=100000)
            
            if result_df.empty:
                st.warning(f"⚠️ 搜索完成，但在工艺范围内未能找到目标值在 {target_value - tolerance} 到 {target_value + tolerance} 之间的组合。\n\n建议尝试：调整目标值，或稍微放大容差范围。")
            else:
                st.success(f"✅ 搜索成功！为您找到了 **{len(result_df)}** 组满足 {target_type} 目标的工艺参数。")
                st.info("💡 提示：表格已按照目标误差从小到大排序。系统同时计算了另外两种性能供您参考。您可以点击右上角下载完整数据表。")
                
                # 美化表格输出，高亮目标列
                st.dataframe(
                    result_df.style.format({
                        "A (层厚/mm)": "{:.4f}",
                        "B (比例)": "{:.4f}",
                        "C (角度/°)": "{:.2f}",
                        "抗拉强度计算值": "{:.4f}",
                        "弯曲强度计算值": "{:.4f}",
                        "ILSS计算值": "{:.4f}",
                        "目标误差绝对值": "{:.4f}"
                    }),
                    use_container_width=True,
                    height=450
                )
