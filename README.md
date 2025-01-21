# dup_finder

## 简介
`dup_finder` 是一个用于查找并处理重复文件的 Python 工具。它可以通过计算文件的哈希值来识别重复文件，并根据指定的保留优先级规则（修改时间、路径等）保留惟一文件，同时根据需求对其他重复文件执行删除或移动操作。

## 功能特性
- **查找重复文件**：通过文件大小和哈希值（SHA-256）唯一标识文件，查找给定目录中的重复文件。对于哈希值相同但文件大小不同的文件，全部保留并打印出来，进行手动甄别。
- **优先级排序**：根据文件路径、修改时间等条件为文件分配优先级，确保重要文件被保留。
- **关键字过滤**：支持通过关键字筛选需要保留的文件。
- **灵活处理**：可以选择删除或移动重复文件，支持自定义移动目标目录。
- **命令行工具**：提供简单易用的命令行接口，方便集成到自动化脚本中。
- **保存文件信息**：将 `file_dict` 的内容按当前日期时间保留下来，以备后查。
- **生成文件**：程序执行时会生成以下文件：
  - `file_cache.json`：用于缓存文件信息，以便后续查找重复文件时提高效率。
  - `duplicates_YYYYMMDD_HHMMSS.json`：记录每次查找重复文件的结果，文件名中的时间戳表示生成时间。

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
| `-d, --directories` | 必选 | 查找重复文件的目录，可以输入多个目录，以空格分隔 |
| `--exclude` | 可选 | 排除关键字，包含该关键字的文件将被排除在处理结果外 |
| `--exclude-file` | 可选 | 同上，但将排除关键字写入一个文件中，每行一个关键字 |
| `--action` | 可选，默认为 `move` | 对重复文件执行的操作，可选值为 `delete` 或 `move` |
| `--priority-order` | 可选 | 自定义优先级顺序，可选内容为 `modified_time path`。modified_time优先是考虑最新修改过的文件可能是最有保留价值的文件， path是文件完整路径，层数多的文件可能做了更细的整理。实际结合自己文件的情况，做对应的修改。 |
| `--move-to-dir` | 可选 | 移动文件的目标目录 |
| `--try-run, -n` | 可选 | 尝试运行模式：仅打印操作，不实际执行 |

```
$ python dup_finder.py mock -h

usage: dup_finder.py [-h] -d DIRECTORIES [DIRECTORIES ...] [--exclude EXCLUDE [EXCLUDE ...]] [--exclude-file EXCLUDE_FILE] [--action {delete,move}] [--priority-order PRIORITY_ORDER [PRIORITY_ORDER ...]] [--move-to-dir MOVE_TO_DIR] [--try-run]

Find and process duplicate files.

options:
  -h, --help            show this help message and exit
  -d DIRECTORIES [DIRECTORIES ...], --directories DIRECTORIES [DIRECTORIES ...]
                        Directories to search for duplicate files
  --exclude EXCLUDE [EXCLUDE ...]
                        Exclude keywords,
  --exclude-file EXCLUDE_FILE
                        File containing exclude keywords, one per line
  --action {delete,move}
                        Action to process files (default: move)
  --priority-order PRIORITY_ORDER [PRIORITY_ORDER ...]
                        Custom priority order: default is modified_time, path
  --move-to-dir MOVE_TO_DIR
                        Directory to move files to (if not specified, rename files with .dup_finder suffix)
  --try-run, -n         Try run mode: only print actions without executing them


```

### 示例
1. 查找并移动重复文件到指定目录：
   ```bash
   python dup_finder.py -d /path/to/dir1 /path/to/dir2 --action move --move-to-dir /path/to/move_dir
   ```

2. 查找并删除重复文件，保留包含特定关键字的文件：
   ```bash
   python dup_finder.py -d /path/to/dir1 --keyword important --action delete
   ```

3. 使用自定义优先级顺序查找并处理重复文件：
   ```bash
   python dup_finder.py -d /path/to/dir1 --priority-order modified_time path --action move
   ```

4. 尝试运行模式，仅打印操作，不实际执行：
   ```bash
   python dup_finder.py -d /path/to/dir1 --try-run
   ```

5. 使用简写形式尝试运行模式：
   ```bash
   python dup_finder.py -d /path/to/dir1 -n
   ```

6. 排除包含特定关键字的文件：
   ```bash
   python dup_finder.py -d /path/to/dir1 --exclude temp --exclude pdf
   ```

7. 使用排除文件排除特定关键字的文件：
   ```bash
   python dup_finder.py -d /path/to/dir1 --exclude-file exclude_keywords.txt
   ```

## 贡献
欢迎贡献代码！请阅读 [贡献指南](CONTRIBUTING.md) 以了解如何参与开发。

## 许可证
本项目采用 GPL-3.0 许可证，详情参见 [LICENSE](LICENSE) 文件。

---

希望这个 README 文件能帮助你更好地理解和使用 `dup_finder`。如果有任何问题或建议，请随时提 issue 或者联系开发者。