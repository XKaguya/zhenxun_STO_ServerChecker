# zhenxun_STO_ServerChecker

<div align="center">

[![Version](https://img.shields.io/github/v/release/XKaguya/zhenxun_STO_ServerChecker?sort=semver&style=flat-square&color=8DBBE9&label=Version)]()
[![GitHub Issues](https://img.shields.io/github/issues/XKaguya/zhenxun_STO_ServerChecker/total?style=flat-square&label=Issues&color=d77982)](https://github.com/XKaguya/zhenxun_STO_ServerChecker)
![Downloads](https://img.shields.io/github/downloads/XKaguya/zhenxun_STO_ServerChecker/total?style=flat-square&label=Downloads&color=d77982)

</div>

真寻的Star Trek Online服务器状态查询插件，又名STORecent。

名称灵感来源wws me recent。

# 安装
需要在和真寻同一台计算机上开启[STOTool]([https://github.com/XKaguya/StarTrekOnline-ServerStatus](https://github.com/XKaguya/STOTool))软件的Server功能。

若是自动开启的STOChecker，则无需手动开启Server功能。

自动重启STOTool不兼容旧版STOChecker。因为自动重启两步验证最终验证的是来自服务端的回信。

主动功能需要新版STOTool，否则您可能需要低版本的本插件。

~~*欲使用最新版STOTool与旧版插件，需要手动开启`LegacyPipeMode`*~~

# 功能
* 自动获取维护信息并发送到群中

* 获取最新9个新闻并显示在图片上

* 获取最新活动剩余时间/开始时间并显示在图片上

* 获取新闻长图

* 自动获取新闻发送到群中

# 用法
**若需使用自动重启STOChecker后端软件功能，请这样放置插件：**

`STORecent文件夹` 

![image](https://github.com/XKaguya/zhenxun_STO_ServerChecker/assets/96401952/d0eae86d-2194-42fe-bce8-5ca1f052801f)

`STOChecker文件夹`

![image](https://github.com/XKaguya/zhenxun_STO_ServerChecker/assets/96401952/3b7260bc-4e96-462b-b669-c97b21b5a8fe)

## 主动用法

在群中输入指令：
`/STORecent`，真寻就会获取所有上述功能的信息并发送到群中。

![image](https://github.com/XKaguya/zhenxun_STO_ServerChecker/assets/96401952/c0d552fd-fec6-4bb8-b552-828f01f93c01)

## 被动用法

真寻会自动获取维护信息并发送到配置文件定义的群中。

![image](https://github.com/XKaguya/zhenxun_STO_ServerChecker/assets/96401952/6299851e-2110-4265-acb6-2ff6abd1a143)

# 贡献
如有任何Bug，欢迎在Issue中提出。

