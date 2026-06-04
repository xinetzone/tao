cmake_minimum_required(VERSION 3.20)
project(HelloPass LANGUAGES CXX)

# Find LLVM (use llvm-config --cmakedir if LLVM_DIR not set)
if(NOT DEFINED LLVM_DIR)
    execute_process(
        COMMAND llvm-config --cmakedir
        OUTPUT_VARIABLE LLVM_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
endif()

find_package(LLVM REQUIRED CONFIG)
message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")

include_directories(${LLVM_INCLUDE_DIRS})
add_definitions(${LLVM_DEFINITIONS})

# Build pass as shared MODULE (symbols resolved at load time by opt/clang)
add_library(HelloPass MODULE src/HelloPass.cpp)
target_compile_features(HelloPass PRIVATE cxx_std_17)
set_target_properties(HelloPass PROPERTIES
    PREFIX ""
    SUFFIX ".so"
)

# No need to link LLVM libraries for a pass plugin
# Symbols are resolved when loaded by opt or clang
