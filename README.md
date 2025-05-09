# Pointcloud Viewer

## Compilation of the script

To compile the script into an only one executable file, you will need to install the PyInstaller library.
```console
python3 -m pip install pyinstaller
```

You can now start to compile the script. You may also need to use the `--exclude-module <package>` option to exclude others PyQt versions.
```console
pyinstaller --clean --onefile --windowed src/main.py
pyinstaller --clean --onefile --windowed --exclude-module PySide2 src/main.py
```

Add the line `import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)` at the top in the `main.spec` file. Then, run the next command.
```console
pyinstaller main.spec
```

The `main` executable file has been created in the `dist/` folder. You can execute it.
```
./dist/main
```