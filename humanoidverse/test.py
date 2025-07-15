import xml.etree.ElementTree as ET
import sys


def calculate_urdf_weight(urdf_path):
    """计算URDF文件中机器人的总重量"""
    try:
        # 解析URDF文件
        tree = ET.parse(urdf_path)
        root = tree.getroot()

        total_mass = 0.0

        # 遍历所有link元素
        for link in root.findall('link'):
            # 查找link下的inertial元素
            inertial = link.find('inertial')
            if inertial is not None:
                # 查找inertial下的mass元素
                mass_element = inertial.find('mass')
                if mass_element is not None:
                    # 获取mass元素的value属性并转换为浮点数
                    try:
                        mass = float(mass_element.get('value', 0.0))
                        total_mass += mass
                    except ValueError:
                        print(f"警告: link '{link.get('name', 'unknown')}' 的质量值无法转换为浮点数")

        return total_mass

    except FileNotFoundError:
        print(f"错误: 文件 '{urdf_path}' 不存在")
        return None
    except ET.ParseError as e:
        print(f"错误: URDF文件解析失败: {e}")
        return None
    except Exception as e:
        print(f"错误: 发生未知错误: {e}")
        return None


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("用法: python urdf_weight_calculator.py <urdf文件路径>")
        sys.exit(1)

    urdf_path = sys.argv[1]
    total_weight = calculate_urdf_weight(urdf_path)

    if total_weight is not None:
        print(f"机器人总重量: {total_weight} 千克")