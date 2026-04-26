## 编译过程

不是直接在项目根目录下进行项目编译，而是先使用Ninja构建，然后进行build目录下的编译

你在源码目录（没有CMakeCache.txt）下直接运行了cmake --build .，而不是在CMake已配置的构建目录（如build）下运行。
正确做法是：
•	先用cmake -S . -B out\build -G Ninja生成构建目录
•	再用cmake --build out\build --config Release进行编译





## vcpkg



### 基本命令

```powershell
$env:VCPKG_ROOT = "C:\APP\vcpkg"
$env:PATH = "$env:VCPKG_ROOT;$env:PATH"
```



此 vcpkg 实例需要具有指定基线的清单才能与端口交互。请将 “builtin-baseline” 添加到清单或添加 “vcpkg-configuration.json”，以重新定义默认注册表。



```powershell
vcpkg x-update-baseline --add-initial-baseline
// 初始化生成自动创建 vcpkg.json 和 vcpkg-configuration.json，但是不会自动生成基线
vcpkg new --application
vcpkg add port fmt
vcpkg add port nlohmann-json
vcpkg add port eigen3

```

### 关键属性-基线

你观察得很仔细。vcpkg 的清单模式（Manifest Mode）**不会自动**为 `vcpkg.json` 生成 `"builtin-baseline"` 字段，这是**设计使然**，而不是一个 Bug。

#### 为什么不会自动生成基线？

vcpkg 的原则是：**不擅自修改用户的清单文件**。`vcpkg.json` 由你（或你的版本控制系统）管理，vcpkg 只负责读取并执行。如果它自动往文件里写入一个基线，可能会：

- 覆盖你已有的版本锁定策略
- 导致不必要的 Git 变更，干扰你的版本控制

所以，当你只写了 `"dependencies"` 时，vcpkg 会默认使用**当前 vcpkg 注册表中每个库的最新可用版本**。这虽然能工作，但存在两个风险：

1. **不可重复构建**：今天能编译通过，一周后 vcpkg 注册表更新了某个库的版本，你的项目可能突然失败。
2. **团队协作问题**：不同成员本地的 vcpkg 注册表版本不同，导致每个人拉取的依赖版本不一致。

#### 正确的做法：显式添加基线

基线（`builtin-baseline`）本质上是一个 **Git commit hash**，它指向 vcpkg 官方仓库中 `versions/baseline.json` 文件的某个版本，该文件记录了所有库在那一刻的精确版本快照。

##### 方法一：手动获取并添加（推荐）

1. 打开你本地 vcpkg 的安装目录（例如 `C:/APP/vcpkg`）。
2. 运行以下命令获取当前 vcpkg 的最新基线 commit hash：
   ```bash
   git rev-parse HEAD
   ```
   输出类似：`a1b2c3d4e5f6...`
3. 将这个 hash 写入你的 `vcpkg.json`：
   ```json
   {
     "builtin-baseline": "a1b2c3d4e5f6...",
     "dependencies": [
       "eigen3",
       "fmt",
       "nlohmann-json",
       "boost-geometry"
     ]
   }
   ```

##### 方法二：使用 vcpkg 命令自动添加（vcpkg 2024 及以后版本）

在项目目录下执行：
```bash
vcpkg x-update-baseline --add-initial-baseline
```
vcpkg 会自动将当前注册表的基线写入你的 `vcpkg.json`。

##### 方法三：不写基线，改用版本覆盖（不推荐）

你可以为每个依赖单独指定版本，例如：
```json
{
  "dependencies": [
    "eigen3",
    "fmt"
  ],
  "overrides": [
    { "name": "eigen3", "version": "3.4.0" },
    { "name": "fmt",    "version": "10.1.1" }
  ]
}
```
但这会失去全局版本快照的便利性，维护成本较高。

#### 总结

- **vcpkg 不会自动生成基线**，因为清单文件是用户的，vcpkg 不会擅自修改。
- **强烈建议你主动添加基线**，以保证构建的可重复性。
- 添加基线后，vcpkg 会严格按照该基线对应的版本安装依赖，不会再“每次拉取最新代码”。

添加基线后，你的 `vcpkg install` 或 CMake 配置行为就会变得稳定可预测，不会再因为外部注册表更新而意外变化。

## cmake

### VS 预设

在 Visual Studio 的 **CMake 目标选择器**（工具栏中间，通常显示“x64-Debug”或类似字样）下拉框中，可以看到当前激活的预设名称。你可以手动切换到 `vcpkg` 预设（如果你希望用它来配置），或者按我上一轮建议的修改方案，将工具链配置直接写入 `windows-base` 或 `x64-debug` 预设中。

如果你仍然不确定，也可以直接在 VS 的“输出”窗口 -> “CMake” 中查看开头的几行日志，会明确打印：

```
Using CMake preset: x64-debug
```

### 问题一：为什么 `"windows-base"` 没有出现在目标选择器中

因为它在预设定义中设置了 **`"hidden": true`**。

```json
{
  "name": "windows-base",
  "hidden": true,   // ← 这一行的作用
  ...
}
```

**`"hidden": true` 的含义**
告诉 Visual Studio（或其他 CMake 前端）**不要**在预设选择下拉列表中显示这个预设。它只作为一个**基础模板**供其他预设通过 `"inherits"` 继承使用，而不是一个可以直接选择的最终配置。

在你的配置中：
- `x64-debug` 继承了 `windows-base`，所以 `x64-debug` 会出现在列表中。
- `windows-base` 本身因为 `hidden: true` 而隐藏。

这就是为什么你只能在选择器中看到 `x64-debug`、`x64-release`、`x86-debug` 等，而看不到 `windows-base`。

### 问题二：`CMakePresets.json` 文件的作用

`CMakePresets.json` 是 CMake 官方提供的一个**配置文件**，用于集中管理项目的 CMake 配置选项，主要作用包括：

1. 统一团队开发环境

团队成员共享同一个 `CMakePresets.json`，可以确保大家使用相同的生成器（如 Ninja）、编译选项、构建目录结构等，避免“在我电脑上能编译”的问题。

#### 2. 简化命令行操作

不用每次都输入一长串 `-D` 参数，只需指定预设名称：
```bash
cmake --preset x64-debug
cmake --build --preset x64-debug
```

#### 3. 集成 IDE 支持
Visual Studio、VS Code、CLion 等都能自动识别 `CMakePresets.json`，将预设显示为可选配置，方便在 IDE 内切换不同构建类型（Debug/Release）、架构（x64/x86）甚至跨平台（Linux/macOS）。

#### 4. 管理多配置

可以一次定义多种构建场景：
- `x64-debug`
- `x64-release`
- `x86-debug`
- `linux-debug`
- `macos-debug`

每个场景可以有独立的：
- 生成器（Ninja / Visual Studio）
- 构建/安装目录
- CMake 变量（`CMAKE_BUILD_TYPE`、`CMAKE_TOOLCHAIN_FILE` 等）
- 工具链文件（用于交叉编译或 vcpkg 集成）

#### 5. 支持条件配置

通过 `"condition"` 字段，可以根据当前主机系统（Windows/Linux/Darwin）自动启用或禁用某些预设，实现跨平台项目的统一管理。

#### 总结
`CMakePresets.json` 就是 CMake 项目的“控制面板”，让你和你的团队用一种标准化的方式管理所有构建配置，不再依赖个人 IDE 的私有设置或手写的脚本。



#### 配置好cmake pre配置之后



```
// 配置项目
cmake --preset x64-debug

// 构建项目
cmake --build out/build/x64-debug

PS C:\APP\CODE\3d_city\app\3d> cmake --build --preset=x64-debug
[2/2] Linking CXX executable 3d.exe
PS C:\APP\CODE\3d_city\app\3d>
```

### cmake结合vcpkg

在 VS2026 中使用 vcpkg 的正确方式是采用**清单模式（Manifest Mode）**。这种方式能让你的项目自动管理依赖，团队成员克隆代码后即可一键构建，无需手动安装库。

#### 第一步：安装 vcpkg 并集成到 VS

如果你还没有一个独立的 vcpkg，强烈建议不要使用 VS 自带的版本（功能受限且难以更新）。请打开 **PowerShell**，按以下步骤操作：

1.  **克隆并安装**：在你想安装的目录下（如 `C:\dev\`）运行：
    ```powershell
    git clone https://github.com/microsoft/vcpkg.git
    cd vcpkg
    .\bootstrap-vcpkg.bat
    ```
2.  **集成到 VS**：执行以下命令，这会将 vcpkg 注册到 Visual Studio 全局，之后所有项目都能受益：
    ```powershell
    .\vcpkg integrate install
    ```
3.  **设置环境变量（推荐）**：方便在命令行中使用，添加一个用户环境变量：
    ```powershell
    [System.Environment]::SetEnvironmentVariable('VCPKG_ROOT','C:\dev\vcpkg', 'User')
    ```

#### 第二步：为你的项目配置依赖

接下来，在你项目的根目录下（`CMakeLists.txt` 所在位置），用 vcpkg 初始化清单文件。

1.  **初始化清单**：打开终端，cd 到你的项目目录，运行：
    ```powershell
    vcpkg new --application
    ```
    这会自动创建 `vcpkg.json` 和 `vcpkg-configuration.json` 两个文件。

2.  **添加库依赖**：使用 `add port` 命令添加你需要的库，例如：
    ```powershell
    vcpkg add port fmt
    vcpkg add port nlohmann-json
    vcpkg add port eigen3
    ```
    执行后，`vcpkg.json` 文件里就会列出这些依赖。

#### 第三步：确认 CMake 配置

现在最关键的一步是确保 CMake 能找到这些通过 vcpkg 安装的库。

*   **如果你使用 `CMakePresets.json`**：
    检查你的 `windows-base` 预设，确保 `toolchainFile` 指向了 vcpkg 的工具链：
    ```json
    "toolchainFile": "C:/dev/vcpkg/scripts/buildsystems/vcpkg.cmake"
    ```

*   **如果你不使用预设**：
    在 VS 的 CMake 设置中，添加一个名为 `CMAKE_TOOLCHAIN_FILE` 的变量，值为 `C:/dev/vcpkg/scripts/buildsystems/vcpkg.cmake`。

完成以上设置后，你的 `CMakeLists.txt` 中只需要简单的 `find_package` 命令，无需再手动指定任何路径。

#### 第四步：开始构建

关闭并重新打开 Visual Studio，打开你的项目文件夹。VS 会自动识别 `vcpkg.json` 文件。当你首次点击**生成**时，你会看到 VS 开始自动下载和编译 `fmt`、`nlohmann-json` 等依赖库。这个过程需要联网，第一次可能会花费一些时间，但完成后就一劳永逸了。

#### 关键点与常见问题

*   **路径不能有空格**：确保 `vcpkg` 的安装路径和你的项目路径中**不包含空格或中文字符**，否则会引发奇怪的编译错误。
*   **架构必须匹配**：你的 VS 解决方案平台（x64/x86）必须与你安装库的架构一致。默认情况下，vcpkg 安装的是 x64 版本。
*   **工具链文件是必须的**：这是新手最容易忽略的一步。没有它，`find_package` 就会像你之前那样报错找不到 `fmtConfig.cmake`。

按照这个标准流程走下来，你就不会再遇到之前那种手动配置路径的问题了。





#### 注意点

在 `CMakePresets.json` 中设置 `toolchainFile` 时，请使用以下路径（注意使用正斜杠）：

```json
"toolchainFile": "C:/APP/vcpkg/scripts/buildsystems/vcpkg.cmake"
```

或者在 `CMakeLists.txt` 中（放在 `project()` 之前）：

```cmake
set(CMAKE_TOOLCHAIN_FILE "C:/APP/vcpkg/scripts/buildsystems/vcpkg.cmake" CACHE STRING "")
```

如果需要在命令行指定：

```bash
cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE="C:/APP/vcpkg/scripts/buildsystems/vcpkg.cmake"
```

确保路径指向 `scripts/buildsystems/vcpkg.cmake`，而不是 vcpkg 根目录。



## 设置控制台语言

### 方法一：在 PowerShell 中临时设置编码（当前会话有效）

打开 PowerShell，执行以下命令将输出编码改为 UTF-8：

powershell

```
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```



如果需要输入 UTF-8（例如从管道读取），也可设置输入编码：

powershell

```
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
```



**注意**：此设置只影响当前 PowerShell 窗口，关闭后失效。



### 方法三：使用 Windows 的 UTF-8 全局支持（Beta 功能）

此方法会影响整个系统（包括命令提示符、传统控制台应用），**可能引起某些旧程序乱码**，请谨慎操作。

1. 打开 **设置** → **时间和语言** → **语言和区域**。
2. 点击 **管理语言设置** → **更改系统区域设置**。
3. 勾选 **Beta 版：使用 Unicode UTF-8 提供全球语言支持**。
4. 重启计算机。

启用后，控制台将默认使用 UTF-8 编码，PowerShell 和 cmd 都能直接显示 UTF-8 字符。



## 配置内容顺序

```cmake
# CMakeList.txt: 3d 的 CMake 项目，在此处包括源代码并定义
# 项目特定的逻辑。
#
cmake_minimum_required (VERSION 3.10)

# 如果支持，请为 MSVC 编译器启用热重载。
if (POLICY CMP0141)
  cmake_policy(SET CMP0141 NEW)
  set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "$<IF:$<AND:$<C_COMPILER_ID:MSVC>,$<CXX_COMPILER_ID:MSVC>>,$<$<CONFIG:Debug,RelWithDebInfo>:EditAndContinue>,$<$<CONFIG:Debug,RelWithDebInfo>:ProgramDatabase>>")
endif()
set(CMAKE_TOOLCHAIN_FILE "C:/APP/vcpkg/scripts/buildsystems/vcpkg.cmake" CACHE STRING "")
project ("3d")

file(GLOB_RECURSE SRC_FILES
    3d.cpp
    src/*.cpp
    src/*.c
)

add_executable(3d ${SRC_FILES})
# 顺序不可以更改，必须先add然后指定编译格式
target_compile_options(3d PRIVATE /utf-8)
target_include_directories(3d PRIVATE include)

find_package(fmt CONFIG REQUIRED)
find_package(Eigen3 CONFIG REQUIRED)
find_package(Boost REQUIRED)          # boost-geometry 是 header-only
#find_package(nlohmann_json CONFIG REQUIRED)
find_package(nlohmann_json REQUIRED)
target_link_libraries(3d PRIVATE nlohmann_json::nlohmann_json)

# 将源代码添加到此项目的可执行文件。

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET 3d PROPERTY CXX_STANDARD 20)
endif()

# TODO: 如有需要，请添加测试并安装目标。


```

## cmake寻找模块方式变更

好的，我们来系统性地总结一下 **CMake 查找依赖库的“旧模式”（Find 模块）与“新模式”（Config 文件）的对比**，并给出具体的语法示例，结合你之前遇到的 Boost 和 nlohmann/json 的情况。



### 核心对比总览

| 对比维度       | **旧模式：Find 模块**                                        | **新模式：Config 文件**                                      |
| -------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **提供者**     | CMake 官方或第三方维护的 `Find<Package>.cmake` 脚本          | 库的作者在安装时生成的 `<Package>Config.cmake` 或 `<lowercase>-config.cmake` |
| **触发方式**   | `find_package(<Package> MODULE)` 或默认（没有 CONFIG 关键字） | `find_package(<Package> CONFIG)` 或设置 `CMAKE_FIND_PACKAGE_PREFER_CONFIG=TRUE` |
| **工作原理**   | 猜测头文件、库文件路径（依赖变量如 `BOOST_ROOT`）            | 直接读取库自带的配置文件，包含精确的路径、目标、依赖关系     |
| **可靠性**     | 低 – 需要 CMake 持续更新以支持新版本库                       | 高 – 由库作者维护，与库版本严格匹配                          |
| **暴露的接口** | 变量（如 `Boost_INCLUDE_DIRS`、`Boost_LIBRARIES`）           | 导入目标（如 `Boost::boost`、`nlohmann_json::nlohmann_json`） |
| **链接方式**   | `target_include_directories(... ${Boost_INCLUDE_DIRS})`<br>`target_link_libraries(... ${Boost_LIBRARIES})` | `target_link_libraries(... Boost::boost)`（自动处理包含路径和依赖） |
| **依赖传递**   | 需手动处理（例如 Boost::filesystem 依赖 Boost::system）      | 自动传递，无需手动添加                                       |
| **错误信息**   | 可能含糊：“找不到 Boost”                                     | 更明确：“找不到 BoostConfig.cmake，请确保 Boost 已正确安装”  |
| **CMake 政策** | CMake 3.30 起 `CMP0167` 默认为 NEW，不推荐 FindBoost         | 推荐方式，未来 CMake 版本将完全依赖此模式                    |
| **适用场景**   | 老旧库、未使用 CMake 构建的库（如某些 C 库）                 | 现代库（几乎全部用 CMake 构建的主流库）                      |



### 语法示例对比

#### 1. Boost 库

##### ❌ 旧模式（FindBoost，CMake < 3.30 默认）

```cmake
find_package(Boost 1.70 REQUIRED COMPONENTS filesystem system)
if(Boost_FOUND)
    include_directories(${Boost_INCLUDE_DIRS})
    target_link_libraries(my_app ${Boost_LIBRARIES})
endif()
```

##### ✅ 新模式（BoostConfig，CMake ≥ 3.30 推荐）
```cmake
find_package(Boost 1.70 REQUIRED COMPONENTS filesystem system)
target_link_libraries(my_app PRIVATE Boost::filesystem Boost::system)
# 无需手动添加 include 路径，导入目标会自动处理
```

**注意**：新模式中 `find_package` 写法不变，但实际查找的是 `BoostConfig.cmake`（由 Boost 官方提供）。链接时直接使用 `Boost::组件` 目标。



#### 2. nlohmann/json 库

##### ❌ 旧模式（Findnlohmann_json，如果存在）
```cmake
find_package(nlohmann_json MODULE)
if(nlohmann_json_FOUND)
    include_directories(${nlohmann_json_INCLUDE_DIR})
    target_link_libraries(my_app ${nlohmann_json_LIBRARIES})
endif()
```
但实际上 CMake 官方**没有**提供 `Findnlohmann_json.cmake`，所以这种做法通常失败。

##### ✅ 新模式（Config 文件）
```cmake
find_package(nlohmann_json CONFIG REQUIRED)
target_link_libraries(my_app PRIVATE nlohmann_json::nlohmann_json)
```
`nlohmann_json::nlohmann_json` 是一个仅头文件的导入目标，链接它就会自动添加头文件路径。



#### 3. 通用模式：让 CMake 自动选择

为了兼容性，可以**不指定 MODULE 或 CONFIG**，让 CMake 先尝试 Config 模式，失败再回退到 Module 模式：
```cmake
find_package(Boost 1.70 REQUIRED)   # 默认顺序：Config -> Module
```
但 CMake 3.30+ 对 Boost 已经默认禁用 Module 模式，所以最好显式设置策略。

**强制优先使用 Config 模式**（全局推荐）：
```cmake
set(CMAKE_FIND_PACKAGE_PREFER_CONFIG TRUE)
find_package(Boost 1.70 REQUIRED COMPONENTS filesystem)
```



### 遇到的具体问题总结

#### 问题 1：Boost 警告 `CMP0167`
- **原因**：你的 CMake ≥ 3.30，默认 `CMP0167` 为 `NEW`（使用 Config 模式），但你的 `CMakeLists.txt` 没有明确设置策略。
- **解决**：在 `CMakeLists.txt` 顶部添加：
  ```cmake
  cmake_minimum_required(VERSION 3.30)
  ```
  或显式设置：
  ```cmake
  if(POLICY CMP0167)
      cmake_policy(SET CMP0167 NEW)
  endif()
  ```

#### 问题 2：nlohmann/json 找不到
- **原因**：你的 `CMakeLists.txt` 使用了 `find_package(nlohmann_json CONFIG REQUIRED)`，但 vcpkg 安装的 nlohmann-json 提供了配置文件，路径没有被 CMake 找到（需要 vcpkg 工具链）。
- **解决**：确保构建时使用了 vcpkg 的工具链文件：
  ```bash
  cmake -DCMAKE_TOOLCHAIN_FILE=C:/APP/vcpkg/scripts/buildsystems/vcpkg.cmake ..
  ```



### 如何迁移旧项目到新模式

1. **检查 CMake 最低版本**：设为 3.15+（支持大多数 Config 模式），推荐 3.30+。
2. **替换变量为导入目标**：
   - 删除 `include_directories(${PACKAGE_INCLUDE_DIRS})`
   - 删除 `link_directories(${PACKAGE_LIBRARY_DIRS})`
   - 直接 `target_link_libraries(main PRIVATE Package::Package)`
3. **设置策略**：`cmake_policy(SET CMP0167 NEW)`（针对 Boost）。
4. **全局偏好 Config**：`set(CMAKE_FIND_PACKAGE_PREFER_CONFIG TRUE)`



### 常用库的导入目标名称参考

| 库名          | Config 包名     | 导入目标示例                        |
| ------------- | --------------- | ----------------------------------- |
| Boost         | `Boost`         | `Boost::boost`, `Boost::filesystem` |
| nlohmann/json | `nlohmann_json` | `nlohmann_json::nlohmann_json`      |
| OpenCV        | `OpenCV`        | `opencv::core`, `opencv::highgui`   |
| Qt6           | `Qt6`           | `Qt6::Core`, `Qt6::Widgets`         |
| fmt           | `fmt`           | `fmt::fmt`                          |
| spdlog        | `spdlog`        | `spdlog::spdlog`                    |
| CUDA          | `CUDA`          | `CUDA::cudart`                      |



### 快速检查某个库是否支持 Config 模式

在命令行执行：
```bash
cmake --find-package -DNAME=Boost -DCOMPILER_ID=MSVC -DLANGUAGE=CXX -DMODE=EXIST
```
如果返回成功且路径指向 `BoostConfig.cmake`，则支持。

或者直接看库安装目录下是否有 `*Config.cmake` 文件。



