# DDPV Scripts


## gen_fib 生成数据集

运行方式： ```python3 gen_fib.py <input> <output> [-nprefix x] [-prefix x] [-layers x] [-decompose x]```

参数说明：
- `input`: 拓扑文件路径。
- `output`: 输出路径，若路径不存在会自动创建。
- `-nprefix x`: (可选) 为每个设备分配x条IP网段，默认为1。
- `-prefix x`: (可选) 设置每个IP网段的前缀长度为x，默认为24。
- `-layers x`: (可选) 将部分生成的rule进行放大，与其他rule产生x层的交集，默认为0。
- `-decompose x`: (可选) 将最终生成的rule分解x次，例如前缀长度为24的分解1次会变成2个25长度的，分解2次分变成4个26长度的，即最终rule数量会变成2^x倍。默认为0。

其他说明：
- 最终还会在`output`中生成`1.space`文件，表示每个设备的IP范围。
- 若layers>=1，建议nprefix设置为`2^layers`的整数倍，以保证能够生成目的重叠数的rule。
- `0` <= `prefix-layers` <= `prefix` <= `prefix + decompose` <= `32`