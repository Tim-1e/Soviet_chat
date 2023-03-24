@echo off
chcp 65001
echo ============================================免责声明====================================================
echo 为避免可能的法律纠纷和道德风险，使用者在使用该整合包前，请务必仔细阅读本条款，继续使用即代表理解并同意该声明，如有异议，请立即停止使用并删除本整合包。
echo.
echo 1. 本整合包修改自So-VITS-SVC 4.0项目(https://github.com/svc-develop-team/so-vits-svc)，该项目目前由So-VITS社区维护。
echo.
echo 2. 在使用本整合包时，必须根据知情同意原则取得数据集音声来源的授权许可，并根据授权协议条款规定使用数据集。
echo.
echo 3. 禁止使用该整合包对公众人物、政治人物或其他容易引起争议的人物进行模型训练。使用本整合包产出和传输的信息需符合中国法律、国际公约的规定、符合公序良俗。不将本整合包以及与之相关的服务用作非法用途以及非正当用途。
echo.
echo 4. 禁止将本整合包用于血腥、暴力、性相关、或侵犯他人合法权利的用途。
echo.
echo 5. 任何发布到视频平台的基于So-VITS制作的视频，都必须要在简介明确指明用于变声器转换的输入源歌声、音频，例如：使用他人发布的视频/音频，通过分离的人声作为输入源进行转换的，必须要给出明确的原视频、音乐链接；若使用是自己的人声，或是使用其他歌声合成引擎合成的声音作为输入源进行转换的，也必须在简介加以说明。	
echo.			
echo 因使用者违反上述条款中的任意一条或多条而造成的一切后果，均由使用者本人承担，与整合包作者、项目作者以及So-VITS社区无关，特此声明。
echo =========================================================================================================
echo 请输入使用的模型步数（例：模型为G_800.pth就输入800）
set /p step=:
echo 请输入参考的wav干声文件名，该文件应放入raw文件夹下（例：文件名为test.wav就输入test）
set /p wav=:
echo 请输入音高（例：维持原调为0，支持正负，数字为半音）
set /p key=:
echo 聚类方案占比，范围 0-1（例：0为不使用）
set /p cluster=:
echo 请输入是否启用f0自动音高预测（例：0不启用，1启用。转换歌声请勿开启，会跑调）
set /p f0=:
echo ================================ 成功！开始处理 ================================
if "%f0%"=="0" (echo 不启用f0!聚类占比为%cluster% & .\env\python.exe inference_main.py -m "logs/44k/G_%step%.pth" -c "configs/config.json" -n "%wav%" -t %key% -s "barbara" -cm "logs/44k/kmeans_10000.pt" -cr %cluster%) else (echo 启用f0!聚类占比为%cluster% & .\env\python.exe inference_main.py -m "logs/44k/G_%step%.pth" -c "configs/config.json" -n "%wav%" -t %key% -s "barbara" -cm "logs/44k/kmeans_10000.pt" -cr %cluster% -a)
echo ================================ 若无报错结果将输出至result文件夹 ================================
pause