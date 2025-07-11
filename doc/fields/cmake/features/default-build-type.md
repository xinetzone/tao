# 默认构建类型

CMake 通常执行“非发布、非调试”的空构建类型；如果你希望自行设置默认构建类型，可以参考 [Kitware 博客](https://blog.kitware.com/cmake-and-the-default-build-type/)中修改后的默认构建类型配方：

```cmake
set(default_build_type "Release")
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to '${default_build_type}' as none was specified.")
  set(CMAKE_BUILD_TYPE "${default_build_type}" CACHE
      STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
    "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()
```
