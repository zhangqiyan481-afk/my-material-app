import streamlit as st
import numpy as np
import pandas as pd
import json
import os

st.set_page_config(page_title="材料力学性能工具", page_icon="🧪", layout="wide")

# ==========================================
# 账号数据存储逻辑 (利用本地 JSON 文件充当轻量级数据库)
# ==========================================
USER_DATA_FILE = "users.json"

def load_users():
    """读取本地的用户数据"""
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    # 如果文件不存在，默认给一个超级管理员账号
    return {"admin": "888888"}

def save_users(users_dict):
    """保存新注册的用户数据到本地"""
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users_dict, f)

# 初始化系统状态
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = ""

# ==========================================
# 登录与注册界面
# ==========================================
if not st.session_state['logged_in']:
    st.title("🔒 欢迎使用材料力学计算系统")
    st.markdown("请登录以访问核心算法引擎。")
    
    # 使用标签页拆分登录和注册功能
    tab_login, tab_register = st.tabs(["🔑 账号登录", "📝 注册新账号"])
    
    # --- 登录模块 ---
    with tab_login:
        login_user = st.text_input("用户名", key="login_user")
        login_pwd = st.text_input("密码", type="password", key="login_pwd")
        
        if st.button("登录", type="primary", use_container_width=True):
            users = load_users()
            if login_user in users and users[login_user] == login_pwd:
                st.session_state['logged_in'] = True
                st.session_state['current_user'] = login_user
                st.rerun() # 刷新进入主界面
            else:
                st.error("用户名不存在或密码错误！")

    # --- 注册模块 ---
    with tab_register:
        reg_user = st.text_input("设置新用户名", key="reg_user")
        reg_pwd = st.text_input("设置密码", type="password", key="reg_pwd")
        reg_pwd_confirm = st.text_input("确认密码", type="password", key="reg_pwd_conf")
        
        if st.button("立即注册", use_container_width=True):
            users = load_users()
            if reg_user in users:
                st.warning("⚠️ 该用户名已被注册，请换一个试试！")
            elif reg_pwd != reg_pwd_confirm:
                st.error("❌ 两次输入的密码不一致！")
            elif len(reg_user) < 3 or len(reg_pwd) < 6:
                st.warning("⚠️ 用户名至少3位，密码至少6位！")
            else:
                # 校验通过，写入“数据库”
                users[reg_user] = reg_pwd
                save_users(users)
                st.success("✅ 注册成功！请切换到【账号登录】页面进行登录。")

# ==========================================
# 核心业务界面 (只有登录后才能看到)
# ==========================================
else:
    # 顶部状态栏：显示当前操作者和退出按钮
    col_user, col_space, col_exit = st.columns([2, 6, 1])
    with col_user:
        st.info(f"👤 当前登录操作员：{st.session_state['current_user']}")
    with col_exit:
        if st.button("退出登录"):
            st.session_state['logged_in'] = False
            st.session_state['current_user'] = ""
            st.rerun()
            
    st.divider() # 画一条分割线
    
    # ----------------------------------------------------
    # 下面直接粘贴您之前写好的那些 tab1, tab2 的核心计算器代码
    # ----------------------------------------------------
    st.title("🧪 材料参数设计与反推系统")
    # ... (此处省略我们之前写好的蒙特卡洛算法、正向反推等代码)
import streamlit as st
import numpy as np
import pandas as pd

# --- 核心计算逻辑 ---
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
    在指定范围内随机生成大量样本，根据用户选择的核心目标，筛选出符合条件的组合。
    """
    # 1. 工艺边界更新：A和B是连续区间，C被严格限制为离散选项
    a_samples = np.random.uniform(0.1, 0.3, num_samples)
    b_samples = np.random.uniform(1.0, 3.0, num_samples)
    # 核心改动：使用 np.random.choice 从列表中随机抽取，而不是 np.random.uniform
    c_samples = np.random.choice([0.0, 45.0, 90.0], size=num_samples)
    
    # 2. 批量计算
    ts_values, fs_values, ilss_values = calculate_properties(a_samples, b_samples, c_samples)
    
    # 3. 锁定目标与误差
    if target_type == "抗拉强度 (Tensile)":
        errors = np.abs(ts_values - target_value)
    elif target_type == "弯曲强度 (Flexural)":
        errors = np.abs(fs_values - target_value)
    else: 
        errors = np.abs(ilss_values - target_value)
        
    # 4. 筛选合格索引
    valid_indices = np.where(errors <= tolerance)[0]
    
    # 5. 整理数据
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
    if not df.empty:
        df = df.sort_values(by="目标误差绝对值").reset_index(drop=True)
    return df

# --- 网页界面布局 ---
st.set_page_config(page_title="材料力学性能工具", page_icon="🧪", layout="wide")
st.title("🧪 材料参数设计与反推系统")

tab1, tab2 = st.tabs(["➡️ 正向计算 (成分 -> 性能)", "🎯 单指标反推多组解 (离散角度)"])

# --- 标签页 1：正向计算 ---
with tab1:
    st.header("手动输入验证")
    st.markdown("输入 A、B、C，系统将直接计算出三种强度的预测值。")
    col1, col2, col3 = st.columns(3)
    with col1:
        a_input = st.number_input("A (层厚/mm) ", value=0.20, format="%f")
    with col2:
        b_input = st.number_input("B (比例) ", value=2.00, format="%f")
    with col3:
        # 正向计算时，也改为下拉菜单限制输入，防止用户输入非标准角度
        c_input = st.selectbox("C (角度/°) ", options=[0.0, 45.0, 90.0], index=1)
        
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
    # 界面文案同步更新
    st.markdown("系统将在限定边界内 (**A: 0.1~0.3, B: 1~3, C: 0, 45, 90**)，为您寻找满足目标的最佳参数组合。")
    
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
        with st.spinner("正在匹配十万种参数组合..."):
            result_df = find_multiple_solutions(target_type, target_value, tolerance, num_samples=100000)
            
            if result_df.empty:
                st.warning(f"⚠️ 搜索完成，未能找到误差在 {tolerance} 内的组合。建议调整目标值或放宽容差。")
            else:
                st.success(f"✅ 搜索成功！为您找到了 **{len(result_df)}** 组满足 {target_type} 目标的工艺参数。")
                
                st.dataframe(
                    result_df.style.format({
                        "A (层厚/mm)": "{:.4f}",
                        "B (比例)": "{:.4f}",
                        "C (角度/°)": "{:.0f}",  # 角度不再需要小数位，直接展示整数
                        "抗拉强度计算值": "{:.4f}",
                        "弯曲强度计算值": "{:.4f}",
                        "ILSS计算值": "{:.4f}",
                        "目标误差绝对值": "{:.4f}"
                    }),
                    use_container_width=True,
                    height=450
                )
