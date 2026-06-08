"""构建产物管理.

提供构建产物的完整性校验和清单管理能力:
- 产物条目 (ArtifactEntry)
- 产物清单 (ArtifactManifest)
- SHA256 校验
- 清单序列化与验证

运行环境要求: Python 3.10+
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .models import compute_sha256


@dataclass
class ArtifactEntry:
    """单个产物条目.
    
    Attributes:
        path: 产物路径 (相对于输出目录)
        sha256: SHA256 哈希值
        size_bytes: 文件大小 (字节)
    """
    path: str
    sha256: str
    size_bytes: int

    @classmethod
    def from_file(
        cls,
        file_path: Path,
        base_dir: Path | None = None,
    ) -> ArtifactEntry:
        """从文件创建产物条目.
        
        Args:
            file_path: 文件路径
            base_dir: 基准目录 (用于计算相对路径), 默认为文件父目录
            
        Returns:
            ArtifactEntry 实例
        """
        if base_dir is None:
            base_dir = file_path.parent

        return cls(
            path=str(file_path.relative_to(base_dir)),
            sha256=compute_sha256(file_path),
            size_bytes=file_path.stat().st_size,
        )


@dataclass
class ArtifactManifest:
    """产物完整性清单.
    
    记录构建产物的元数据和哈希值,用于后续验证产物完整性.
    
    Attributes:
        created_at: 清单创建时间 (ISO 8601)
        run_id: 关联的构建运行 ID
        artifacts: 产物条目列表
        
    Example:
        >>> manifest = ArtifactManifest(
        ...     created_at=datetime.now().isoformat(),
        ...     run_id="build_123",
        ... )
        >>> manifest.artifacts.append(ArtifactEntry.from_file(wheel_path, output_dir))
        >>> manifest.to_json(output_dir / "manifest.json")
        >>> 
        >>> # 后续验证
        >>> success, errors = ArtifactManifest.verify(manifest_path)
        >>> if not success:
        ...     print("校验失败:", errors)
    """

    created_at: str
    run_id: str
    artifacts: list[ArtifactEntry] = field(default_factory=list)

    def add_artifact(
        self,
        file_path: Path,
        base_dir: Path | None = None,
    ) -> ArtifactEntry:
        """添加产物到清单.
        
        Args:
            file_path: 产物文件路径
            base_dir: 基准目录 (用于计算相对路径)
            
        Returns:
            创建的 ArtifactEntry 实例
        """
        entry = ArtifactEntry.from_file(file_path, base_dir)
        self.artifacts.append(entry)
        return entry

    def to_json(self, output_path: Path) -> Path:
        """序列化为 JSON 文件.
        
        Args:
            output_path: 输出文件路径 (父目录会自动创建)
            
        Returns:
            实际写入的文件路径
        """
        data = {
            "created_at": self.created_at,
            "run_id": self.run_id,
            "artifacts": [
                {
                    "path": a.path,
                    "sha256": a.sha256,
                    "size_bytes": a.size_bytes
                }
                for a in self.artifacts
            ],
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return output_path

    @classmethod
    def from_json(cls, manifest_path: Path) -> ArtifactManifest:
        """从 JSON 文件加载清单.
        
        Args:
            manifest_path: JSON 文件路径
            
        Returns:
            ArtifactManifest 实例
            
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON 格式错误
        """
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest = cls(
            created_at=data["created_at"],
            run_id=data["run_id"],
        )
        for artifact_data in data.get("artifacts", []):
            manifest.artifacts.append(ArtifactEntry(
                path=artifact_data["path"],
                sha256=artifact_data["sha256"],
                size_bytes=artifact_data["size_bytes"],
            ))
        return manifest

    @classmethod
    def verify(cls, manifest_path: Path) -> tuple[bool, list[str]]:
        """验证清单中所有产物的完整性.
        
        检查每个产物文件是否存在、SHA256 哈希是否匹配、文件大小是否一致.
        
        Args:
            manifest_path: 清单 JSON 文件路径
            
        Returns:
            (全部通过, 错误列表) 元组
        """
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        base_dir = manifest_path.parent
        errors: list[str] = []

        for entry in data["artifacts"]:
            file_path = base_dir / entry["path"]

            if not file_path.exists():
                errors.append(f"文件缺失: {entry['path']}")
                continue

            actual_hash = compute_sha256(file_path)
            if actual_hash != entry["sha256"]:
                errors.append(
                    f"校验失败: {entry['path']} "
                    f"(期望 {entry['sha256'][:16]}..., 实际 {actual_hash[:16]}...)"
                )

            actual_size = file_path.stat().st_size
            if actual_size != entry["size_bytes"]:
                errors.append(
                    f"大小不符: {entry['path']} "
                    f"(期望 {entry['size_bytes']}, 实际 {actual_size})"
                )

        return (len(errors) == 0, errors)


def generate_checksum_file(file_path: Path) -> Path:
    """为文件生成 SHA256 校验文件.
    
    生成格式与 sha256sum 工具一致: ``<hex>  <filename>\\n``
    
    Args:
        file_path: 要校验的文件路径
        
    Returns:
        校验文件路径 (原文件名 + .sha256)
    """
    sha256_hash = compute_sha256(file_path)
    checksum_file = file_path.with_suffix(file_path.suffix + ".sha256")
    checksum_file.write_text(
        f"{sha256_hash}  {file_path.name}\n",
        encoding="utf-8"
    )
    return checksum_file


def verify_checksum_file(checksum_path: Path) -> tuple[bool, str]:
    """验证 SHA256 校验文件.
    
    Args:
        checksum_path: 校验文件路径 (.sha256)
        
    Returns:
        (是否通过, 消息) 元组
    """
    content = checksum_path.read_text(encoding="utf-8").strip()
    expected_hash, filename = content.split("  ", 1)

    file_path = checksum_path.parent / filename
    if not file_path.exists():
        return (False, f"文件不存在: {filename}")

    actual_hash = compute_sha256(file_path)
    if actual_hash != expected_hash:
        return (
            False,
            f"哈希不匹配: 期望 {expected_hash[:16]}..., 实际 {actual_hash[:16]}..."
        )

    return (True, "校验通过")
