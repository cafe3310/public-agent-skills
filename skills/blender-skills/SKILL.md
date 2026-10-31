---
name: blender-skills
description: >
  Mandatory entry point for 3D product modeling, rendering, scene composition, and camera animations in Blender.
  Acts as the composite skill router containing 14 specialized subskills in subskills/<name>.
  Covers PolyHaven studio & PBR material setup, material variant swap, camera orbit & reveal animations
  (turntable, slow-zoom, dolly-rotate, crane-shot, dynamic loop), product polish, interactive Three.js
  web export, and Blender automation via MCP/WebSocket.
  Directs agents to read subskills/<name>/SKILL.md on demand without cluttering the global skill namespace.
license: MIT
author: https://github.com/kevinbadi/blender-skills
depends_on_skill: []
depends_on_binary:
  - blender
  - node
  - ffmpeg
---

# Blender 3D 产品摄影与自动化套件 (Master Composite Skill)

本技能通过 **Blender MCP (Model Context Protocol)** 与 WebSocket 服务驱动 Blender，覆盖 3D 模型表面打磨、专业摄影棚环境搭建、PBR 材质赋予与换肤、电影级透明通道运镜视频渲染，到 Three.js 网页端可交互交付的完整产品管线。

> **复合技能架构说明 (Composite Skill)**：  
> 本技能为一级总控入口。所有 14 个专项子技能与自动化脚本均收纳在 **`subskills/<name>/`** 目录下。  
> 当确定具体执行任务时，**请使用 `view_file` 读取对应的 `subskills/<name>/SKILL.md` 文档**。

---

## 1. 依据项目现有状态判定 (Start from project state)

按首个命中的行处理，不要向下顺延：

| 状态 | 执行动作 | 需加载的子技能 |
| :--- | :--- | :--- |
| **已有原始 3D 模型**（GLB/GLTF），质感粗糙，需快速打磨为高级产品级成片 | 进行几何居中、规格化、微调粗糙度与三点布光 | `subskills/product-polish/SKILL.md` |
| **需搭建专业摄影棚**、配置自然反射地面与 HDRI 环境光 | 自动拉取 PolyHaven 预设资产并构建世界光照 | `subskills/polyhaven-studio-setup/SKILL.md` |
| **需展示多款材质/颜色配置**（如金属、木纹、皮革等变体对比） | 批量替换材质并自动输出变体效果渲染图 | `subskills/polyhaven-material-swap/SKILL.md` |
| **需生成产品视频动画**（带透明通道的 ProRes 4444 / WebM） | 判定镜头语言，依据运镜矩阵配置并渲染 | 参见第 3 节「运镜动画子技能」 |
| **需将 3D 产品展示放置到网页**，支持鼠标拖拽旋转交互 | 导出优化后的 GLB 并生成带控制器与自转的 Three.js 页面 | `subskills/threejs-export/SKILL.md` |
| **需进行底层几何形变**、修改器操作或 Mixamo 角色骨骼动画绑定 | 启动 WebSocket 实时控制套件 | `subskills/blender-toolkit/SKILL.md` |

---

## 2. 全新任务意图路由表 (Intent Routing Table)

请根据**交付物形态与任务目标**匹配首个命中的子技能：

| 优先级 | 需求形态 / 场景特征 | 适用的子技能 (Subskill) | 相对路径 |
| :---: | :--- | :--- | :--- |
| 1 | 刚导入的 3D 模型缺乏光泽与质感，需产品级高光与基础布光 | `product-polish` | `subskills/product-polish/SKILL.md` |
| 2 | 一键配置产品摄影棚（HDRI 环境光 + PBR 地面反射） | `polyhaven-studio-setup` | `subskills/polyhaven-studio-setup/SKILL.md` |
| 3 | 给指定物体赋予真实 PBR 贴图（金属/木材/大理石/布料） | `polyhaven-texture-apply` | `subskills/polyhaven-texture-apply/SKILL.md` |
| 4 | 针对产品测试不同材质款式，批量渲染对比图 | `polyhaven-material-swap` | `subskills/polyhaven-material-swap/SKILL.md` |
| 5 | 构建包含圆柱展台（Pedestal）、地面与装饰道具的完整场景 | `polyhaven-scene-builder` | `subskills/polyhaven-scene-builder/SKILL.md` |
| 6 | 在多种 HDRI 环境（影棚/黄昏/户外）下渲染矩阵对比图 | `polyhaven-hdri-showcase` | `subskills/polyhaven-hdri-showcase/SKILL.md` |
| 7 | 经典 360° 环绕平拍展示视频（默认带透明通道） | `turntable` | `subskills/turntable/SKILL.md` |
| 8 | 细节慢推特写镜头（Hero Shot，聚焦 Logo 或局部质感） | `slow-zoom` | `subskills/slow-zoom/SKILL.md` |
| 9 | 前进同时环绕旋转的弧形动态推进镜头 | `dolly-rotate` | `subskills/dolly-rotate/SKILL.md` |
| 10 | 摇臂俯仰镜头（低角度升起俯瞰展台与产品） | `crane-shot` | `subskills/crane-shot/SKILL.md` |
| 11 | 变速多面环绕镜头（慢速定格关键面，快速甩镜头切换） | `dynamic-full-loop` | `subskills/dynamic-full-loop/SKILL.md` |
| 12 | 首尾帧速度与位置严格匹配的无缝无限循环展示镜头 | `perfect-loop` | `subskills/perfect-loop/SKILL.md` |
| 13 | 导出 Web 3D 交互式 Three.js 独立展示网页 | `threejs-export` | `subskills/threejs-export/SKILL.md` |
| 14 | Blender 基础几何体构建、材质通道管理与 Mixamo 动画重定向 | `blender-toolkit` | `subskills/blender-toolkit/SKILL.md` |

---

## 3. 运镜动画子技能速查 (Camera Motion Matrix)

所有运镜技能默认渲染输出到 `~/Desktop/Blender Videos/`，支持 **ProRes 4444 透明通道（MOV）** 或 **WebM**：

| 运镜名称 | 轨迹特征 | 镜头视觉感受 | 适用场景 |
| :--- | :--- | :--- | :--- |
| **`turntable`** | 360° 水平匀速圆周轨道 | 客观、平稳、经典工业展示 | 通用产品全视角展示 |
| **`slow-zoom`** | 线性慢推 + 滑动变焦（Dolly Zoom） | 聚焦、揭示、强调局部质感 | Logo 特写、精密器件细节 |
| **`dolly-rotate`** | 螺旋式向前推进并绕转 | 动态纵深感、现代宣发节奏 | 消费电子、潮品新品上市片头 |
| **`crane-shot`** | 沿 Z 轴升起 + 摄像机同步下俯下倾 | 庄重、揭示展台与整体气势 | 放置在展台上的珠宝、香水、腕表 |
| **`dynamic-full-loop`** | 变速贝塞尔曲线 + 快速甩镜头（Whip-pan） | 高科技感、多角度快节奏巡礼 | 电子数码、多接口/全角度设备 |
| **`perfect-loop`** | 严格首尾闭合的 360° 旋转 | 首尾无缝衔接，无卡顿无跳帧 | 电商详情页循环动图、动态 Banner |

> 运镜执行前需通过检测物体包围盒识别正面方位（详见 `references/camera-choreography.md`）；摄像机光轴注视与坐标系必须严格遵循右手系 Z-Up 与局部 -Z 注视铁律（详见 `references/coordinates-and-scene-building.md`）。

---

## 4. 领域支撑文档与规范

* **MCP 控制架构与 Python 自动化执行规范（核心必读）**：
  查阅 [`references/mcp-control-guide.md`](references/mcp-control-guide.md)
  （知识库溯源：`[[2026-09-28-05 Blender MCP 控制与自动化使用指南]]`）。
  涵盖 MCP 工具集（探测 `get_objects_summary`、截图预览 `render_viewport_to_path`、代码执行器 `execute_blender_code`）、`result` 变量数据回传约定、数据块与对象分离、依赖图刷新 `bpy.context.view_layer.update()`、视口与材质着色实时联动。
* **空间坐标轴向与场景构建避坑规范（核心必读）**：
  查阅 [`references/coordinates-and-scene-building.md`](references/coordinates-and-scene-building.md)
  （知识库溯源：`[[2026-09-28-05 Blender 场景构建经验与空间坐标轴向规范]]`）。
  涵盖右手系 Z-Up 空间坐标原则（$-Y$ 为正面、$+X$ 为右、$+Z$ 向上）、摄影机局部坐标系（局部 $-Z$ 轴为拍摄光轴，局部 $+Y$ 轴为画面正上方，`TRACK_TO` 必须锁定 `TRACK_NEGATIVE_Z` / `UP_Y`）、Blender 5.x 分层动画插值曲线兼容函数、共面 Z-Fighting 规避容差（0.02~0.05 间距）、图元旋转失真防范。
* **环境与通信配置**：查阅 [`references/environment-setup.md`](references/environment-setup.md)（Blender MCP 端口 9876、Node 环境与 FFmpeg）。
* **运镜调度与参数规范**：查阅 [`references/camera-choreography.md`](references/camera-choreography.md)（包围盒居中、正面检测、TrackTo 约束、贝塞尔曲线参数）。
* **PolyHaven 资产与着色器规范**：查阅 [`references/polyhaven-workflows.md`](references/polyhaven-workflows.md)（HDRI 预设、PBR 贴图节点连接图与批量替换逻辑）。

---

## 5. 常见组合操作流水线示例

- **「产品模型高光打磨与 3D 展示视频」**：
  1. `subskills/product-polish/SKILL.md`（打磨高光、规格化模型并调整材质）
  2. `subskills/polyhaven-studio-setup/SKILL.md`（搭建专业影棚灯光）
  3. `subskills/turntable/SKILL.md`（渲染透明通道展示视频）
- **「材质方案提案对比」**：
  1. `subskills/polyhaven-material-swap/SKILL.md`（选择 `metals` 或 `woods` 预设，批量渲染多材质图）
  2. `subskills/polyhaven-hdri-showcase/SKILL.md`（生成多光照场景对比矩阵图）
- **「独立 Web 交互交付」**：
  1. `subskills/product-polish/SKILL.md`（调整模型表面）
  2. `subskills/threejs-export/SKILL.md`（导出 GLB + 独立 HTML）
