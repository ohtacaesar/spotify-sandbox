### メモ

- JWTにaudが含まれている場合、decodeの引数にaudを渡して一致するか検証する必要あり
    - 一致しない場合はエラーに
    - user_idはaudではなくsubに

### 参考

[Atomic Designをやめてディレクトリ構造を見直した話](https://note.com/tabelog_frontend/n/n07b4077f5cf3)
