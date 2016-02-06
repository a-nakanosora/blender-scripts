### Curve scripts


===================

##### Curve Point Divide / Curve Point Bevel (& refresh)

![image](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/Curve/divide_bevel.gif)


* Curve Point Divide - カーブの頂点を2つに分離させる
* Curve Point Bevel - カーブの頂点を密集した3つに分離させる。鋭角を出したいときに使用
* Curve Point Bevel refresh - Point Bevel で生成した3つの頂点の位置関係を再設定する。頂点は3つ選択するか、中央の1つを選択した状態で実行

今のところNURBSカーブ専用です。

ちなみに上の動画では [External Script Executer](https://github.com/a-nakanosora/blender-addon-external-script-executer) を通してショートカットキーから実行してます。

===================

##### Set Curve Deform

![image](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/Curve/curvedeform.gif)

* メッシュオブジェクト→カーブオブジェクトの順に複数選択した状態で実行することでメッシュオブジェクトにCurve Deformを設定。

またオブジェクトにはカーブへのCopy Locationコンストレイントも設定されます。

===================

##### Set Curve Dupli Frames

![image](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/Curve/dupli.gif)

* 使い方はSet Curve Deformに同じ

メッシュオブジェクトにDupli Framesを利用してのカーブに沿った複製を設定します。


<br>
