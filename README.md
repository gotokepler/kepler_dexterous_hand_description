# Kepler 灵巧手 ROS 2 描述包

`kepler_dexterous_hand_description` 提供左右灵巧手的 URDF、STL 网格、RViz 配置和启动文件，用于查看手部模型、调节关节姿态及检查运动学联动。

每只手包含 **12 个 link、11 个旋转关节**，其中 **6 个独立关节、5 个 mimic 跟随关节**。默认启动 RViz 和关节滑块界面，每次加载一只手。

本包是模型描述与可视化包，不包含真实电机驱动、`ros2_control` 控制器、MoveIt 配置或 Gazebo 仿真配置。滑块用于发布关节位置，不会控制真实灵巧手。

## 目录结构

```text
kepler_dexterous_hand_description/
├── CMakeLists.txt          # ament_cmake 构建与资源安装规则
├── package.xml            # 包信息和依赖
├── README.md
├── launch/
│   └── display.launch.py   # 左右手可视化启动文件
├── urdf/
│   ├── Lefthand.urdf
│   └── Righthand.urdf
├── meshes/
│   ├── left/              # 左手 12 个 STL
│   └── right/             # 右手 12 个 STL
├── rviz/
│   └── display.rviz
└── docs/
    ├── README.md          # 详细使用与网格路径说明
    ├── joints.md          # 关节范围、方向和联动参数
    └── troubleshooting.md # 常见问题排查
```

## 环境与依赖

需要安装 ROS 2、colcon 和 rosdep。以下以 ROS 2 Humble 和 Bash 为例；使用其他发行版时，请将命令中的 `humble` 替换为对应发行版名称。RViz 和关节滑块需要桌面图形环境。

运行依赖已在 `package.xml` 声明，包括 `ament_index_python`、`launch`、`launch_ros`、`robot_state_publisher`、`joint_state_publisher`、`joint_state_publisher_gui` 和 `rviz2`，构建使用 `ament_cmake`。

## 创建工作空间并放置源码

创建 ROS 2 工作空间。以下统一使用 `~/ros2_ws` 作为示例，可替换为自己的工作空间路径：

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

将本包完整放入工作空间的 `src/` 目录，确认结构如下：

```text
ros2_ws/
└── src/
    └── kepler_dexterous_hand_description/
        ├── package.xml
        ├── CMakeLists.txt
        ├── urdf/
        ├── meshes/
        ├── launch/
        ├── rviz/
        └── docs/
```

本包已包含构建配置，无需再运行 `ros2 pkg create`。

## 安装依赖与编译

如果终端已激活 Conda，先退出，避免构建时使用 Conda Python。未激活 Conda 时跳过：

```bash
conda deactivate
```

加载 ROS 2 环境，并进入工作空间根目录：

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
```

安装包依赖。若尚未初始化 rosdep，先执行一次 `sudo rosdep init`；已初始化时跳过：

```bash
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

在工作空间根目录编译并加载安装环境：

```bash
colcon build --symlink-install \
  --packages-select kepler_dexterous_hand_description

source install/setup.bash
```

构建生成的 `build/`、`install/` 和 `log/` 位于工作空间根目录，无需放入描述包源码目录。

## 启动左右手

每次新开终端，都需要加载 ROS 2 和工作空间环境。若使用自定义工作空间路径，请相应修改 `cd` 命令：

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
source install/setup.bash
```

启动左手：

```bash
ros2 launch kepler_dexterous_hand_description display.launch.py hand:=left
```

按 `Ctrl+C` 关闭上一套节点后，启动右手：

```bash
ros2 launch kepler_dexterous_hand_description display.launch.py hand:=right
```

默认启动 `robot_state_publisher`、`joint_state_publisher_gui` 和 `rviz2`。RViz 的 Fixed Frame 为 `Base`，滑块界面应显示 6 个独立关节，其余 5 个关节按 URDF 的 `<mimic>` 定义联动。

两手模型均使用 `Base` 根坐标系，默认也共享话题和节点名称，因此不要直接同时运行两套默认 launch。双手同显需要另行配置命名空间、坐标系前缀和显示配置。

## 常用启动方式

保留 RViz，关闭滑块，发布初始关节位置：

```bash
ros2 launch kepler_dexterous_hand_description display.launch.py hand:=left gui:=false
```

无图形界面启动，只运行模型和关节状态发布节点：

```bash
ros2 launch kepler_dexterous_hand_description display.launch.py hand:=left gui:=false rviz:=false
```

接入外部驱动，由驱动发布 `/joint_states`：

```bash
ros2 launch kepler_dexterous_hand_description display.launch.py hand:=right publish_joint_states:=false
```

`gui:=false` 仍会启动关节状态发布器。使用外部驱动时应设置 `publish_joint_states:=false`，避免多个发布器交替覆盖关节位置。驱动的关节名称需与所选 URDF 一致，独立关节名称见 [关节说明](docs/joints.md)。

查看全部启动参数：

```bash
ros2 launch kepler_dexterous_hand_description display.launch.py --show-args
```

## 启动参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `hand` | `left` | 选择 `left` 或 `right` |
| `description_package` | `kepler_dexterous_hand_description` | URDF、网格及 RViz 配置所在包 |
| `gui` | `true` | 是否使用关节滑块；仅在发布关节状态时生效 |
| `rviz` | `true` | 是否启动 RViz |
| `publish_joint_states` | `true` | 是否启动本包 launch 中的关节状态发布器 |
| `use_sim_time` | `false` | 是否使用仿真时间；启用时需要 `/clock` |
| `check_meshes` | `true` | 启动前检查描述包内引用的网格文件是否存在 |
| `rviz_config` | `rviz/display.rviz` | RViz 配置的绝对路径，或相对描述包 share 目录的路径 |

布尔参数使用 `true` 或 `false`。

## 关节与模型维护

6 个独立关节分别控制拇指横滚、拇指弯曲，以及食指、中指、无名指、小指弯曲。各手指的末端关节跟随对应主关节，拇指的联动倍率约为 `1.2666`，其余四指为 `1`。精确参数以 URDF 为准，详见 [关节参数与联动](docs/joints.md)。

URDF 长度单位为 m，角度为 rad，速度为 rad/s，力矩为 N·m。RViz 滑块不执行真实电机控制，也不会根据 `effort`、`velocity` 字段进行力矩仿真或运动限速。


