### (Armature) Chain to SplineIK.py

1繋ぎのボーンにスプラインIKを設定します。

===================

ポーズモードで対象とするボーンを選択した状態でスクリプトを実行。

![.](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/(Armature) Chain to SplineIK/1.png)

するとカーブとフック用Armatureが生成され、元の選択していたボーンにはスプラインIKが設定されます。

![.](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/(Armature) Chain to SplineIK/2.png)

カーブのコントロールポイントごとにフック用ボーンがアサインされます。これによりシェイプキーを使わずにカーブの形を制御できます。

![.](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/(Armature) Chain to SplineIK/3.png)


===================

#### フックArmatureの統合

スプラインIKを設定したい Armature _(A)_ とはまた別の Armature _(B)_ を選択してから _(A)_ を同時選択(Shift+クリックで選択)してスクリプトを実行することで、生成したフックArmatureを事前に選択していた _(B)_ に統合することができます。

![.](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/(Armature) Chain to SplineIK/b1.png)
![.](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/(Armature) Chain to SplineIK/b2.png)

上記の手順を踏まない場合ではフックArmatureは別々のオブジェクトとして生成されますが、一つのArmatureに統合されていたほうが使いやすいことや、複数のフックArmatureを後になって一つに統合しようとする場合に単純にJoinするだけでは上手くいかないことなども踏まえると、なるべく最初から一つのArmatureに統合するようにしておいた方がいいです。

(そのうちバージョンアップで統合を強制するようにするかもしれません。)

===================

#### フックの数(＝カーブのコントロールポイントの数)の設定

スクリプトの上部にある `class Pref` の `control_hook_number` の値を変えることで、生成されるカーブ用フックの数が変更可能です。

デフォルトは`3`になっています。実用上は多くても`5`程度で十分でしょう。

![.](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/(Armature) Chain to SplineIK/4.png)

![.](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/(Armature) Chain to SplineIK/5.png)

![.](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/(Armature) Chain to SplineIK/6.png)

![.](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/(Armature) Chain to SplineIK/7.png)


===================

#### 注意点

* 選択しているボーンの中に途中で枝分かれしている(子が複数ある)ボーンがある場合はサポートしていません。
* スプラインIKを設定するボーンは一旦 Rest Position にしてからでないとうまく設定されない場合があります。
* 複数のボーンが入り組んでくるとカーブのフックの初期位置を示す点線(Relationship Lines)が鬱陶しくなってきますが、その場合はカーブだけを別の非表示レイヤに移動させれば余計な線がなくなって見やすくなります。元々カーブを直接編集する必要はないので、最初から非表示にしておくのも手です。
    
* 生成した各フックを元の(スプラインIKを設定した)Armatureのボーンの動きに追従したい時などで、フック用Armatureを元のArmatureの中のボーンに対してParentを設定すると、Cyclic Dependancy警告が出ます。これは 元のArmatureのボーン→(スプラインIK)カーブ→フック用ボーンArmature→元のArmatureのボーンという流れで依存が循環してしまうせいですが、このままだと微妙に不具合が出るため、間にまた別のコントロール用Armatureを挟むことで対処するといいと思います。

    ![.](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/(Armature) Chain to SplineIK/c1_.gif)
    
    例えば上の画像だと、DeformArmature を対象に本スクリプトで生成した SplineIK_Control_Hooks は ControlArmature のボーンに対してParentを設定しているので、ControlArmatureの動きに追従しています。また DeformArmature はそれぞれのボーンに Copy Transforms コンストレイントが割り当てられていて、対応する ControlArmature のボーンの動きをコピーしています。
    
    これで依存の流れは
    * **(Spline IK Constraint)** DeformArmature → Curve → SplineIK_Control_Hooks → ControlArmature
    * **(Copy Transforms Constraint)** DeformArmature → ControlArmature
    
    のようになり、循環がなくなるため Cyclic Dependancy 警告を出さずに済むことになります。

===================
<!--
![a](https://raw.githubusercontent.com/wiki/a-nakanosora/blender-scripts/images/test.png)
-->

