# 简单的例子

这是一个简单但完整的正确 CMakeLists 示例。对于这个程序，有库（`MyLibExample`），包含头文件和源文件，以及应用程序 `MyExample`，包含源文件。

```cmake
# Almost all CMake files should start with this
# You should always specify a range with the newest
# and oldest tested versions of CMake. This will ensure
# you pick up the best policies.
cmake_minimum_required(VERSION 3.15...4.0)

# This is your project statement. You should always list languages;
# Listing the version is nice here since it sets lots of useful variables
project(
  ModernCMakeExample
  VERSION 1.0
  LANGUAGES CXX)

# If you set any CMAKE_ variables, that can go here.
# (But usually don't do this, except maybe for C++ standard)

# Find packages go here.

# You should usually split this into folders, but this is a simple example

# This is a "default" library, and will match the *** variable setting.
# Other common choices are STATIC, SHARED, and MODULE
# Including header files here helps IDEs but is not required.
# Output libname matches target name, with the usual extensions on your system
add_library(MyLibExample simple_lib.cpp simple_lib.hpp)

# Link each target with other targets or add options, etc.

# Adding something we can run - Output name matches target name
add_executable(MyExample simple_example.cpp)

# Make sure you link your targets with this command. It can also link libraries and
# even flags, so linking a target that does not exist will not give a configure-time error.
target_link_libraries(MyExample PRIVATE MyLibExample)
```

完整示例可以在 [examples](https://gitlab.com/CLIUtils/modern-cmake/tree/master/examples/simple-project) 文件夹中找到。

还有更大、多文件的[示例](https://gitlab.com/CLIUtils/modern-cmake/tree/master/examples/extended-project)可供使用。