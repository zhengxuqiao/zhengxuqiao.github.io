
pushd E:\族谱\族谱本地文件夹\家谱文件\跳板网页文件\自建网页\WWW\zhengxuqiao.github.io

:: 删除子文件夹中的文件
del .\.git\index.lock

:: echo 当前盘符路径：%~dp0
:: echo 当前路径下文件：
:: dir /b

git add -A
git commit -m "test"
git push -u origin master -f

popd
