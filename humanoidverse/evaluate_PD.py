#!/usr/bin/env python3
# reverse_kpkd.py
#
# 作用：读取 MJCF XML + 已知 Kp/Kd，反推 ω_n 和 ζ
# 依赖：Python >= 3.8，仅标准库

from lxml import etree as ET
import math, csv, sys
from collections import defaultdict

# ---------- 手动配置区域 ----------
XML_PATH = "/home/ehr/wxy/PBHC/description/robots/g1/g1_23dof_lock_wrist.xml"        # ← 改成你的 MJCF 路径

# 已知的 Kp / Kd（Nm/rad ，Nm·s/rad）
# 键使用关节 name；可以只填需要分析的关节
KP_DICT = {
    "left_hip_yaw_joint": 100,
    "left_hip_roll_joint": 100,
    "left_hip_pitch_joint": 100,
    "left_knee_joint": 150,
    "left_ankle_pitch_joint": 40,
    "left_ankle_roll_joint": 40,
    "right_hip_yaw_joint": 100,
    "right_hip_roll_joint": 100,
    "right_hip_pitch_joint": 100,
    "right_knee_joint": 150,
    "right_ankle_pitch_joint": 40,
    "right_ankle_roll_joint": 40,
    "waist_yaw": 400,
    "waist_roll": 400,
    "waist_pitch": 400,
    "left_shoulder_pitch_joint": 100,
    "left_shoulder_roll_joint": 100,
    "left_shoulder_yaw_joint": 50,
    "left_elbow_joint": 50,
    "right_shoulder_pitch_joint": 100,
    "right_shoulder_roll_joint": 100,
    "right_shoulder_yaw_joint": 50,
    "right_elbow_joint": 50,
}
KD_DICT = {
    "left_hip_yaw_joint": 2.0,
    "left_hip_roll_joint": 2.0,
    "left_hip_pitch_joint": 2.0,
    "left_knee_joint": 4.0,
    "left_ankle_pitch_joint": 2.0,
    "left_ankle_roll_joint": 2.0,
    "right_hip_yaw_joint": 2.0,
    "right_hip_roll_joint": 2.0,
    "right_hip_pitch_joint": 2.0,
    "right_knee_joint": 4.0,
    "right_ankle_pitch_joint": 2.0,
    "right_ankle_roll_joint": 2.0,
    "waist_yaw": 5.0,
    "waist_roll": 5.0,
    "waist_pitch": 5.0,
    "left_shoulder_pitch_joint": 2.0,
    "left_shoulder_roll_joint": 2.0,
    "left_shoulder_yaw_joint": 2.0,
    "left_elbow_joint": 2.0,
    "right_shoulder_pitch_joint": 2.0,
    "right_shoulder_roll_joint": 2.0,
    "right_shoulder_yaw_joint": 2.0,
    "right_elbow_joint": 2.0,
}

GEAR_COEF = 1e-4  # gear² 折算惯量
# ---------------------------------
# ---------- 解析带 default 继承 ---------- #
def parse_mjcf_with_defaults(xml_path):
    parser = ET.XMLParser(recover=True)
    root   = ET.parse(xml_path, parser).getroot()

    # 收集 default 树
    default_stack = [{}]
    def traverse(elem, inherited):
        cur = inherited.copy()
        if elem.tag == "default":
            for joint in elem.iter("joint"):
                for k, v in joint.attrib.items():
                    cur[f"joint.{k}"] = v
            for motor in elem.iter("motor"):
                for k, v in motor.attrib.items():
                    cur[f"motor.{k}"] = v

        if elem.tag == "joint":
            name = elem.get("name")
            arm  = elem.get("armature") or cur.get("joint.armature") or "0"
            elem.set("resolved_armature", arm)
        if elem.tag in ("motor", "velocity", "position"):
            joint = elem.get("joint")
            gear  = elem.get("gear") or cur.get("motor.gear") or "0"
            elem.set("resolved_gear", gear)

        for child in elem:
            traverse(child, cur)

    traverse(root, {})
    return root

root = parse_mjcf_with_defaults(XML_PATH)

# ---------- 收集 gear ---------- #
gear_dict = defaultdict(float)
for motor in root.xpath(".//actuator/*[@joint]"):
    joint_name = motor.get("joint")
    gear_dict[joint_name] = float(motor.get("resolved_gear"))

# ---------- 主循环 ---------- #
rows = []
for joint in root.xpath(".//joint[@name]"):
    name  = joint.get("name")
    if name not in KP_DICT:  # 只分析提供的关节
        continue

    kp = KP_DICT[name]; kd = KD_DICT[name]
    arm = float(joint.get("resolved_armature", "0"))
    gear = gear_dict.get(name, 0.0)
    Ieq  = arm + (gear ** 2) * GEAR_COEF
    wn   = math.sqrt(kp / Ieq) if Ieq else None
    zeta = kd / (2 * math.sqrt(kp * Ieq)) if Ieq else None

    rows.append(dict(
        joint=name, armature=arm, gear=gear, Ieq=round(Ieq,6),
        kp=kp, kd=kd,
        wn=round(wn,3) if wn else None,
        zeta=round(zeta,3) if zeta else None
    ))

# ---------- 输出 ---------- #
writer = csv.DictWriter(sys.stdout,
    fieldnames=["joint","armature","gear","Ieq","kp","kd","wn","zeta"])
writer.writeheader(); writer.writerows(rows)