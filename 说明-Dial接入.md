# BituoPMD 改动说明（给测试用）

仓库：[https://github.com/bo706/BituoPMD](https://github.com/bo706/BituoPMD)  
这是官方插件 [script0803/BituoPMD](https://github.com/script0803/BituoPMD) 的 fork，**不是** Dial 圆屏固件。  
当前版本：`1.1.1`。

---

## 要解决什么问题

办公室 Home Assistant 里原来的 BituoPMD，只能接 **EW 电表**（电表自己带 Wi-Fi，插件按 IP 去读网页）。

这次要接的是 **Bituo Dial（圆屏网关）**：

- 三块表（SPM02、SPM01、SDM01）走 **蓝牙**，挂在 Dial 后面
- 表本身没有 Wi-Fi，插件不能像 EW 那样直接搜到表
- Dial 开了局域网网页后，访问 Dial 的 IP，一次能拿到后面所有表的数据

官方插件读不懂 Dial 返回的数据格式，所以加不上。  
本 fork **只改了 Home Assistant 插件**，**没有改 Dial 固件，也没有给三块 BLE 表重新配网**。

---

## 和官方插件差在哪

| | 官方 BituoPMD | 本 fork |
|---|---|---|
| 能接什么 | 只有 EW 电表 | EW 电表 + Dial 网关 |
| 怎么加 Dial | 加不上 | 手动填 Dial 的 IP |
| 数据怎么来 | 每 5 秒访问电表网页 | Dial：每 10 秒访问 Dial 的 `/data` |
| 功率单位 | EW 是 kW，插件会 ×1000 变成 W | Dial 本身已经是 W，**不再 ×1000** |
| 不该对 Dial 用的功能 | 定位灯、恢复出厂、网页 OTA、开关口 | 已跳过（Dial 没有这些 EW 接口） |

EW 电表原有用法尽量保持不变。

---

## 办公室里现在的状态

办公室 HA：`http://192.168.50.211:8123/`  
已经用本 fork 加过 Dial（实验 IP：`192.168.50.151`）。

设备页应能看到：

- **Bituo Dial - 192.168.50.151**（网关，显示在线表数）
- **SPM02 / SPM01 / SDM01-4560**（三块表，电压、功率、电能等）

数值大约每 10 秒更新一次。  
办公室里原来的 EW / Zigbee 电表没有动。

HACS 里可能同时出现两个「BituoPMD」：一个是官方仓库，一个是本 fork。真正在跑、能认 Dial 的是 **bo706/BituoPMD** 这一份。官方那条可以从 HACS 列表里 Remove，不要卸掉 fork。

---

## 领导怎么测

电脑连办公室同一局域网，打开上面的 HA 即可，不必再装一遍。

若要在别的 HA 上自己装：

1. HACS → 自定义仓库 → 填 `https://github.com/bo706/BituoPMD` → 类型选 Integration → 安装后**重启 HA**
2. 圆屏长按 Setup，打开 **局域网网页**（默认是关的）
3. 设置 → 设备与服务 → 添加 **BituoPMD** → **Use IP to pair devices**
4. 填 Dial 的 STA IP（以圆屏系统页为准）
5. 看三块表的电压、功率是否在变

不要对 Dial 这条目使用：定位、恢复出厂、OTA。  
不要把三块 BLE 表改配到 Wi-Fi 上，否则会离开 Dial。

---

## 改了哪些文件（便于对照代码）

都在 `custom_components/bituopmd/`：

- `device_api.py`：判断对方是 EW 还是 Dial；Dial 按信封拆成多块表
- `config_flow.py`：手动填 IP 时走上面的识别
- `sensor.py`：Dial 每块表一个设备；网关有「在线表数」；10 秒轮询
- `__init__.py` / `switch.py`：Dial 不加载开关平台，避免去打不存在的 `/hadata`
- `button.py`：Dial 不提供定位按钮
- `translations/`：中英文提示里写明可以填 Dial IP
- `manifest.json`：版本 `1.1.1`

---

## 建议怎么决策

- 本仓库用于 **先测、再决定要不要合进官方工程**
- 若认可：从本 fork 向官方 `script0803/BituoPMD` 提 PR
- 若只在公司内部用：HACS 一直指向本仓库即可
