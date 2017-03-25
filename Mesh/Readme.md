> ##### Extrude Face Along Hair.py

メッシュオブジェクトの各Faceを、同オブジェクトに設定された Hair Particle のパスに従って押し出したメッシュを新たに生成します。

<img src="./doc/img/Extrude Face Along Hair--b.jpg" width="500px">

<img src="./doc/img/Extrude Face Along Hair--d.jpg" width="500px">

* 複数本の Hair パスが1つのFaceから生えている場合、その内の1本のみが使用されます。
* Hair Dynamics を利用する場合は事前に Hair を Bake しておく必要があります。
* Hair Particle の `Vertex Groups` による変更は今のところ正しく適用されません。
