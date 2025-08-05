# 子项目管理示例

```{toctree}
A-basic/index
B-advanced/index
```

## 项目结构说明

大型项目通常由多个库和二进制文件组成，通过子项目管理可以更好地组织代码结构。

### 包含的示例

- [基础示例](A-basic/index)：包含以下组件
  - 静态库（Static library）
  - 头文件库（Header-only library）
  - 可执行文件（Executable）

```
# 典型子项目结构
project_root/
├── CMakeLists.txt
├── A-basic/
│   ├── CMakeLists.txt
│   ├── include/
│   └── src/
└── B-advanced/
    └── ...
```

## 最佳实践

1. **模块化设计**：每个子项目应有独立的`CMakeLists.txt`
2. **依赖管理**：使用`add_subdirectory()`包含子项目
3. **作用域控制**：通过`PUBLIC/PRIVATE`管理头文件包含路径
4. **构建隔离**：推荐为每个子项目创建独立的构建目录