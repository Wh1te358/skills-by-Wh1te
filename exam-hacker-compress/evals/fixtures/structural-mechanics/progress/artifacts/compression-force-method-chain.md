# compression-force-method-chain

终点：得到满足协调条件与整体平衡的原结构最终内力。

1. `step-release-redundant`：解除一个多余约束，形成稳定基本体系。
2. `step-compute-flexibility`：计算外荷载位移与单位未知力柔度系数。
3. `step-write-compatibility`：写出变形协调方程。
4. `step-solve-redundant`：求多余未知力并回代检查。
5. `step-superpose-forces`：恢复约束并叠加得到最终内力。

压缩损失：未展开具体积分；遇到分段、变截面或特殊变形时恢复该部分。
