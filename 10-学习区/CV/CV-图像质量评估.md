---
tags: [CV, 概念]
created: 2026-09-06
status: 整理中
domain: CV
source: 个人总结
---

# CV-图像质量评估

> [!note] 分拣说明
> 2026-09-06 由 临时缓冲区(已删除) 分拣而来(该缓冲池已清空删除),内容逐字搬运未改写。图像质量评估体系:Python 图像处理库清单、PSNR/SSIM/LPIPS/Mask IoU/Hausdorff/ΔE 指标解读、四类热点诊断与修复策略、A/B 实验设计。

> —— 摘自原临时缓冲区 L32–L44 ——

图像加载、裁剪、缩放、灰度转换、基本像素操作、矩阵计算等
Pillow / OpenCV-Python 图像的读取、写入、缩放、裁剪、色彩空间转换、基本滤波器、像素操作
scikit-image 高级图像处理，如边缘检测（Canny）、结构相似性指数（SSIM）、色彩空间转换（如RGB到Lab），直方图匹配
SciPy 科学计算库，可能用于某些图像处理算法或统计,一些滤波器或数学函数

PSNR / SSIM：计算峰值信噪比和结构相似性指数。
LPIPS (Learned Perceptual Image Patch Similarity)： 计算基于深度学习的感知相似性，更符合人眼感受。
Mask IoU (Intersection over Union)：评估两个二值掩码（前景/背景）的重叠程度。
Hausdorff Distance (for binary masks)：衡量两个形状（如掩码边缘）之间最不相似的点到另一个形状的距离，用于评估边缘位移。
ΔE (Delta E)：量化两种颜色在CIELAB空间中的感知差异，CIE76是最简单的版本。

计算两张图的RGB绝对差，取平均，然后可视化。
对两张图分别进行Canny边缘检测，然后计算边缘图的绝对差，可视化。

> —— 摘自原临时缓冲区 L604–L646 ——

PSNR
SSIM
LPIPS
Mask IoU
Hausdorff（像素）
ΔE（CIE76，像素级）
检测到热点数

* PSNR/SSIM 很低 → 由像素级与结构级指标看，两张图在细节或整体表现存在显著差异（可能是色彩、亮度、边缘细节、压缩、局部变形等共同作用）。
* Mask IoU 高 → 虽然细节差异大，但主体整体位置/轮廓大致未丢失（这是好现象）。
* Hausdorff 很高 → 表明某些边缘（例如羽毛边缘或边框）在局部有明显位移或变化；需要重点关注这些边界区域（通常是印刷或 logo 场景最敏感的地方）。
* ΔE 平均/最大偏大 → 颜色偏移显著（需要色彩校正或 ICC 打样）。




### A. 边缘位移 / 轮廓变形（Hausdorff 高）
* **表现**：羽毛边缘、细小线条、边框局部有位移或“锯齿化”。
* **建议修复**：
  1. 对该区域使用更保守的重建：先**保护边缘**（从原图提取高阈值二值边缘作为硬保护 mask），然后对内部应用 SR 或修补；
  2. 或用**手工矢量化（Illustrator）**处理关键 logo / 线稿以保证几何精确；
  3. 若是 SR 导致的伪影，尝试使用另一个 SR 模型（SwinIR 或更保守的 Real-ESRGAN 模式），并减少 scale 或降低细节生成强度（参数调小）。

### B. 色彩偏移 / 色差（ΔE 大）
* **表现**：整体或局部色温/饱和度不同，某些区域颜色显著偏移。
* **建议修复**：
  1. 使用 **Color Transfer（统计色彩匹配）** 在局部热点区域做颜色校正（OpenCV 的 histogram matching，或 scikit-image 的 match_histograms）；
  2. 更专业：用 **ICC profile** 在 Photoshop 中进行软打样并微调（建议拿印厂 ICC），或用 ImageMagick 做批量 CMYK 转换并对比；
  3. 若颜色由 SR 或生成模型引入，限制这些区域为“只做亮度/纹理提升，不改变色相”或手工指定保留原色（mask 条件下进行 SR）。

### C. 纹理伪影 / 生成“虚假细节”
* **表现**：某些纹理看起来“像生成的笔触/噪点”，不是真实细节（hallucination）。
* **建议修复**：
  1. 对关键区域使用**更保守的插值或去噪先行**（先 denoise -> 然后做小倍率 SR）；
  2. 采用**局部 inpainting**（LaMa / Stable Diffusion inpaint）+ 人工微调替换不可信细节；
  3. 如果该区域为品牌元素，**不要用生成模型**来重建其几何/纹理，改为人工修复或矢量化。

### D. 大范围小差异（大量热小点）
* **表现**：很多小点状差异（可能为压缩、抖动或轻微色偏）。
* **建议修复**：
  1. 对图像做全局 color smoothing / tone mapping，或局部 bilateral filter + unsharp mask；
  2. 若这是压缩产生（JPEG artifacts），对热点区域做 artifact reduction（JPEG artifact removal 模型）。


> —— 摘自原临时缓冲区 L735–L744 ——

# 8. 实验设计（A/B 测试建议）

做对比实验并打表（每组至少 N=50 张印花样本）：

* A: `denoise→deblur→SwinIR`
* B: `denoise→SwinIR→ESRGAN_refine`
* C: `Real-ESRGAN single-step`
* D: `SwinIR + diffusion_refine (少量样本)`
  评估：PSNR / SSIM / LPIPS / 专家主观打分（5 个人盲测） + 印花匹配任务（若你有 ground-truth，做纹理相似度评估）。
  建议优先拿 LPIPS + 专家主观作为排序依据（印花场景感知更重要）。

