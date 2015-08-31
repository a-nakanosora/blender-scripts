### (Armature) Attach Deformer to Controller

Deform 用の Armature _(Deformer)_ と Control 用の Armature _(Controller)_ の2つがあるとき、Controller によって  Deformer を動かすために、 Controllerのボーンに対応するDeformerのボーンそれぞれにCopy Transformsコンストレイントを設定します。

===================

![image](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/(Armature) Attach Deformer to Controller/a1.gif)

使い方：
* Deformer を選択してから Controller を同時選択 (Shift を押しながら選択) してスクリプトを実行。

  Deformerのボーンに Copy Transforms コンストレイントが設定されます。

<br>

両者の対応関係はボーンの名前のみで判別してます。つまり、Deformer のあるボーンと同名のボーンが Controller にある場合にコンストレイントが設定されるという流れになってます。

===================

関連：
* [blender-scripts/(Armature) Chain to SplineIK](https://github.com/a-nakanosora/blender-scripts/tree/master/(Armature)%20Chain%20to%20SplineIK)


<br>

