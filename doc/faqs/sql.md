# SQL 相关问题

## undefined symbol: sqlite3_deserialize

参考：[undefined symbol: sqlite3_deserialize](https://github.com/conda-forge/sqlite-feedstock/issues/113) & [undefined-symbol-sqlite3-deserialize-in-jupyter-notebook-visual-studio-code](https://stackoverflow.com/questions/78990030/undefined-symbol-sqlite3-deserialize-in-jupyter-notebook-visual-studio-code)

可以确认将所有 sqlite 包更新到 conda-forge 解决了这个问题：

```bash
conda install conda-forge::pysqlite3 conda-forge::sqlite conda-forge:libsqlite
```
