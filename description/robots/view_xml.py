import mujoco
import mujoco.viewer

# 替换为你自己的路径
xml_path = "/home/ehr/wxy/PBHC/description/robots/g1/smpl_humanoid.xml"

# 加载模型
model = mujoco.MjModel.from_xml_path(xml_path)
data = mujoco.MjData(model)

# 启动可视化窗口
with mujoco.viewer.launch_passive(model, data) as viewer:
    print("Press ESC to exit viewer")
    while viewer.is_running():
        mujoco.mj_step(model, data)
        viewer.sync()
