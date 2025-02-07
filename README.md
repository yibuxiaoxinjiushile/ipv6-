这是一个利用ipv6进行屏幕共享的项目。
我希望能在完全不依赖第三方服务器的情况下，仅在服务端启动一个简单的程序，接收方只需在浏览器中就能观看。
这样双方都能无比简单地使用它，且完全不需要为支付任何费用而担忧。

目前有三种版本：
版本号为0.0.x的为图片传帧，这种方式很容易就能实现且延迟较低。
版本号为0.x.x的为流媒体传输，目前尚不稳定，还在研究中。
版本号尾部带有"s"的为包含远程控制的版本。



效果演示可以关注我的Bilibili账号"一不小心就逝了"
注意，远程控制目前尚未添加安全方案，长时间使用有风险，请谨慎使用
流媒体传输的版本中使用了ffmpeg进行屏幕捕获和编码
