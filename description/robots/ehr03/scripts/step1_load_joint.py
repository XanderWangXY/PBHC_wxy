import mujoco, json, numpy as np

model = mujoco.MjModel.from_xml_path("/home/ehr/wxy/PBHC/description/robots/ehr03/urdf/ehr03_simplifed.xml")
joints = []
for j in range(model.njnt):
    if model.jnt_type[j] == mujoco.mjtJoint.mjJNT_HINGE:   # 只管旋转 DOF
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, j)
        axis = model.jnt_axis[j].copy().round(5).tolist()
        parent = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY,
                                   model.jnt_bodyid[j])
        joints.append({"name": name, "axis": axis, "parent_body": parent})
with open("ehr03_rot_joints.json", "w") as f: json.dump(joints, f, indent=2)
print(f"Found {len(joints)} hinge joints.")
