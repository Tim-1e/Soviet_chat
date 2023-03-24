@echo off
chcp 65001
echo ================================ 启动TensorBoard ================================
echo.
echo 若启动正常，你应当能看到类似于TensorBoard 2.12.0 at http://localhost:6006/ (Press CTRL+C to quit)的输出
echo.
echo 保持bat运行，将你的网址输入浏览器查看TensorBoard
echo.
.\env\python.exe .\env\Scripts\tensorboard.exe --logdir=.\logs
pause