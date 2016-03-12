
==================
> ##### (Debug) Clear Console.py

コンソールウィンドウをクリアします。(Windows以外で動作するかは不明)


==================
> ##### (Debug) store context.py

`bpy.a`, `bpy.b`にスクリプト呼び出し時のコンテキスト値`bpy.context`のコピーを格納します。

e.g. `bpy.a["active_object"].data`/ `bpy.b.active_object.data`



==================
> ##### (Object) Name to clipboard.py

アクティブなオブジェクトの名前をクリップボードにコピーします。

オブジェクトがArmatureでPoseモードの時はアクティブなボーンの名前がコピーされます。


==================
> ##### (Vertex Paint) toggle brush color WB.py

Vertex Paintモードで実行。選択中のカラーを白(1,1,1)か黒(0,0,0)の2つでトグルします。



==================
> ##### paths.py

開いているblendファイルが使用している外部ファイルへのパスの一覧をコンソールに表示します。

相対パスか絶対パスかはblendファイルでの使用状態に従います。




