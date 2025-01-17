# dup_finder

## 简介
`dup_finder` 是一个用于查找并处理重复文件的 Python 工具。它可以通过计算文件的哈希值来识别重复文件，并根据指定的优先级规则保留某些文件，同时对其他文件执行删除或移动操作。

## 功能特性
- **查找重复文件**：通过文件大小和哈希值（SHA-256）唯一标识文件，查找给定目录中的重复文件。对于哈希值相同但文件大小不同的文件，全部保留并打印出来，进行手动甄别。
- **优先级排序**：根据文件路径、修改时间等条件为文件分配优先级，确保重要文件被保留。
- **关键字过滤**：支持通过关键字筛选需要保留的文件。
- **灵活处理**：可以选择删除或移动重复文件，支持自定义移动目标目录。
- **命令行工具**：提供简单易用的命令行接口，方便集成到自动化脚本中。

## 技术栈
- 编程语言：Python 3.x
- 标准库模块：`os`, `hashlib`, `argparse`, `shutil`, `time`

## 安装
1. 克隆仓库：
   ```bash
   git clone https://github.com/your-repo/dup_finder.git
   cd dup_finder
   ```

2. 安装依赖（如果有额外依赖，可以添加到 `requirements.txt` 并安装）：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法
### 命令行参数
`dup_finder` 提供了多种命令行参数以满足不同需求：

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| `directories` | 必选 | 需要查找重复文件的目录列表 |
| `--keyword` | 可选 | 关键字，包含该关键字的文件将被优先保留 |
| `--action` | 可选，默认为 `move` | 对重复文件执行的操作，可选值为 `delete` 或 `move` |
| `--priority-order` | 可选 | 自定义优先级顺序，可选内容为 `modified_time path`。modified_time优先是考虑最新修改过的文件可能是最有保留价值的文件， path是文件完整路径，层数多的文件可能做了更细的整理。实际结合自己文件的情况，做对应的修改。 |
| `--move-to-dir` | 可选 | 移动文件的目标目录 |
| `--try-run, -n` | 可选 | 尝试运行模式：仅打印操作，不实际执行 |

   ```
   $ python dup_finder.py mock -h 
   usage: dup_finder.py [-h] [--keyword KEYWORD] [--action {delete,move}]
                        [--priority-order PRIORITY_ORDER [PRIORITY_ORDER ...]]
                        [--move-to-dir MOVE_TO_DIR] [--try-run]
                        directories [directories ...]

   Find and process duplicate files.

   positional arguments:
   directories           Directories to search for duplicate files

   optional arguments:
   -h, --help            show this help message and exit
   --keyword KEYWORD     Keyword to retain files
   --action {delete,move}
                           Action to process files (default: move)
   --priority-order PRIORITY_ORDER [PRIORITY_ORDER ...]
                           Custom priority order: modified_time, path
   --move-to-dir MOVE_TO_DIR
                           Directory to move files to (if not specified, rename
                           files with .dup_finder suffix)
   --try-run, -n         Try run mode: only print actions without executing
                           them
   ```


### 示例
1. 查找并移动重复文件到指定目录：
   ```bash
   python dup_finder.py /path/to/dir1 /path/to/dir2 --action move --move-to-dir /path/to/move_dir
   ```

2. 查找并删除重复文件，保留包含特定关键字的文件：
   ```bash
   python dup_finder.py /path/to/dir1 --keyword important --action delete
   ```

3. 使用自定义优先级顺序查找并处理重复文件：
   ```bash
   python dup_finder.py /path/to/dir1 --priority-order modified_time path --action move
   ```

4. 尝试运行模式，仅打印操作，不实际执行：
   ```bash
   python dup_finder.py /path/to/dir1 --try-run
   ```

5. 使用简写形式尝试运行模式：
   ```bash
   python dup_finder.py /path/to/dir1 -n
   ```

## 贡献
欢迎贡献代码！请阅读 [贡献指南](CONTRIBUTING.md) 以了解如何参与开发。

## 许可证
本项目采用 GPL-3.0 许可证，详情参见 [LICENSE](LICENSE) 文件。

---

希望这个 README 文件能帮助你更好地理解和使用 `dup_finder`。如果有任何问题或建议，请随时提 issue 或者联系开发者。