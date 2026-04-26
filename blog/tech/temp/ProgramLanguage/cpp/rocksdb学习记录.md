---
title: RocksDB 学习记录
published: 2025-04-28
description: RocksDB 入门学习路径、核心概念与实践排查清单。
tags:
  - 编程语言
  - cpp
  - rocksdb
category: 编程基础
draft: false
image: ""
pinned: false
---

# RocksDB 学习记录

## 官方入口

- 官方博客：<https://rocksdb.org/blog/>
- 官方文档主页：<https://rocksdb.org/>

## 学习主线

1. 先理解 LSM Tree 结构，再看 RocksDB 的实现细节。
2. 重点掌握 `MemTable`、`SSTable`、`Compaction`、`WAL`。
3. 关注读放大、写放大、空间放大的权衡关系。

## 实践关注点

- 写入路径：`Put` 到落盘的关键阶段与失败恢复。
- 读路径：Block Cache、Bloom Filter 对命中率的影响。
- 压缩策略：不同层级的压缩触发条件与资源开销。
- 参数调优：根据业务读写比选择 compaction 风格。

## 后续补充计划

- 增加一个最小可运行 demo（含基本读写和参数说明）。
- 记录常见监控指标与线上故障排查路径。