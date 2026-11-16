# 常见问题

## 找不到描述包或启动文件

确认已加载 ROS 2 环境及本工作空间的 `install/setup.bash`。检查：

```bash
ros2 pkg prefix kepler_dexterous_hand_description
```

实际包名不同，应替换命令中的包名，同时传入 `description_package:=实际包名`。若找不到 `display.launch.py`，检查 `CMakeLists.txt` 的资源安装规则是否包含 `launch`，并重新编译。

## 启动时报 URDF 或 STL 不存在

启动文件读取的是已安装包的 share 目录。该目录下需要有 `urdf/Lefthand.urdf`、`urdf/Righthand.urdf`，以及左右手对应的 `meshes/left/`、`meshes/right/`。

检查 `install(DIRECTORY ...)` 包含 `urdf` 和 `meshes`，并保留 URDF 引用的大小写，例如左手 `left_base.STL`、右手 `right_base.STL`，应分别放进左右目录。

启动文件会适配 `package://Lefthand/meshes/`、`package://Righthand/meshes/` 两个旧前缀。其他旧包名应直接在 URDF 中改成实际包名和目录。

只想先查看 TF 时，可以设置 `check_meshes:=false` 跳过预检查；这个选项不会修复缺失的网格，RViz 仍会提示相关资源错误。

## RViz 没有显示模型

检查 Fixed Frame 为 `Base`，Hand 显示项已启用，Description Topic 为 `/robot_description`，订阅采用 Transient Local。然后检查：

```bash
ros2 topic info /robot_description
ros2 topic echo /joint_states --once
```

默认模式下应有模型描述和关节位置消息。若设置了 `publish_joint_states:=false`，需要由外部驱动发布关节状态。模型根坐标系改名后，也应相应修改 RViz 的 Fixed Frame。

## 窗口中的模型太大、太小或离原点很远

先调整 RViz 视角并查看 URDF 中的 `origin xyz` 和网格 `scale`。URDF 长度单位为 m，STL 本身不记录单位，应确认 STL 的实际导出尺寸。本启动文件不自动缩放网格。

## 滑块显示 11 个关节，或末端不联动

当前模型应有 11 个旋转关节，其中 5 个包含 `<mimic>`，所以独立滑块为 6 个。确认 `urdf/` 中放的是已添加联动的最终模型，并在重新安装后重启 launch。

检查跟随关节的 `mimic joint` 是否与主关节名称完全一致。启动文件已经对关节发布器设置 `use_mimic_tags=true`。

## 接外部驱动后，关节位置反复跳回零位

默认的滑块或初始位置发布器仍在发布 `/joint_states`。改用：

```bash
ros2 launch kepler_dexterous_hand_description display.launch.py hand:=right publish_joint_states:=false
```

`gui:=false` 只切换为无界面初始位置发布器，不会关闭关节状态发布。

## 启用了仿真时间后不更新

`use_sim_time:=true` 需要可用的 `/clock`。普通 RViz 模型查看保持默认的 `use_sim_time:=false`。

## 左右手同时启动发生重叠

本启动文件每次加载一只手。两份模型都使用 `Base` 根坐标系，并默认共享模型与关节话题。查看另一只手前关闭上一套 launch；双手同显需要另外配置互不冲突的坐标系和命名空间。
