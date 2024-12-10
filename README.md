[English](./README_en.md)

# プロジェクトテンプレートの利用
このリポジトリの画面右上にある`Use this template`ボタンを押して、`Create a new repository`を選択する。あとはいつも通り。このリポジトリの画面を開かずとも、ABEJA organizationで新しくリポジトリを作成する際にテンプレートを選択出来るようになっているので、このテンプレートを選択する。

# Dockerコンテナのセットアップ
## Specify Python version
`context/<cpu or gpu>`配下の`docker-compose.yml`でPythonのバージョンを指定する。Jupyter Labを使用する場合は`ports`のコメントアウトを外す。デフォルトでポート8888を使うため、DGXなどの共通利用のマシン上で起動する場合などは空いているポートを確認し、`docker-compose.yml`の`ports`のソースを変更する。


## Build & Run docker container
以下のコマンドを実行してイメージ作成、Dockerコンテナを立ち上げる。このコマンドによって`.env_project`が生成される。この`.env_project`を環境変数ファイルとして`docker-compose.yml`で使用している。

With cpu
```
make init-docker-cpu
```

With gpu
```
make init-docker-gpu
```

# 分析環境のセットアップ
## For VSCode
### Connect into docker container with VSCode
VSCodeの`Dev Containers`拡張機能で立ち上げたコンテナにVSCodeをアタッチする

### Setup VSCode
コンテナ内で以下のコマンドを実行してVSCodeの最低限の拡張機能をインストールする
```
make setup-vscode
```

## For JupyterLab
ローカル環境であれば以下のコマンドを実行してJupyter Labを起動する。
```
make start-jupyter
```

起動したら[http://127.0.0.1:8888/lab](http://127.0.0.1:8888/lab)にアクセスする。ポートを変えている場合は適宜8888の部分を変更する。また、DGXなどの共有マシンで起動する場合は以下のようにSSHポートフォワーディングしてから上記に接続する。
```
$ ssh -N -L 8888:localhost:{コンテナと繋がっているDGXのポート番号} dgx1a
```

ホストOSがWindowsの場合は`%USERPROFILE%/.wslconfig`を作成し、以下を記載する。（作成後、WSLを一度shutdownする）
```
[wsl2] 
localhostForwarding=true
```

終了したらJupyterLabをshutdownする。JupyterLabのGUIからshutdownしてもいいし、以下のコマンドでコンテナを停止してもいい。
```
make docker-stop
```

# Install Python packages
仮想環境の作成とパッケージのインストールをする
```
make setup-poetry
```

# ディレクトリ構成
このリポジトリは以下のディレクトリで構成されています。

- .github: GitHub workflowなど
    - [pull_request_template.md](./.github/pull_request_template.md): PRテンプレートの設定ファイル
    - workflows
        - [lint.yaml](./.github/workflows/lint.yaml): DockerfileのlintとPythonパッケージのlintを行うworkflowの設定ファイル
            - lint_python_scriptsについて
                - ベースコミットと比較して差分のあるPythonスクリプトを含むPythonパッケージに対してlintを実行します。
                - 差分が無い場合はlintは実行されません。
- [.vscode](./.vscode): VSCode利用時のsettingsファイル
    - [settings.json](./.vscode/settings.json): 適宜設定を変更してください。formatOnSaveはデフォルトでoffになっています
- context: Dockerfileと、CPU、GPU環境向けのdocker-compose.ymlがそれぞれ格納されています。
    - [Dockerfile](./context/Dockerfile)
    - [.hadolint.yaml](./context/.hadolint.yaml)
    - cpu
        - [docker-compose.yml](./context/cpu/docker-compose.yml)
    - gpu
        - [docker-compose.yml](./context/gpu/docker-compose.yml)
- experimentation: 実験用のnotebookやデータセット、出力を格納するディレクトリ
    - [dataset](./experimentation/dataset/): データセットを配置するディレクトリ
    - [latest](./experimentation/latest/): 最新の実験パラメータや結果を格納するディレクトリ
    - [notebooks](./experimentation/notebooks/): 実験用notebookを配置するディレクトリ
    - [outputs](./experimentation/outputs/): 実験の出力を格納するディレクトリ
- libs: プロジェクト固有ではないモジュールやgit submoduleを置いておく場所
    - [abeja-toolkit](./libs/abeja-toolkit/): ABEJAの社内Pythonライブラリの一部。デフォルトでは以下のツールが含まれている。
        - [notebook_exporter](./libs/abeja-toolkit/notebook_exporter/): notebookをNotionページに変換するツール
        - [notion_extension](./libs/abeja-toolkit/notion_extension/): Notion APIをハンドリングするツール
        - [spreadsheet](./libs/abeja-toolkit/spreadsheet/): スプレッドシートのデータを読み込んだり、スプレッドシートにデータを書き込むツール
- [project_module](./project_module/): プロジェクト固有のモジュールを実装するPythonパッケージテンプレート。このPythonパッケージをeditableモードでinstallし、importして使用します。スクリプトは適宜追加してください。
    - [tests](./project_module/tests/): 単体テストなどのテストモジュールを実装する
    - src
        - [project_module](./project_module/src/project_module/): この配下にスクリプトを格納していく
            - [prediction](./project_module/src/project_module/prediction/): 予測・推論パイプライン用のスクリプトを格納するディレクトリ
                - [config.py](./project_module/src/project_module/prediction/config.py): `PredictionPipeline`で使用するconfigスクリプト
                - [io.py](./project_module/src/project_module/prediction/io.py): `PredictionPipeline`の入出力を定義するスクリプト
                - [pipeline.py](./project_module/src/project_module/prediction/pipeline.py): 予測用のパイプラインクラス`PredictionPipeline`を実装するスクリプト
            - [training](./project_module/src/project_module/training/): 学習パイプライン用のスクリプトを格納するディレクトリ
                - [config.py](./project_module/src/project_module/training/config.py): `TrainingPipeline`で使用するconfigスクリプト
                - [io.py](./project_module/src/project_module/training/io.py): `TrainingPipeline`の入出力を定義するスクリプト
                - [pipeline.py](./project_module/src/project_module/training/pipeline.py): 学習用パイプラインクラス`TrainingPipeline`を実装するスクリプト
            - [common_config.py](./project_module/src/project_module/common_config.py): 学習、予測に共通する全般的なconfigを定義するスクリプト
    - [pyproject.toml](./project_module/pyproject.toml): `project_module`の依存関係を記述するファイル
    - [README.md](./project_module/README.md): `project_module`の利用法を記載したファイル
- [pyproject.toml](./pyproject.toml): ルートディレクトリ直下のpyproject.toml。ここには開発用パッケージの依存関係などを定義する。`package-mode = false`にしているため、ルートディレクトリはパッケージとみなされない（※`package-mode`はpoetry >= 1.8で利用可能です。）
- README.md: このプロジェクトテンプレートの利用方法を記載しているファイル
- README_en.md: プロジェクトテンプレートの利用方法（英語版）


# Linting
devグループの依存関係をinstallしていれば、mypyとruffのlintチェックが以下のコマンドで実行出来ます。

```shell
make lint /path/to/module
```

# NotebookをNotionページに変換する
認証などを済ませて以下のコマンドを実行すると、指定したタイトルのNotionページが自動で生成され、notebook内のMarakdownセルとセル出力がNotionブロックに変換されます。詳細な利用方法は`notebook_exporter`の[README.md](./libs/abeja-toolkit/notebook_exporter/README.md)をご確認ください。

```
make to-notion /path/to/notebook.ipynb <notion_page_title>
```

# Notebookの出力を消す

Notebookのセル出力に機密情報を含む場合、GitHubにpushする前に出力を消すことを推奨します。以下のコマンドで一括で指定したディレクトリ配下のnotebook出力を削除することが出来ます。

```
make reset-notebook /path/to/directory/
```