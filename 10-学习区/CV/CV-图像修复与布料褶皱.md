---
tags: [CV, 概念]
created: 2026-09-06
status: 整理中
domain: CV
source: 个人总结
---

# CV-图像修复与布料褶皱

> [!note] 分拣说明
> 2026-09-06 由 [[临时缓冲区]] 分拣而来(该缓冲池已清空删除),内容逐字搬运未改写。图像修复工具链:布料褶皱处理思路(SAM+LaMa)、lama-cleaner/IOPaint、DocTr/GeoTr 适用性辨析、热点修复流程脚本。

> —— 摘自原临时缓冲区 L52–L59 ——

简单光照估计并去阴影（OpenCV 的 L 通道形态学估计）

褶皱检测（梯度/Laplacian + 闭运算生成褶皱 mask）

基于 mask 做局部 inpainting（用 LaMa 或 lama-cleaner；轻量）


（SAM 自动生成褶皱 mask + LaMa 修复）

> —— 摘自原临时缓冲区 L61–L90 ——

lama-cleaner 本身就是 IOPaint 项目的 “子集”（IOPaint 是更通用的图像修复工具，支持 LaMa、SD Inpaint 等多种模型），iopaint CLI 是官方专门设计的命令行接口，目的就是为了 稳定、无侵入地调用修复功能


DocTr 和 GeoTr 主要是为文档图像校正设计的，它们解决的是：

文档拍摄角度倾斜
书页弯曲变形
扫描件的几何畸变

但你的布料褶皱问题本质不同：

这是物理织物的三维形变
褶皱处有真实的光影变化
图案本身在褶皱处发生了拉伸/压缩

DocTr/GeoTr 期望的输入是"平面内容被拍歪了"，而你的情况是"立体物体表面有起伏"。


修复流程脚本 (repair_pipeline_example.sh / Python)：
这是一个自动化和半自动化结合的脚本，用于处理检测到的热点。
循环处理热点：
从report.json中读取热点列表，按不确定度或面积排序。
裁剪热点区域：根据热点边界框从图B中裁剪出小区域。
应用修复策略：根据热点的诊断类型（例如，边缘位移、色彩偏移、纹理伪影），调用相应的专业模型或传统算法。
边缘保护：OpenCV的Canny边缘检测。
局部SR：调用Real-ESRGAN/SwinIR的脚本，处理裁剪区域。
局部Inpainting：调用LaMa/SD Inpainting脚本，处理裁剪区域。
色彩校正：scikit-image的match_histograms或OpenCV的色彩转移函数。
将修复结果融合回原图：将处理过的热点区域粘贴回原图B的对应位置。
（可选）重新评估：对融合后的图B再次运行evaluate_images.py，量化修复效果。

