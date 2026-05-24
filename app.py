import numpy as np
import pandas as pd
import sys

# --- 核心计算公式 ---
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
def find_multiple_solutions(target_type_code, target_value, tolerance, num_samples=100000):
    """核心寻优算法：在范围内生成随机数进行碰撞筛选"""
    # 设定工艺边界
    a_samples = np.random.uniform(0.1, 0.3, num_samples)
    b_samples = np.random.uniform(1.0, 3.0, num_samples)
    c_samples = np.random.uniform(0.0, 90.0, num_samples)
    
    # 批量计算
    ts_values, fs_values, ilss_values = calculate_properties(a_samples, b_samples, c_samples)
    
    # 根据目标类型锁定误差
    if target_type_code == '1':
        errors = np.abs(ts_values - target_value)
    elif target_type_code == '2':
        errors = np.abs(fs_values - target_value)
    else:
        errors = np.abs(ilss_values - target_value)
        
    # 筛选合格数据
    valid_indices = np.where(errors <= tolerance)[0]
    
    results = []
    for idx in valid_indices:
        results.append({
            "A(层厚)": round(a_samples[idx], 4),
            "B(比例)": round(b_samples[idx], 4),
            "C(角度)": round(c_samples[idx], 2),
            "抗拉(TS)": round(ts_values[idx], 4),
            "弯曲(FS)": round(fs_values[idx], 4),
            "ILSS": round(ilss_values[idx], 4),
            "误差": round(errors[idx], 4)
        })
        
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values(by="误差").reset_index(drop=True)
    return df

# --- 交互界面 ---
def main():
    # 设置 pandas 打印格式，使其在终端显示更完整、更美观
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    while True:
        print("\n" + "="*50)
        print("  材料力学性能算法测试工具 (纯代码版)")
        print("="*50)
        print("1. 正向计算 (已知 A, B, C 算三种性能)")
        print("2. 逆向反推 (指定单一目标，搜索多组可行解)")
        print("0. 退出程序")
        print("="*50)
        
        choice = input("请输入您的选择 (0/1/2): ")
        
        if choice == '0':
            print("退出测试...")
            sys.exit(0)
            
        elif choice == '1':
            print("\n--- [模式 1] 正向计算 ---")
            try:
                a = float(input("输入 A (层厚 0.1~0.3): "))
                b = float(input("输入 B (比例 1~3): "))
                c = float(input("输入 C (角度 0~90): "))
                ts, fs, ilss = calculate_properties(a, b, c)
                print("\n>>> 计算结果 <<<")
                print(f"抗拉强度 (Tensile): {ts:.4f}")
                print(f"弯曲强度 (Flexural): {fs:.4f}")
                print(f"层间剪切强度 (ILSS): {ilss:.4f}")
            except ValueError:
                print("输入格式错误，请输入数字。")
                
        elif choice == '2':
            print("\n--- [模式 2] 单指标多解搜索 ---")
            print("选择核心目标: 1-抗拉强度 | 2-弯曲强度 | 3-ILSS")
            target_type = input("请输入目标序号 (1/2/3): ")
            if target_type not in ['1', '2', '3']:
                print("无效的序号！")
                continue
                
            try:
                target_val = float(input("请输入期望的目标数值: "))
                tol = float(input("请输入允许的误差范围 (如 0.5): "))
                
                print(f"\n正在生成 10 万组数据进行寻优，请稍候...\n")
                df = find_multiple_solutions(target_type, target_val, tol)
                
                if df.empty:
                    print(">>> 未找到符合条件的参数组合。您可以尝试放大误差范围或调整目标值。 <<<")
                else:
                    print(f">>> 寻优成功！共找到 {len(df)} 组方案 (默认最多显示前50条最佳匹配) <<<")
                    print(df.head(50)) # 终端里展示前50条误差最小的记录
            except ValueError:
                print("输入格式错误，请输入数字。")
        else:
            print("无效的输入，请重试。")

if __name__ == "__main__":
    main()
