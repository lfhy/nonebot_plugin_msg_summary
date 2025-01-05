# nonebot_plugin_msg_summary

## 📖 介绍

基于Nonebot2，使用AI分析群聊记录，生成讨论内容的总结。

原项目采用Gemini进行推理,本项目修改为OpenAI格式API进行推理

原项目地址:```https://github.com/StillMisty/nonebot_plugin_summary_group```

## 💿 安装

使用nb-cli安装插件

```shell
nb plugin install nonebot_plugin_msg_summary
```

使用pip安装插件

```shell
pip install nonebot_plugin_msg_summary
```

## ⚙️ 配置

在机器人文件夹的`env`文件中添加下表中配置项。

|       配置项       | 必填  |       默认       |      说明      |
| :----------------: | :---: | :--------------: | :------------: |
|     summary_ai_key     |  是   |       None       | AI接口密钥 |
|   summary_ai_endpoint  |  否   | https://api.chatanywhere.tech | AI请求地址 |
|   summary_ai_api    |  否   | /v1/chat/completions | AI推理API |
|   summary_ai_model |  否   | gpt-4o-mini | AI模型名称 |
|       proxy        |  否   |       None       |    代理设置    |
| summary_max_length |  否   |       2000       |  总结最大长度  |
| summary_min_length |  否   |        50        |  总结最小长度  |
| summary_cool_down  |  否   |        0         |  总结冷却时间  |

### 如何配置AI请求地址

实际推理地址构成为`$summary_ai_endpoint$summary_ai_api`
默认为https://api.chatanywhere.tech/v1/chat/completions

请求采用openai兼容API格式

如果需要替换其他地址则替换summary_ai_endpoint和summary_ai_api即可

比如需要使用openai官方API进行总结 则在env文件中添加`summary_ai_endpoint=https://api.openai.com`即可

需要使用glm-4v-flash免费API进行总结,则需要在env文件添加
```
summary_ai_endpoint=https://open.bigmodel.cn
summary_ai_api=/api/paas/v4/chat/completions
summary_ai_model=glm-4v-flash
```

### 关于chatanywhere
默认使用chatanywhere提供的免费API进行总结,获取免费推理Key通过下面项目进行获取:
```https://github.com/chatanywhere/GPT_API_free```



## 🕹️ 使用

**总结 [消息数量]** ：生成该群最近消息数量的内容总结

**总结 [@群友] [消息数量]** ：生成指定群友相关内容总结

注：默认总结消息数量范围50~2000，使用无冷却时间
