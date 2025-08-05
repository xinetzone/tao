# 合并多个动态库为单个动态库

在 CMake 中组织多目录源码并合并多个动态库为单个动态库，可通过以下步骤实现。核心思路是利用静态库作为中间产物，最终链接为一个动态库以避免运行时依赖问题：

## 一、项目结构设计
```
project/
├── CMakeLists.txt        # 根目录 CMake 配置
├── module1/
│   ├── CMakeLists.txt    # 模块 1 的 CMake 配置
│   └── src/
│       └── module1.cpp
└── module2/
    ├── CMakeLists.txt    # 模块 2 的 CMake 配置
    └── src/
        └── module2.cpp
```

## 二、模块目录配置（module1/CMakeLists.txt）
```cmake
cmake_minimum_required(VERSION 3.10)
add_library(module1 STATIC src/module1.cpp)  # 生成静态库
target_compile_features(module1 PUBLIC cxx_std_11)
```

## 三、根目录配置（CMakeLists.txt）
```cmake
cmake_minimum_required(VERSION 3.10)
project(MultiLibMerge)

# 添加子模块
add_subdirectory(module1)
add_subdirectory(module2)

# 生成合并后的动态库
add_library(merged SHARED)

# 链接所有静态库并强制包含全部符号
target_link_libraries(merged 
    PUBLIC 
    "-Wl,--whole-archive"  # 包含静态库全部内容
    module1 module2
    "-Wl,--no-whole-archive"  # 恢复默认链接行为
)

# 可选：设置输出路径
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
```

## 四、关键技术解析
1. **静态库作为中间层**
   - 每个模块生成静态库（`STATIC`），避免动态库依赖传递问题
   - 静态库包含完整编译单元，便于后续链接合并

2. **链接器选项控制**
   - `--whole-archive` 强制链接器包含静态库所有目标文件
   - `--no-whole-archive` 恢复默认链接行为，避免后续库被过度链接
   - 此组合确保静态库代码完全合并到动态库中

3. **符号可见性管理**
   - 若静态库中存在隐藏符号（如使用 `__attribute__((visibility("hidden")))`），需在链接时显式导出：
     ```cmake
     target_compile_options(module1 PUBLIC -fvisibility=hidden)
     target_link_libraries(merged PUBLIC -Wl,--export-dynamic)
     ```

## 五、构建与验证
1. 执行构建：
   ```bash
   mkdir build && cd build
   cmake ..
   make
   ```

2. 验证合并结果：
   ```bash
   # 检查动态库依赖（应无外部依赖）
   ldd lib/libmerged.so

   # 查看符号表（应包含 module1/module2 符号）
   nm -D lib/libmerged.so | grep -E "module1|module2"
   ```

## 六、高级场景处理
### 1. 动态库合并（非推荐方案）
若必须保留动态库形式，可通过构建后处理合并：
```cmake
# 根目录 CMakeLists.txt 追加
add_custom_command(
    OUTPUT merged.so
    COMMAND ld -shared -o merged.so module1.so module2.so
    DEPENDS module1.so module2.so
)
add_custom_target(merge ALL DEPENDS merged.so)
```

### 2. 跨平台兼容
```cmake
if(APPLE)
    target_link_libraries(merged PUBLIC "-Wl,-force_load")
else()
    target_link_libraries(merged PUBLIC "-Wl,--whole-archive")
endif()
```

### 3. 符号冲突解决
```cmake
# 在根目录添加
add_link_options(-Wl,--no-undefined)  # 严格检查未定义符号
```

## 七、性能优化建议
1. **选择性导出符号**
   ```cmake
   # 仅导出指定符号
   add_library(merged SHARED)
   target_link_libraries(merged PUBLIC module1 module2)
   add_link_options(-Wl,--version-script=export.map)
   ```

2. **增量编译优化**
   ```cmake
   # 启用预编译头文件
   target_precompile_headers(module1 PUBLIC "module1.h")
   ```

## 八、常见问题排查
1. **未定义引用错误**
   - 检查是否遗漏 `--whole-archive` 选项
   - 确认静态库编译时包含对应源文件

2. **符号重复定义**
   - 使用 `nm` 命令定位冲突符号
   - 添加 `add_compile_options(-fvisibility=hidden)` 隐藏非导出符号

3. **动态库体积过大**
   - 使用 `strip` 工具压缩：
     ```cmake
     install(TARGETS merged POST_BUILD COMMAND strip)
     ```

通过上述方法，可实现多目录源码的模块化管理，并最终生成一个包含所有功能的独立动态库。此方案在保证代码可维护性的同时，解决了动态库依赖传递和符号可见性问题，适用于需要发布单一库文件的场景。