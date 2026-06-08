"""Nuitka 编译器参数生成器.

提供 Nuitka 编译配置的完整抽象层，覆盖 Nuitka 实际命令行选项。
基于 Nuitka 源码 (nuitka/options/OptionParsing.py) 设计。

主要功能:
- 编译模式: module/standalone/onefile/accelerated/app/app-dist/package
- 编译器选择: clang/gcc/msvc/mingw64/zig
- 插件管理: enabled/disabled/user plugins
- 输出控制: 输出目录/文件名/清理选项
- 数据文件: package_data/data_files/data_dirs
- 导入跟踪: follow_imports/nofollow_imports/follow_stdlib
- 高级选项: LTO/PGO/缓存/并行编译
- 平台特定: Windows 图标/控制台模式、macOS 应用包

运行环境要求: Python 3.10+

Example:
    >>> from flowkit.nuitka_config import NuitkaConfig
    >>> config = NuitkaConfig(
    ...     mode="standalone",
    ...     compiler="clang",
    ...     include_packages=["mypackage"],
    ...     follow_imports=["mypackage"],
    ...     output_dir="./dist",
    ... )
    >>> args = config.to_args()
    >>> print(args)
    ['--mode=standalone', '--clang', '--include-package=mypackage', ...]
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# 编译模式常量
NuitkaMode = Literal[
    "module",       # 编译为扩展模块
    "package",      # 编译整个包为扩展模块
    "standalone",   # 独立可执行文件 (含依赖文件夹)
    "onefile",      # 单文件自解压可执行文件
    "accelerated",  # 加速模式 (依赖系统 Python)
    "app",          # 应用 (onefile 或 macOS 应用包)
    "app-dist",     # 应用分发 (standalone 或 macOS 应用包)
    "dll",          # DLL 模式 (实验性)
]

# 编译器常量
NuitkaCompiler = Literal[
    "clang",    # LLVM Clang
    "gcc",      # GNU GCC (默认非 Windows)
    "msvc",     # Microsoft Visual C++ (Windows)
    "mingw64",  # MinGW-w64 (Windows)
    "zig",      # Zig 编译器
    "auto",     # 自动选择
]

# 插件名称类型
PluginName = str


@dataclass(frozen=True)
class OutputConfig:
    """输出配置.
    
    Attributes:
        output_dir: 输出目录 (--output-dir)
        output_filename: 输出文件名 (--output-filename, -o)
        output_folder_name: 分发文件夹名 (--output-folder-name)
        remove_build: 编译后删除构建目录 (--remove-output)
        pyi_file: 生成 .pyi 文件 (默认 False, --no-pyi-file 禁用)
        pyi_stubs: 使用 stubgen 生成 .pyi (默认 True, --no-pyi-stubs 禁用)
    
    Note:
        默认情况下不输出任何标志，通过 extra_flags 控制。
        如需显式控制，设置 remove_build=True 或 pyi_file=False。
    """
    output_dir: str | None = None
    output_filename: str | None = None
    output_folder_name: str | None = None
    remove_build: bool = False
    pyi_file: bool = True
    pyi_stubs: bool = True


@dataclass(frozen=True)
class DataConfig:
    """数据文件配置.
    
    Attributes:
        package_data: 包含的包数据 (--include-package-data)
            格式: "package_name" 或 "package_name:pattern"
        data_files: 包含的数据文件 (--include-data-files)
            格式: "/path/to/file=dest/" 或 "/path/*.txt=folder/"
        data_dirs: 包含的数据目录 (--include-data-dir)
            格式: "/path/to/dir=dest_dir"
        noinclude_data_files: 排除的数据文件模式 (--noinclude-data-files)
        raw_dirs: 包含的原始目录 (--include-raw-dir)
    """
    package_data: list[str] = field(default_factory=list)
    data_files: list[str] = field(default_factory=list)
    data_dirs: list[str] = field(default_factory=list)
    noinclude_data_files: list[str] = field(default_factory=list)
    raw_dirs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CompilerConfig:
    """编译器高级配置.
    
    Attributes:
        jobs: 并行编译任务数 (--jobs, -j)
            None=自动, 正数=指定数, 负数=CPU数减去该值
        lto: 链接时优化 (--lto)
            "auto" | "yes" | "no"
        static_libpython: 静态链接 libpython (--static-libpython)
            "auto" | "yes" | "no"
        reproducible: 可重复构建 (--reproducible)
            "auto" | "yes" | "no"
        cf_protection: CF 保护模式 (--cf-protection, GCC only)
            "auto" | "full" | "branch" | "return" | "none" | "check"
        low_memory: 低内存模式 (--low-memory)
        msvc_version: MSVC 版本 (--msvc, Windows only)
            如 "14.3", "latest", "list"
    """
    jobs: int | None = None
    lto: Literal["auto", "yes", "no"] = "auto"
    static_libpython: Literal["auto", "yes", "no"] = "auto"
    reproducible: Literal["auto", "yes", "no"] = "auto"
    cf_protection: Literal["auto", "full", "branch", "return", "none", "check"] = "auto"
    low_memory: bool = False
    msvc_version: str | None = None


@dataclass(frozen=True)
class CacheConfig:
    """缓存配置.
    
    Attributes:
        disabled_caches: 禁用的缓存列表 (--disable-cache)
            可选值: "all", "ccache", "bytecode", "compression", "dll-dependencies"
        clean_caches: 编译前清理的缓存列表 (--clean-cache)
    """
    disabled_caches: list[str] = field(default_factory=list)
    clean_caches: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class WindowsConfig:
    """Windows 特定配置.
    
    Attributes:
        icon_path: 图标路径列表 (--windows-icon-from-ico)
        icon_exe_path: 从 EXE 复制图标 (--windows-icon-from-exe)
        console_mode: 控制台模式 (--windows-console-mode)
            "force" | "disable" | "attach" | "hide"
        uac_admin: 请求管理员权限 (--windows-uac-admin)
        uac_uiaccess: 请求 UIAccess (--windows-uac-uiaccess)
        force_stdout_spec: 强制标准输出位置 (--force-stdout-spec)
        force_stderr_spec: 强制标准错误位置 (--force-stderr-spec)
    """
    icon_path: list[str] = field(default_factory=list)
    icon_exe_path: str | None = None
    console_mode: Literal["force", "disable", "attach", "hide"] | None = None
    uac_admin: bool = False
    uac_uiaccess: bool = False
    force_stdout_spec: str | None = None
    force_stderr_spec: str | None = None


@dataclass(frozen=True)
class MacOSConfig:
    """macOS 特定配置.
    
    Attributes:
        create_bundle: 创建应用包 (--macos-create-app-bundle)
        app_name: 应用名称 (--macos-app-name)
        app_version: 应用版本 (--macos-app-version)
        app_icon_path: 应用图标路径 (--macos-app-icon)
        app_mode: 应用模式 (--macos-app-mode)
            "gui" | "background" | "ui-element"
        target_arch: 目标架构 (--macos-target-arch)
            "arm64" | "x86_64"
        create_dmg: 创建 DMG (--macos-app-create-dmg)
        signed_app_name: 签名应用名 (--macos-signed-app-name)
        sign_identity: 签名身份 (--macos-sign-identity)
    """
    create_bundle: bool = False
    app_name: str | None = None
    app_version: str | None = None
    app_icon_path: list[str] = field(default_factory=list)
    app_mode: Literal["gui", "background", "ui-element"] | None = None
    target_arch: Literal["arm64", "x86_64"] | None = None
    create_dmg: bool = False
    signed_app_name: str | None = None
    sign_identity: str | None = None


@dataclass(frozen=True)
class VersionInfo:
    """二进制版本信息.
    
    Attributes:
        company_name: 公司名称 (--company-name)
        product_name: 产品名称 (--product-name)
        file_version: 文件版本 (--file-version), 如 "1.0.0.0"
        product_version: 产品版本 (--product-version)
        file_description: 文件描述 (--file-description)
        copyright_text: 版权信息 (--copyright)
        trademarks: 商标信息 (--trademarks)
    """
    company_name: str | None = None
    product_name: str | None = None
    file_version: str | None = None
    product_version: str | None = None
    file_description: str | None = None
    copyright_text: str | None = None
    trademarks: str | None = None


@dataclass(frozen=True)
class NuitkaConfig:
    """Nuitka 编译配置.
    
    封装 Nuitka 编译器的所有参数，提供 to_args() 方法生成命令行参数。
    
    Attributes:
        mode: 编译模式 (默认 "module")
        compiler: C 编译器 (默认 "clang")
        
        # 插件管理
        enabled_plugins: 启用的插件列表 (--enable-plugins)
            标准插件: dill-compat, numpy, torch, tensorflow, pyqt5, pyside2,
                     matplotlib, kivy, tkinter, gevent, eventlet, trio 等
        disabled_plugins: 禁用的插件列表 (--disable-plugins)
        user_plugins: 用户插件路径列表 (--user-plugin)
        
        # 导入控制
        follow_imports: 跟踪导入的包 (--follow-import-to)
        nofollow_imports: 不跟踪导入的包 (--nofollow-import-to)
            支持模式: "*.tests", "mypackage.submodule"
        follow_all: 跟踪所有导入 (--follow-imports / --nofollow-imports)
            None=默认 (standalone 时为 True), True=强制, False=禁用
        follow_stdlib: 跟踪标准库 (--follow-stdlib)
        
        # 包/模块包含
        include_packages: 包含的包 (--include-package)
            自动包含包数据 (--include-package-data)
        include_modules: 包含的模块 (--include-module)
        include_plugin_dirs: 额外插件目录 (--include-plugin-directory)
        include_plugin_files: 插件文件模式 (--include-plugin-files)
        
        # 数据文件 (通过 DataConfig)
        data: 数据文件配置
        
        # 输出控制 (通过 OutputConfig)
        output: 输出配置
        
        # 编译器高级配置 (通过 CompilerConfig)
        compiler_config: 编译器配置
        
        # 缓存配置 (通过 CacheConfig)
        cache: 缓存配置
        
        # 平台特定配置
        windows: Windows 配置
        macos: macOS 配置
        
        # 版本信息
        version_info: 版本信息配置
        
        # 其他选项
        python_flags: Python 标志列表 (--python-flag)
            可选: "no_site", "static_hashes", "no_warnings", "no_asserts",
                  "no_docstrings", "unbuffered", "isolated", "safe_path", "package"
        deployment: 部署模式 (--deployment)
        assume_yes_for_downloads: 自动确认下载 (--assume-yes-for-downloads)
        quiet: 安静模式 (--quiet)
        verbose: 详细输出 (--verbose)
        show_scons: 显示 Scons 输出 (--show-scons)
        report_filename: 编译报告文件 (--report)
        extra_flags: 额外编译标志 (直接追加到命令行)
        
    Example:
        >>> config = NuitkaConfig(
        ...     mode="standalone",
        ...     compiler="clang",
        ...     include_packages=["mypackage"],
        ...     follow_imports=["mypackage"],
        ...     output=OutputConfig(output_dir="./dist"),
        ...     enabled_plugins=["dill-compat"],
        ... )
        >>> args = config.to_args()
        >>> print(args)
        ['--mode=standalone', '--clang', '--include-package=mypackage', ...]
    """

    # 基本配置
    mode: NuitkaMode = "module"
    compiler: NuitkaCompiler = "clang"

    # 插件管理
    enabled_plugins: list[PluginName] = field(default_factory=lambda: ["dill-compat"])
    disabled_plugins: list[PluginName] = field(default_factory=list)
    user_plugins: list[str] = field(default_factory=list)

    # 导入控制
    follow_imports: list[str] = field(default_factory=list)
    nofollow_imports: list[str] = field(default_factory=list)
    follow_all: bool | None = None
    follow_stdlib: bool = False

    # 包/模块包含
    include_packages: list[str] = field(default_factory=list)
    include_modules: list[str] = field(default_factory=list)
    include_plugin_dirs: list[str] = field(default_factory=list)
    include_plugin_files: list[str] = field(default_factory=list)

    # 子配置 (使用默认实例)
    data: DataConfig = field(default_factory=DataConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    compiler_config: CompilerConfig = field(default_factory=CompilerConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    windows: WindowsConfig = field(default_factory=WindowsConfig)
    macos: MacOSConfig = field(default_factory=MacOSConfig)
    version_info: VersionInfo = field(default_factory=VersionInfo)

    # 其他选项
    python_flags: list[str] = field(default_factory=list)
    deployment: bool = False
    assume_yes_for_downloads: bool = False
    quiet: bool = False
    verbose: bool = False
    show_scons: bool = False
    report_filename: str | None = None
    extra_flags: list[str] = field(default_factory=lambda: ["--remove-output", "--no-pyi-file"])

    def to_args(self) -> list[str]:
        """生成 Nuitka 命令行参数列表.
        
        Returns:
            命令行参数列表，可直接传递给 subprocess.run()
        """
        args: list[str] = []

        # === 基本配置 ===
        args.append(f"--mode={self.mode}")

        # 编译器选择
        if self.compiler == "clang":
            args.append("--clang")
        elif self.compiler == "mingw64":
            args.append("--mingw64")
        elif self.compiler == "zig":
            args.append("--zig")
        elif self.compiler == "msvc":
            if self.compiler_config.msvc_version:
                args.append(f"--msvc={self.compiler_config.msvc_version}")
            else:
                args.append("--msvc=latest")
        # gcc 和 auto 不需要显式标志

        # === 插件管理 ===
        for p in self.enabled_plugins:
            args.append(f"--enable-plugin={p}")
        for p in self.disabled_plugins:
            args.append(f"--disable-plugin={p}")
        for p in self.user_plugins:
            args.append(f"--user-plugin={p}")

        # === 导入控制 ===
        for pkg in self.follow_imports:
            args.append(f"--follow-import-to={pkg}")
        for pkg in self.nofollow_imports:
            args.append(f"--nofollow-import-to={pkg}")
        if self.follow_all is True:
            args.append("--follow-imports")
        elif self.follow_all is False:
            args.append("--nofollow-imports")
        if self.follow_stdlib:
            args.append("--follow-stdlib")

        # === 包/模块包含 ===
        for pkg in self.include_packages:
            args.append(f"--include-package={pkg}")
            # 同时包含包数据
            args.append(f"--include-package-data={pkg}")
        for mod in self.include_modules:
            args.append(f"--include-module={mod}")
        for d in self.include_plugin_dirs:
            args.append(f"--include-plugin-directory={d}")
        for f in self.include_plugin_files:
            args.append(f"--include-plugin-files={f}")

        # === 数据文件 ===
        for pd in self.data.package_data:
            args.append(f"--include-package-data={pd}")
        for df in self.data.data_files:
            args.append(f"--include-data-files={df}")
        for dd in self.data.data_dirs:
            args.append(f"--include-data-dir={dd}")
        for nd in self.data.noinclude_data_files:
            args.append(f"--noinclude-data-files={nd}")
        for rd in self.data.raw_dirs:
            args.append(f"--include-raw-dir={rd}")

        # === 输出配置 ===
        if self.output.output_dir:
            args.append(f"--output-dir={self.output.output_dir}")
        if self.output.output_filename:
            args.append(f"--output-filename={self.output.output_filename}")
        if self.output.output_folder_name:
            args.append(f"--output-folder-name={self.output.output_folder_name}")
        if self.output.remove_build:
            args.append("--remove-output")
        if not self.output.pyi_file:
            args.append("--no-pyi-file")
        if not self.output.pyi_stubs:
            args.append("--no-pyi-stubs")

        # === 编译器高级配置 ===
        cc = self.compiler_config
        if cc.jobs is not None:
            args.append(f"--jobs={cc.jobs}")
        if cc.lto != "auto":
            args.append(f"--lto={cc.lto}")
        if cc.static_libpython != "auto":
            args.append(f"--static-libpython={cc.static_libpython}")
        if cc.reproducible != "auto":
            args.append(f"--reproducible={cc.reproducible}")
        if cc.cf_protection != "auto":
            args.append(f"--cf-protection={cc.cf_protection}")
        if cc.low_memory:
            args.append("--low-memory")

        # === 缓存配置 ===
        for c in self.cache.disabled_caches:
            args.append(f"--disable-cache={c}")
        for c in self.cache.clean_caches:
            args.append(f"--clean-cache={c}")

        # === Windows 配置 ===
        win = self.windows
        for icon in win.icon_path:
            args.append(f"--windows-icon-from-ico={icon}")
        if win.icon_exe_path:
            args.append(f"--windows-icon-from-exe={win.icon_exe_path}")
        if win.console_mode:
            args.append(f"--windows-console-mode={win.console_mode}")
        if win.uac_admin:
            args.append("--windows-uac-admin")
        if win.uac_uiaccess:
            args.append("--windows-uac-uiaccess")
        if win.force_stdout_spec:
            args.append(f"--force-stdout-spec={win.force_stdout_spec}")
        if win.force_stderr_spec:
            args.append(f"--force-stderr-spec={win.force_stderr_spec}")

        # === macOS 配置 ===
        mac = self.macos
        if mac.create_bundle:
            args.append("--macos-create-app-bundle")
        if mac.app_name:
            args.append(f"--macos-app-name={mac.app_name}")
        if mac.app_version:
            args.append(f"--macos-app-version={mac.app_version}")
        for icon in mac.app_icon_path:
            args.append(f"--macos-app-icon={icon}")
        if mac.app_mode:
            args.append(f"--macos-app-mode={mac.app_mode}")
        if mac.target_arch:
            args.append(f"--macos-target-arch={mac.target_arch}")
        if mac.create_dmg:
            args.append("--macos-app-create-dmg")
        if mac.signed_app_name:
            args.append(f"--macos-signed-app-name={mac.signed_app_name}")
        if mac.sign_identity:
            args.append(f"--macos-sign-identity={mac.sign_identity}")

        # === 版本信息 ===
        vi = self.version_info
        if vi.company_name:
            args.append(f"--company-name={vi.company_name}")
        if vi.product_name:
            args.append(f"--product-name={vi.product_name}")
        if vi.file_version:
            args.append(f"--file-version={vi.file_version}")
        if vi.product_version:
            args.append(f"--product-version={vi.product_version}")
        if vi.file_description:
            args.append(f"--file-description={vi.file_description}")
        if vi.copyright_text:
            args.append(f"--copyright={vi.copyright_text}")
        if vi.trademarks:
            args.append(f"--trademarks={vi.trademarks}")

        # === 其他选项 ===
        for flag in self.python_flags:
            args.append(f"--python-flag={flag}")
        if self.deployment:
            args.append("--deployment")
        if self.assume_yes_for_downloads:
            args.append("--assume-yes-for-downloads")
        if self.quiet:
            args.append("--quiet")
        if self.verbose:
            args.append("--verbose")
        if self.show_scons:
            args.append("--show-scons")
        if self.report_filename:
            args.append(f"--report={self.report_filename}")

        # 额外标志 (直接追加)
        args.extend(self.extra_flags)

        return args

    @property
    def jobs(self) -> int | None:
        """向后兼容: 返回 jobs 配置."""
        return self.compiler_config.jobs

    @property
    def plugins(self) -> list[PluginName]:
        """向后兼容: 返回启用的插件列表."""
        return list(self.enabled_plugins)

    def with_output(self, output_dir: str) -> NuitkaConfig:
        """创建带输出目录配置的新实例.
        
        Args:
            output_dir: 输出目录路径
            
        Returns:
            新的 NuitkaConfig 实例
        """
        new_output = OutputConfig(
            output_dir=output_dir,
            output_filename=self.output.output_filename,
            output_folder_name=self.output.output_folder_name,
            remove_build=self.output.remove_build,
            pyi_file=self.output.pyi_file,
            pyi_stubs=self.output.pyi_stubs,
        )
        return NuitkaConfig(
            mode=self.mode,
            compiler=self.compiler,
            enabled_plugins=self.enabled_plugins,
            disabled_plugins=self.disabled_plugins,
            user_plugins=self.user_plugins,
            follow_imports=self.follow_imports,
            nofollow_imports=self.nofollow_imports,
            follow_all=self.follow_all,
            follow_stdlib=self.follow_stdlib,
            include_packages=self.include_packages,
            include_modules=self.include_modules,
            include_plugin_dirs=self.include_plugin_dirs,
            include_plugin_files=self.include_plugin_files,
            data=self.data,
            output=new_output,
            compiler_config=self.compiler_config,
            cache=self.cache,
            windows=self.windows,
            macos=self.macos,
            version_info=self.version_info,
            python_flags=self.python_flags,
            deployment=self.deployment,
            assume_yes_for_downloads=self.assume_yes_for_downloads,
            quiet=self.quiet,
            verbose=self.verbose,
            show_scons=self.show_scons,
            report_filename=self.report_filename,
            extra_flags=self.extra_flags,
        )

    def with_jobs(self, jobs: int) -> NuitkaConfig:
        """创建带并行任务数的新实例.
        
        Args:
            jobs: 并行编译任务数
            
        Returns:
            新的 NuitkaConfig 实例
        """
        new_cc = CompilerConfig(
            jobs=jobs,
            lto=self.compiler_config.lto,
            static_libpython=self.compiler_config.static_libpython,
            reproducible=self.compiler_config.reproducible,
            cf_protection=self.compiler_config.cf_protection,
            low_memory=self.compiler_config.low_memory,
            msvc_version=self.compiler_config.msvc_version,
        )
        return NuitkaConfig(
            mode=self.mode,
            compiler=self.compiler,
            enabled_plugins=self.enabled_plugins,
            disabled_plugins=self.disabled_plugins,
            user_plugins=self.user_plugins,
            follow_imports=self.follow_imports,
            nofollow_imports=self.nofollow_imports,
            follow_all=self.follow_all,
            follow_stdlib=self.follow_stdlib,
            include_packages=self.include_packages,
            include_modules=self.include_modules,
            include_plugin_dirs=self.include_plugin_dirs,
            include_plugin_files=self.include_plugin_files,
            data=self.data,
            output=self.output,
            compiler_config=new_cc,
            cache=self.cache,
            windows=self.windows,
            macos=self.macos,
            version_info=self.version_info,
            python_flags=self.python_flags,
            deployment=self.deployment,
            assume_yes_for_downloads=self.assume_yes_for_downloads,
            quiet=self.quiet,
            verbose=self.verbose,
            show_scons=self.show_scons,
            report_filename=self.report_filename,
            extra_flags=self.extra_flags,
        )


def _merge_lists(a: list, b: list) -> list:
    """合并两个列表，去重保持顺序."""
    result = list(a)
    for item in b:
        if item not in result:
            result.append(item)
    return result


# ---------------------------------------------------------------------------
# 预定义配置模板
# ---------------------------------------------------------------------------

NUITKA_MODULE = NuitkaConfig(
    mode="module",
    compiler="clang",
    enabled_plugins=["dill-compat"],
    extra_flags=["--remove-output", "--no-pyi-file"],
)

NUITKA_STANDALONE = NuitkaConfig(
    mode="standalone",
    compiler="clang",
    enabled_plugins=["dill-compat"],
    extra_flags=["--remove-output", "--no-pyi-file"],
)

NUITKA_ONEFILE = NuitkaConfig(
    mode="onefile",
    compiler="clang",
    enabled_plugins=["dill-compat"],
    extra_flags=["--remove-output", "--no-pyi-file"],
)

NUITKA_ACCELERATED = NuitkaConfig(
    mode="accelerated",
    compiler="clang",
    enabled_plugins=["dill-compat"],
    extra_flags=[],
)

NUITKA_APP = NuitkaConfig(
    mode="app",
    compiler="clang",
    enabled_plugins=["dill-compat"],
    extra_flags=["--remove-output"],
)


# ---------------------------------------------------------------------------
# 标准插件列表 (来自 Nuitka 源码 nuitka/plugins/standard/)
# ---------------------------------------------------------------------------

#: Nuitka 标准插件列表
STANDARD_PLUGINS = [
    "anti-bloat",           # 减少包体积
    "consider-pylint",      # 考虑 pylint 注解
    "data-files",           # 数据文件处理
    "delvewheel",           # Delvewheel 支持
    "dill-compat",          # dill 序列化兼容
    "dll-files",            # DLL 文件处理
    "enum",                 # Enum 优化
    "eventlet",             # Eventlet 支持
    "gevent",               # Gevent 支持
    "gi",                   # GObject Introspection
    "glfw",                 # GLFW 支持
    "implicit-imports",     # 隐式导入检测
    "kivy",                 # Kivy 支持
    "matplotlib",           # Matplotlib 支持
    "multiprocessing",      # Multiprocessing 支持
    "numpy",                # NumPy 支持
    "options-nanny",        # 选项检查
    "pbr",                  # PBR 支持
    "pkg-resources",        # pkg_resources 支持
    "playwright",           # Playwright 支持
    "pmw",                  # Pmw 支持
    "pyqt5",                # PyQt5 支持
    "pyside2",              # PySide2 支持
    "pyside6",              # PySide6 支持
    "pywebview",            # PyWebView 支持
    "source-inclusion",     # 源码包含
    "spacy",                # spaCy 支持
    "tensorflow",           # TensorFlow 支持
    "tkinter",              # Tkinter 支持
    "torch",                # PyTorch 支持
    "torch-hub",            # Torch Hub 支持
    "torch-jit",            # Torch JIT 支持
    "transformers",         # Transformers 支持
    "trio",                 # Trio 支持
    "upx",                  # UPX 压缩
]

#: 常用插件子集
COMMON_PLUGINS = [
    "dill-compat",
    "anti-bloat",
    "implicit-imports",
]


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def build_nuitka_command(
    config: NuitkaConfig,
    main_module: str,
    *,
    dry_run: bool = False,
) -> list[str]:
    """构建完整的 Nuitka 命令行命令.
    
    Args:
        config: Nuitka 编译配置
        main_module: 主模块路径 (如 "mypackage" 或 "main.py")
        dry_run: 如果为 True，添加 --generate-c-only 标志
        
    Returns:
        完整的命令行参数列表，格式: ["python", "-m", "nuitka", ...args, main_module]
        
    Example:
        >>> config = NuitkaConfig(mode="standalone", include_packages=["tvm"])
        >>> cmd = build_nuitka_command(config, "tvm")
        >>> print(cmd)
        ['python', '-m', 'nuitka', '--mode=standalone', ..., 'tvm']
    """
    cmd = ["python", "-m", "nuitka"]
    cmd.extend(config.to_args())
    if dry_run:
        cmd.append("--generate-c-only")
    cmd.append(main_module)
    return cmd


def parse_nuitka_version(version_output: str) -> tuple[int, int, int]:
    """解析 Nuitka 版本号.
    
    Args:
        version_output: nuitka --version 的输出
        
    Returns:
        (major, minor, patch) 版本元组
    """
    import re
    match = re.search(r"Nuitka.*?(\d+)\.(\d+)\.(\d+)", version_output)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return (0, 0, 0)
