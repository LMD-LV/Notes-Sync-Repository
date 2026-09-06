---
tags: [CV, 速览]
created: 2026-09-06
status: 整理中
domain: CV
source: 个人总结
---

# CV 印花模型清单(优先级 + 用途)

> [!note] 抽取说明
> 2026-09-06 自 [[CV-印花流水线方案]] 与 [[模型调研]] 的逐字重复清单(414 字)抽取为公共笔记,两处已改为回链。原文照录:

* **分析/分割**：CLIP（分类）、U²-Net / MODNet（抠图）、SAM（Segment Anything）
* **降噪**：BM3D（传统，快速）、DnCNN（轻量）、Restormer（真实噪声）
* **去模糊**：Restormer、DeblurGAN-v2、MPRNet、DeblurDiffusion（视推理成本）
* **超分（保真）**：SwinIR（Transformer-based，结构保持好）
* **超分（感知/纹理）**：ESRGAN / Real-ESRGAN / ESRGAN+（生成细节）
* **超分（超高倍率/细节合成）**：Diffusion SR（如 SR3、DiffFNO）——慢但质量上限高
* **后处理/低光**：Zero-DCE / EnlightenGAN（亮度增强）、LaMa（inpainting）、Poisson blending（融合）
* **评价指标**：PSNR、SSIM、LPIPS、NIQE、FFT-based high-frequency similarity
