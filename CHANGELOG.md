## [0.2.3](https://github.com/Nagico/paperpilot-common/compare/v0.2.2...v0.2.3) (2023-11-08)


### Features

* 添加bump version工具 ([fcfeb86](https://github.com/Nagico/paperpilot-common/commit/fcfeb86ac7f921e4d9e7178009e559bf0d80f30b))
* 添加ci版本发布 ([9d7cf97](https://github.com/Nagico/paperpilot-common/commit/9d7cf971f14b9ae244fb7e3b2fadb46ff005be5d))
* 添加paper event字段 ([5b5322f](https://github.com/Nagico/paperpilot-common/commit/5b5322f85e46de34175829afbe7c890cf3adcd2b))
* bump version to v0.2.3 ([f875959](https://github.com/Nagico/paperpilot-common/commit/f875959564e140535be7217e0a494e4174f0dffb))


### BREAKING CHANGES

* PaperDetail添加string event



## [0.2.2](https://github.com/Nagico/paperpilot-common/compare/v0.2.1...v0.2.2) (2023-11-07)


### Bug Fixes

* 关闭django orm连接 ([43374bd](https://github.com/Nagico/paperpilot-common/commit/43374bda3ab66395ea9b7cb138779e7b61269e26))
* 修复mysql连接 ([9234507](https://github.com/Nagico/paperpilot-common/commit/92345079bb8e16666b7c570cd5693ad5bbfac14c))


### Features

* 添加ai接口 ([72966e4](https://github.com/Nagico/paperpilot-common/commit/72966e4f7989d0b03fa3596b7b4f1ac099792a28))
* ListPaper返回Detail ([efd2c19](https://github.com/Nagico/paperpilot-common/commit/efd2c19567ed89f256cc979f21ad012ca2bf6a41))
* **python:** 添加oss file acl操作 ([f2190aa](https://github.com/Nagico/paperpilot-common/commit/f2190aa58229d05463ddee120c6d92ec0bf64c0b))



## [0.2.1](https://github.com/Nagico/paperpilot-common/compare/v0.2.0...v0.2.1) (2023-10-27)


### Bug Fixes

* 修复django mysql连接 ([080fc80](https://github.com/Nagico/paperpilot-common/commit/080fc80074d35df0527fd583c9a56feded23e68f))


### Features

* **python:** 异常处理移除django依赖 ([70d19c8](https://github.com/Nagico/paperpilot-common/commit/70d19c8bc98a1d0be7106562bc4ccba7bbdd088f))



# [0.2.0](https://github.com/Nagico/paperpilot-common/compare/v0.0.11...v0.2.0) (2023-10-26)


### Bug Fixes

* 修复拦截器返回值 ([ce04dee](https://github.com/Nagico/paperpilot-common/commit/ce04dee70d115a231dd533e0f7b4684ca63195b7))
* 移除django依赖 ([8e6f1e3](https://github.com/Nagico/paperpilot-common/commit/8e6f1e3169ac8d53871348f3fcbd990c50ee3938))
* **python:** 添加反射服务返回 ([e06b359](https://github.com/Nagico/paperpilot-common/commit/e06b3597d48ff8848b6c63610e3bda53248db732))
* **python:** 修复拦截器 ([c19096f](https://github.com/Nagico/paperpilot-common/commit/c19096f2505a070c769f244711f7b503b23cfee3))
* **python:** 修复拦截器await ([5fd9a44](https://github.com/Nagico/paperpilot-common/commit/5fd9a44f9cd7e838a99bb2c224c565dbb0cf8037))
* **python:** 修复stream拦截器调用异常 ([198084c](https://github.com/Nagico/paperpilot-common/commit/198084c2df98523fb9f4ab035550d0ea4835e809))


### Features

* 精简health check log ([451c0d1](https://github.com/Nagico/paperpilot-common/commit/451c0d1c9c334028dfcd3cd38660eb7e51690441))
* 添加监控服务接口 ([f70251a](https://github.com/Nagico/paperpilot-common/commit/f70251a88ec1fa92730aa4ed92a6377b77e9a604))
* 添加监控接口注释 ([e07c97a](https://github.com/Nagico/paperpilot-common/commit/e07c97a579c62bef9deef8f7c82d786ed357a0e7))
* 添加im接口 ([482c4f2](https://github.com/Nagico/paperpilot-common/commit/482c4f240bd6ff281dc180792c2c346f0dad521e))
* 增加ProjectStatus id字段 ([73c125a](https://github.com/Nagico/paperpilot-common/commit/73c125a3f8d028beafe66b41e63da3159421483f))
* 增加server host count ([c404e66](https://github.com/Nagico/paperpilot-common/commit/c404e663b3e9d55ddb17ba65ecfd34c4015cdf1a))
* **python:** 添加默认health check ([4c2c405](https://github.com/Nagico/paperpilot-common/commit/4c2c405d6c974f5ea09dc6daf334e039440821fe))
* **python:** 展示内部异常 ([ea41905](https://github.com/Nagico/paperpilot-common/commit/ea41905b8fa42a7f8a153db63920674c68e746d2))
* **python:** 支持拦截器处理空请求 ([9d8e6be](https://github.com/Nagico/paperpilot-common/commit/9d8e6be9da7c092e6587a7e362ec38ea8491e65d))



## [0.0.11](https://github.com/Nagico/paperpilot-common/compare/v0.0.9...v0.0.11) (2023-10-23)


### Bug Fixes

* 更改oss直传参数 ([70185b8](https://github.com/Nagico/paperpilot-common/commit/70185b8cd28b635edf8d3655b8eab29502215168))
* 修改PaperService.AddPaper参数 ([a47553e](https://github.com/Nagico/paperpilot-common/commit/a47553e80f29248aa6716f1c6f2b8528fa7f0602))
* 只保留paper detail的出版年份 ([5ffdca5](https://github.com/Nagico/paperpilot-common/commit/5ffdca5f71e33e40ab14116a1ed9d9003a1beddc))
* **python:** 更新oss直传参数 ([19377f3](https://github.com/Nagico/paperpilot-common/commit/19377f3dde328b08420ffe5b318031f0b5458063))
* **python:** 修复上传key ([b6c8830](https://github.com/Nagico/paperpilot-common/commit/b6c8830a91bd1649821eeccbc4fbad1c96273532))
* **python:** 修复验证器获取 ([e272c49](https://github.com/Nagico/paperpilot-common/commit/e272c49dc768070c00b3bfd54c97df9ffc665fe6))
* **python:** 修复异常类型 ([4a58632](https://github.com/Nagico/paperpilot-common/commit/4a586325cec4840b9e48fa7a0659021797ab6c16))
* **python:** 修复header获取 ([7854856](https://github.com/Nagico/paperpilot-common/commit/7854856c19c7b4921d7c3b6ecee1c79e7e09ac18))
* **python:** 修复header获取 ([d55eb07](https://github.com/Nagico/paperpilot-common/commit/d55eb071d6894cffe98fdd512655684aa90d5a7a))
* **python:** 修复rest framework异常 ([bd77392](https://github.com/Nagico/paperpilot-common/commit/bd773921a47048651cc9a919f04e3481536db8bb))


### Features

* 添加翻译接口 ([5852d6c](https://github.com/Nagico/paperpilot-common/commit/5852d6c1646f8452ef11d672abd4405ddcb092b0))
* 添加更新论文附件接口 ([ffaaed4](https://github.com/Nagico/paperpilot-common/commit/ffaaed47f7f899ba8e0338920e09ba388ddb4ad0))
* **python:** 独立callback操作 ([25924c6](https://github.com/Nagico/paperpilot-common/commit/25924c6fe4743b8b251daba936f71bb97318fd08))
* **python:** 独立context操作 ([2185e3f](https://github.com/Nagico/paperpilot-common/commit/2185e3fa4cf96a20ec57158643bd3a3316b60e52))
* **python:** 更新依赖版本 ([599c158](https://github.com/Nagico/paperpilot-common/commit/599c15893ce0cd8ba3a7e1a55aadeafe9ea0c30b))
* **python:** 开启签名认证 ([611cc24](https://github.com/Nagico/paperpilot-common/commit/611cc24366c4c45003b4cf6c848d14326e9a05bd))
* **python:** 默认开启重连 ([bf72975](https://github.com/Nagico/paperpilot-common/commit/bf72975b79a0acb4f2b0e1c7b9349d31fd6bb39f))
* **python:** 添加db重连接 ([f1e93be](https://github.com/Nagico/paperpilot-common/commit/f1e93be7c46e00f82fa1eab64f237b51a431385a))


### BREAKING CHANGES

* PaperService.AddPaper参数更改为PaperDetail



## [0.0.9](https://github.com/Nagico/paperpilot-common/compare/b5a85411227dd807b44bf9b93015b272525051aa...v0.0.9) (2023-10-10)


### Bug Fixes

* 修改Register返回类型 ([48fc58c](https://github.com/Nagico/paperpilot-common/commit/48fc58cf0844b32d101c39cbf9568ca06d159aaf))
* **python:** 取消镜像源 ([2d9a34d](https://github.com/Nagico/paperpilot-common/commit/2d9a34dd79c674bf3c433d204fc69b4dc3cf032c))
* **python:** 添加python版本 ([500e0db](https://github.com/Nagico/paperpilot-common/commit/500e0db71a1dbd059d957dfe8b03cadc275e427b))
* **python:** 修复包名 ([2488082](https://github.com/Nagico/paperpilot-common/commit/2488082a55c622e65213867b5da8c22d03a0979c))
* **python:** 修复包名 ([a5aebbd](https://github.com/Nagico/paperpilot-common/commit/a5aebbdc675a271fdc9bb86ee0c30daf7d242326))
* **python:** 修复匿名认证抛出异常 ([b1ea025](https://github.com/Nagico/paperpilot-common/commit/b1ea02566ed3cd209ac0678db7c26c0374a5c2c3))
* **python:** 修复匿名下的auth中间件 ([ab2f05f](https://github.com/Nagico/paperpilot-common/commit/ab2f05f6cec923936abe06d99cd084b4eb59594b))
* **python:** 修复直传key兼容media_url ([48662dc](https://github.com/Nagico/paperpilot-common/commit/48662dc3fb00ea39f95a3595926e57b1855fab0c))
* **python:** 修复中间件await ([9eef566](https://github.com/Nagico/paperpilot-common/commit/9eef56614a4834b0d275d2ecd4496dacbc9a3fc6))
* **python:** 修复字段转换类导入 ([3a13db8](https://github.com/Nagico/paperpilot-common/commit/3a13db88b882ef0ac36d276fca8f24ecefd2d62c))
* **python:** 修复python包生成位置 ([a283ef7](https://github.com/Nagico/paperpilot-common/commit/a283ef70d35a96d62134ab8c3052907c9215ef4b))
* **python:** 修复readme ([80b3a57](https://github.com/Nagico/paperpilot-common/commit/80b3a57f9e80a28c70a587bb302493f77e8babd4))
* **python:** 修改grpc util log类 ([e5030ef](https://github.com/Nagico/paperpilot-common/commit/e5030ef514d944556b08e44ad1cfff00eaf6cb7a))
* **python:** 移除drf依赖 ([6ead043](https://github.com/Nagico/paperpilot-common/commit/6ead043e533ea1eb79831ed48ea936001c1bc9d4))


### Features

* 更新文档说明 ([e765a89](https://github.com/Nagico/paperpilot-common/commit/e765a897f06945b70fda23ed7a7a9ac73ab7c34f))
* 添加 exec 接口定义 ([92638f0](https://github.com/Nagico/paperpilot-common/commit/92638f0fd39a784f8ac83245cdafbed87249d24d))
* 添加测试接口 ([3c32166](https://github.com/Nagico/paperpilot-common/commit/3c3216634174258ae62834ba2a24eeaf9e56a95d))
* 添加发送验证码接口 ([1e37b99](https://github.com/Nagico/paperpilot-common/commit/1e37b995c2a7f3c062250674af4e0d912dd04b33))
* 添加基础项目结构 ([b5a8541](https://github.com/Nagico/paperpilot-common/commit/b5a85411227dd807b44bf9b93015b272525051aa))
* 添加统一version ([aecf996](https://github.com/Nagico/paperpilot-common/commit/aecf996f18dce6726bb7b027351ca6e5ee658e12))
* 添加无trace_id提示 ([529a45a](https://github.com/Nagico/paperpilot-common/commit/529a45ab90743a1d0bc187b6796f3002554f36e3))
* 添加项目、论文接口 ([509bd8f](https://github.com/Nagico/paperpilot-common/commit/509bd8ffef67c79e5dbf216354a01818d90c8a8b))
* 添加用户基本接口 ([0568d96](https://github.com/Nagico/paperpilot-common/commit/0568d9663e3a03032ff5ac9edfa584c479c99314))
* 添加直传token获取 ([b9546f1](https://github.com/Nagico/paperpilot-common/commit/b9546f13134a0b7ca3831defb26e0067d9c5dd0d))
* 添加注册获取数量接口 ([4c6f755](https://github.com/Nagico/paperpilot-common/commit/4c6f7559aeac65aab85c90bf66b055317085941e))
* 添加python库生成脚本 ([d48e7b4](https://github.com/Nagico/paperpilot-common/commit/d48e7b47ffd884beed5347f6361ad5c7ca6a91b9))
* 添加trace ([5167116](https://github.com/Nagico/paperpilot-common/commit/516711631dd5e9385603e24269536ff4d2695046))
* **python:** 更新python接口 ([28cc416](https://github.com/Nagico/paperpilot-common/commit/28cc4165bcd1a8b5b7f935f8b8228fda982525d8))
* **python:** 更新python接口 ([c5e484a](https://github.com/Nagico/paperpilot-common/commit/c5e484add075242c6652253ca8784e26766f7680))
* **python:** 兼容无用户admin ([f5d52ca](https://github.com/Nagico/paperpilot-common/commit/f5d52ca37f67ac33c28a159520db240f03f4a252))
* **python:** 添加公共工具 ([d472467](https://github.com/Nagico/paperpilot-common/commit/d4724676de0e34242373576dfb4edbb8c3c835e1))
* **python:** 添加认证Mixin ([686d56d](https://github.com/Nagico/paperpilot-common/commit/686d56d38f0db7c83f6a3a765094573916d9544f))
* **python:** 添加异步原子操作 ([f8bd0e1](https://github.com/Nagico/paperpilot-common/commit/f8bd0e1b88753211ab7f51a7666e9b6202c11692))
* **python:** 添加自定义middleware ([cc89be5](https://github.com/Nagico/paperpilot-common/commit/cc89be503d5f71394fe61824f786235ef62fa3b2))
* **python:** 添加admin log ([ca83037](https://github.com/Nagico/paperpilot-common/commit/ca83037c587ebc271b81799ab2ea96da5ef626e0))
* **python:** 添加context类型 ([162ee80](https://github.com/Nagico/paperpilot-common/commit/162ee8021a8016fa9d80f8b9a01f084aa90f71b7))
* **python:** 添加django工具 ([8b86423](https://github.com/Nagico/paperpilot-common/commit/8b86423ac2846a2a744e51a87e99e5150d180413))
* **python:** 添加fake context ([af0cb69](https://github.com/Nagico/paperpilot-common/commit/af0cb698a6ac103c7252d4bd6f1d727fdb364444))
* **python:** 添加grpc client ([db209f8](https://github.com/Nagico/paperpilot-common/commit/db209f839c9cd881c9b4321e5cf293c5b6874f43))
* **python:** 添加grpc client缓存 ([752bbbb](https://github.com/Nagico/paperpilot-common/commit/752bbbb1ca0c6113c4aae64a18c0c9854010d72e))
* **python:** 添加grpc反射 ([adee072](https://github.com/Nagico/paperpilot-common/commit/adee072619ae289281f7786ae94aecaea102f0d6))
* **python:** 添加grpc工具 ([076189c](https://github.com/Nagico/paperpilot-common/commit/076189ca64cf89e3665b8238811401098261d78f))
* **python:** 添加grpc运行 ([1d616f6](https://github.com/Nagico/paperpilot-common/commit/1d616f68de1205e431c6b34e2ad8ddb388937fbf))
* **python:** 添加helper ([b911f8b](https://github.com/Nagico/paperpilot-common/commit/b911f8b5ba9361243bfd93b1eaf9b7816a825762))
* **python:** 添加log ([3372b09](https://github.com/Nagico/paperpilot-common/commit/3372b0972a528924ae2bb7713d298b995baa98dc))
* **python:** 添加token过期异常类型 ([979aa18](https://github.com/Nagico/paperpilot-common/commit/979aa18561a297eb090adb00641a73f486297e49))
* **python:** 添加updater更新器 ([b5a8265](https://github.com/Nagico/paperpilot-common/commit/b5a8265be6b00b96ddcff608eef7d10885daaa06))
* **python:** 用户context独立于channel ([368a38d](https://github.com/Nagico/paperpilot-common/commit/368a38de67adff8d1b769858a75b81b780ff0f58))
* **python:** 优化grpc服务 ([8dbd064](https://github.com/Nagico/paperpilot-common/commit/8dbd064db4d7631948b9856ffd43d9c3c0a79d88))
* **python:** 支持多服务反射 ([1e8fa01](https://github.com/Nagico/paperpilot-common/commit/1e8fa0104665f6cd6c2e28eea984d044835df2c0))
* **python:** user context兼容uuid ([18c7b7b](https://github.com/Nagico/paperpilot-common/commit/18c7b7bb124127ac7fbd117ab12613a89006d06b))


### BREAKING CHANGES

* util.OssToken:
减少expire, key等policy重复字段
* AuthService:
重命名为AuthPublicService
AuthService.Register: 响应修改为LoginResponse
