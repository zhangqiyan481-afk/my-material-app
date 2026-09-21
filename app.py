import streamlit as st
import numpy as np
import pandas as pd
import json
import os

# ==========================================
# 1. 页面基础配置 
# ==========================================
st.set_page_config(page_title="材料力学计算系统", layout="wide")

# ==========================================
# 2. 用户数据管理
# ==========================================
USER_DATA_FILE = "users.json"

def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {"admin": "123456"}  # 默认管理员账号

def save_users(users_dict):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users_dict, f)

# ==========================================
# 3. 核心计算算法
# ==========================================
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

# 【修改点 1】新增 top_n=20 参数限制输出数量
def find_multiple_solutions(target_type, target_value, tolerance, num_samples=100000, top_n=20):
    a_samples = np.random.uniform(0.1, 0.3, num_samples)
    b_samples = np.random.uniform(1.0, 3.0, num_samples)
    c_samples = np.random.choice([0.0, 45.0, 90.0], size=num_samples)
    
    ts_values, fs_values, ilss_values = calculate_properties(a_samples, b_samples, c_samples)
    
    if target_type == "抗拉强度":
        errors = np.abs(ts_values - target_value)
    elif target_type == "弯曲强度":
        errors = np.abs(fs_values - target_value)
    else: 
        errors = np.abs(ilss_values - target_value)
        
    valid_indices = np.where(errors <= tolerance)[0]
    
    results = []
    for idx in valid_indices:
        results.append({
            "A (层厚/mm)": a_samples[idx],
            "B (比例)": b_samples[idx],
            "C (角度/°)": c_samples[idx],
            "抗拉强度": ts_values[idx],
            "弯曲强度": fs_values[idx],
            "ILSS": ilss_values[idx],
            "误差": errors[idx]
        })
        
    df = pd.DataFrame(results)
    if not df.empty:
        # 按误差排序后，利用 head(top_n) 截断多余数据
        df = df.sort_values(by="误差").reset_index(drop=True)
        df = df.head(top_n)
    return df

# ==========================================
# 4. 系统登录状态初始化
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = ""

# ==========================================
# 5. 界面路由控制 
# ==========================================
if not st.session_state['logged_in']:
    
    # ------------------ 登录模块 ------------------
    st.title("材料力学计算系统")
    st.write("请登录或注册以继续使用系统。")
    
    tab_login, tab_register = st.tabs(["用户登录", "用户注册"])
    
    with tab_login:
        login_user = st.text_input("用户名", key="login_user")
        login_pwd = st.text_input("密码", type="password", key="login_pwd")
        
        if st.button("登录", type="primary"):
            users = load_users()
            if login_user in users and users[login_user] == login_pwd:
                st.session_state['logged_in'] = True
                st.session_state['current_user'] = login_user
                st.rerun() 
            else:
                st.error("用户名不存在或密码错误")

    with tab_register:
        reg_user = st.text_input("新用户名", key="reg_user")
        reg_pwd = st.text_input("设置密码", type="password", key="reg_pwd")
        reg_pwd_confirm = st.text_input("确认密码", type="password", key="reg_pwd_conf")
        
        if st.button("注册"):
            users = load_users()
            if reg_user in users:
                st.warning("该用户名已存在")
            elif reg_pwd != reg_pwd_confirm:
                st.error("两次输入的密码不一致")
            elif len(reg_user) < 3 or len(reg_pwd) < 6:
                st.warning("用户名至少3位，密码至少6位")
            else:
                users[reg_user] = reg_pwd
                save_users(users)
                st.success("注册成功，请切换至登录页进行登录")

else:
    # ------------------ 核心业务模块 ------------------
    col_user, col_space, col_exit = st.columns([2, 8, 1])
    with col_user:
        st.write(f"当前用户: {st.session_state['current_user']}")
    with col_exit:
        if st.button("退出系统"):
            st.session_state['logged_in'] = False
            st.session_state['current_user'] = ""
            st.rerun()
            
    st.divider()
    
    st.header("系统主控制台")
    tab1, tab2 = st.tabs(["正向性能预测", "逆向参数推导"])

    # --- 正向预测 ---
    with tab1:
        st.subheader("输入工艺参数")
        col1, col2, col3 = st.columns(3)
        with col1:
            a_input = st.number_input("A (层厚/mm)", value=0.20, format="%f")
        with col2:
            b_input = st.number_input("B (比例)", value=2.00, format="%f")
        with col3:
            c_input = st.selectbox("C (角度/°)", options=[0.0, 45.0, 90.0], index=1)
            
        if st.button("执行计算", type="primary"):
            ts, fs, ilss = calculate_properties(a_input, b_input, c_input)
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric("抗拉强度", f"{ts:.4f}")
            res_col2.metric("弯曲强度", f"{fs:.4f}")
            res_col3.metric("ILSS", f"{ilss:.4f}")

    # --- 逆向推导 ---
    with tab2:
        st.subheader("设定目标指标")
        target_type = st.selectbox("目标类别", ["抗拉强度", "弯曲强度", "ILSS"])
        
        col4, col5 = st.columns(2)
        with col4:
            target_value = st.number_input("期望数值", value=50.0)
        with col5:
            # 【修改点 2】优化了容差的默认值和步长
            tolerance = st.number_input("允许误差", value=0.1, step=0.01)
            
        if st.button("开始分析", type="primary"):
            with st.spinner("数据分析中..."):
                # 传入 top_n=20，确保最多只输出 20 组结果
                result_df = find_multiple_solutions(target_type, target_value, tolerance, top_n=20)
                
                if result_df.empty:
                    st.warning("未找到匹配的参数组合，请尝试放大允许误差。")
                else:
                    # 【修改点 3】文案同步更新
                    st.success(f"分析完成，为您展示最优的 {len(result_df)} 组方案。")
                    st.dataframe(
                        result_df.style.format({
                            "A (层厚/mm)": "{:.4f}",
                            "B (比例)": "{:.4f}",
                            "C (角度/°)": "{:.0f}",
                            "抗拉强度": "{:.4f}",
                            "弯曲强度": "{:.4f}",
                            "ILSS": "{:.4f}",
                            "误差": "{:.4f}"
                        }),
                        use_container_width=True,
                        height=450
                    )
