# -----------------------------------------
# pd_table_generator.py   (v3 – inner / rl / freq)
# -----------------------------------------
import math, csv

# ========= 全局可调 =========
MODE = "freq"                    # inner | rl | freq
ZETA = 1.0                       # 阻尼比 0.7~1.2

# —— inner 模式 ↓ ——
DT = 0.001                       # 内环周期 (s)

# —— rl 模式 ↓ ——
COMMON_E_MAX     = 0.10          # rad
COMMON_TAU_LIMIT = 60.0          # N·m

# —— freq 模式 ↓ ——
COMMON_FREQ      = 4.0           # target f_n (Hz)
# ===========================


# 关节表:
# name , I(kg·m²) , alpha , freq(Hz)|None , e_max|None , tau_max|None
JOINTS = [
    ("arm1"  , 0.038909, 1.0, 2.5, 0.05 , 60),
    ("arm2"  , 0.033048, 1.0, 2.5, 0.05 , 75),
    ("arm3"  , 0.023587, 1.0, 2.5, 0.03 , 36),
    ("arm4"  , 0.023587, 1.0, 2.5, 0.03 , 36),
    ("arm5"  , 0.023587, 1.0, 2.5, 0.03 , 36),
    ("arm6"  , 0.023587, 1.0, 2.5, 0.03 , 36),
    ("torso1", 0.038909, 1.0, 4.0, 0.08 , 60),
    ("torso2", 0.047528, 1.0, 4.0, 0.08 , 90),
    ("torso3", 0.038909, 1.0, 4.0, 0.08 , 60),
    ("leg1"  , 0.197652, 1.0, 5.5, 0.10 ,110),
    ("leg2"  , 0.070310, 1.0, 5.0, 0.10 ,150),
    ("leg3"  , 0.070310, 1.0, 5.0, 0.10 ,150),
    ("leg4"  , 0.197652, 1.0, 5.5, 0.10 ,110),
    ("leg5"  , 0.033048, 1.0, 3.0, 0.05 , 75),
    ("leg6"  , 0.033048, 1.0, 3.0, 0.05 , 75),
]

# ---------- 计算函数 ----------
def pd_inner(I, alpha):
    kp = alpha * (math.pi**2) * I / (DT**2)
    kd = 2 * ZETA * math.sqrt(kp * I)
    return kp, kd

def pd_rl(I, alpha, e_max, tau_max):
    kp = alpha * (tau_max / e_max)
    kd = 2 * ZETA * math.sqrt(kp * I)
    return kp, kd

def pd_freq(I, alpha, f_n):
    kp = alpha * I * (2*math.pi*f_n)**2
    kd = 2 * ZETA * math.sqrt(kp * I)
    return kp, kd
# --------------------------------

def main():
    rows = [("joint","I","alpha","kp","kd")]
    for name,I,alpha,freq,e_max,tau_max in JOINTS:
        if MODE == "inner":
            kp,kd = pd_inner(I,alpha)
        elif MODE == "rl":
            em   = e_max  if e_max  is not None else COMMON_E_MAX
            taum = tau_max if tau_max is not None else COMMON_TAU_LIMIT
            kp,kd = pd_rl(I,alpha,em,taum)
        elif MODE == "freq":
            f = freq if freq is not None else COMMON_FREQ
            kp,kd = pd_freq(I,alpha,f)
        else:
            raise ValueError("MODE 需为 inner / rl / freq")

        print(f"{name:10s}  kp={kp:8.2f}  kd={kd:6.2f}")
        rows.append((name,I,alpha,kp,kd))

    with open("pd_gains.csv","w",newline="") as f:
        csv.writer(f).writerows(rows)
    print(f"\n模式: {MODE}  → 已写入 pd_gains.csv")

if __name__ == "__main__":
    main()
