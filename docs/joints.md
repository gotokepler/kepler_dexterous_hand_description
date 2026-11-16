# 关节参数、正方向与联动

适用于包内 `urdf/Lefthand.urdf` 和 `urdf/Righthand.urdf`。启动文件从已安装描述包中读取模型，关节参数以 URDF 中的实际数值为准。

## 单位与角度范围

位置和角度使用 m、rad；旋转速度为 rad/s；力矩为 N·m。

| 关节类别 | lower（rad） | upper（rad） | effort（N·m） | velocity（rad/s） |
|---|---:|---:|---:|---:|
| 拇指横滚 `*_thumb_1_roll` | 0.000 | 2.269 | 0.500 | 1.500 |
| 拇指中间俯仰 `*_thumb_2_pitch` | 0.000 | 1.309 | 0.500 | 1.500 |
| 拇指末端俯仰 `*_thumb_3_pitch` | 0.000 | 1.658 | 0.500 | 1.500 |
| 食指、中指、无名指、小指各俯仰关节 | 0.000 | 1.658 | 0.500 | 1.500 |

上述角度上限分别约为 130°、75°、95°。

## 正方向

正角度约定为：拇指横滚朝小指侧转动，五指朝抓握方向弯曲。零位为 URDF 中关节角度全为 0 的导出姿态。

| 关节类别 | 左手局部 axis | 右手局部 axis |
|---|---|---|
| 拇指横滚 | `0 0 1` | `0 0 -1` |
| 拇指两个俯仰关节 | `0 0 -1` | `0 0 1` |
| 其余四指的全部俯仰关节 | `0 0 -1` | `0 0 1` |

`axis` 位于各关节局部坐标系中，应结合 `origin rpy` 判断实际方向。左右手按共同掌坐标系的 `Y=0` 平面做运动学镜像核对。

## 六个独立控制关节

| 功能 | 左手 | 右手 |
|---|---|---|
| 拇指横滚 | `left_thumb_1_roll` | `right_thumb_1_roll` |
| 拇指弯曲 | `left_thumb_2_pitch` | `right_thumb_2_pitch` |
| 食指弯曲 | `left_index_finger_2_pitch` | `right_index_finger_2_pitch` |
| 中指弯曲 | `left_middle_finger_2_pitch` | `right_middle_finger_2_pitch` |
| 无名指弯曲 | `left_ring_finger_2_pitch` | `right_ring_finger_2_pitch` |
| 小指弯曲 | `left_little_finger_2_pitch` | `right_little_finger_2_pitch` |

滑块界面应只显示这 6 个关节。其余 5 个末端关节由 URDF 中的 `<mimic>` 定义跟随。

## 五组联动

下表中的 `side` 取 `left` 或 `right`，例如 `side_thumb_2_pitch` 对应 `left_thumb_2_pitch` 或 `right_thumb_2_pitch`。

| 手指 | 主关节 | 跟随关节 | multiplier | offset（rad） |
|---|---|---|---:|---:|
| 拇指 | `side_thumb_2_pitch` | `side_thumb_3_pitch` | 1.2666157372039724 | 0 |
| 食指 | `side_index_finger_2_pitch` | `side_index_finger_3_pitch` | 1 | 0 |
| 中指 | `side_middle_finger_2_pitch` | `side_middle_finger_3_pitch` | 1 | 0 |
| 无名指 | `side_ring_finger_2_pitch` | `side_ring_finger_3_pitch` | 1 | 0 |
| 小指 | `side_little_finger_2_pitch` | `side_little_finger_3_pitch` | 1 | 0 |

位置关系为 `q_follow = multiplier * q_master + offset`。

拇指比例取约 `1.658 / 1.309`，使中间关节和末端关节同时到达表格给出的角度上限。该比例属于按行程推定的运动学设置，接入实际机构时应按标定结果核对。

## 拇指联动速度

联动速度关系为 `v_follow = multiplier * v_master`。两关节的 URDF 速度字段都为 1.500 rad/s，因此后续控制器应满足：

```text
|v_thumb_2_pitch| <= 1.500 / 1.2666157372039724
                 ≈ 1.184258142340 rad/s
```

这样末端关节的速度才不超过 1.500 rad/s。该约束需要在控制器或轨迹规划中落实，RViz 滑块不执行这个限速。URDF 的 `effort` 字段同样属于模型参数，滑块展示不会据此进行力矩仿真。

## 如何更新

修改关节上下限、局部轴、力矩、速度或联动比时，编辑对应 URDF。重新安装或编译描述包并重启 launch 后，显示节点会读取新的文件。

启动文件不重新定义这些关节值；`use_mimic_tags` 已开启，以读取实际 URDF 中的联动关系。
