# home-mlops
Building my own open-source MLOps from scratch

## 1. Step00: local 구조
- local 에서 개발하는 단계이므로 추후 변동 가능성 큼
- mlflow-ui 서버에 기록되는 것들은 학습 소스코드를 실질적으로 실행하는 머신에 존재하는 상태임. 따라서 mlflow-ui 서버와 학습 소스코드를 실행하는 머신이 분리되어 있기 때문에 두 파일 시스템을 연결해야 함
    - 해당 파일 시스템은 Serving에 사용되는 BentoML 서버에도 연결되어야 함. 그래야 모델 로드가 가능할 예정(더 알아보긴 해야 함)
- mlflow-ui는 `train` 디렉토리에서 반드시 실행해야 `mlruns` 디렉토리 한 곳에 모두 히스토리가 남음. 다른 경로에서 실행하면 다른 곳에서 `mlruns` 디렉토리가 중복해서 생겨남
- serving의 경우, 반드시 `bentofile.yaml` 파일이 존재하는 경로에서 셸 스크립트를 실행해야 함

![스크린샷 2024-06-02 오후 5 22 12](https://github.com/young-hun-jo/home-mlops/assets/54783194/32536039-ab68-4f1f-8c11-e7b329521cd7)

## 🔗 Referecne

- mlflow 실행하면서 생성되는 `mlruns` 디렉토리 구조
```
📦mlruns : `mlflow ui` command를 실행하는 경로 기준으로 생성됨
 ┣ 📂$EXPERIMENT_ID
 ┃ ┣ 📂$RUN_ID
 ┃ ┃ ┣ 📂artifacts
 ┃ ┃ ┃ ┗ 📂$ARTIFCAT_PATH : argument of `mlflow.flavor.log_model` function
 ┃ ┃ ┃ ┃ ┣ 📂metadata
 ┃ ┃ ┃ ┃ ┃ ┣ 📜MLmodel : 모델의 확장자, predict function 등 정보가 담김
 ┃ ┃ ┃ ┃ ┃ ┣ 📜conda.yaml : 모델 학습시 구성할 conda 기준 환경
 ┃ ┃ ┃ ┃ ┃ ┣ 📜python_env.yaml : 모델 학습시 구성할 native python 기준 환경
 ┃ ┃ ┃ ┃ ┃ ┗ 📜requirements.txt : 모델 학습 환경 pkg dependency
 ┃ ┃ ┃ ┃ ┣ 📜MLmodel : `metadata` 디렉토리 내 MLmodel 내용과 동일
 ┃ ┃ ┃ ┃ ┣ 📜conda.yaml `metadata` 디렉토리 내 `conda.yaml` 내용과 동일
 ┃ ┃ ┃ ┃ ┣ 📜input_example.json : MLmodel 파일의 `saved_input_example_info.format`의 Serving API에 맞은 샘플 인풋 
 ┃ ┃ ┃ ┃ ┣ 📜model.pkl
 ┃ ┃ ┃ ┃ ┣ 📜python_env.yaml : `metadata` 디렉토리 내 `python_env.yaml` 내용과 동일
 ┃ ┃ ┃ ┃ ┗ 📜requirements.txt : `metadata` 디렉토리 내 `requirements.txt` 내용과 동일
 ┃ ┃ ┣ 📂metrics : `log_metrics` 함수에 넣은 `dict[str, float]` 자료구조로, key가 filename이 되며, value가 content of file이 됨(nested json 구조 불가)
 ┃ ┃ ┃ ┣ 📜accuracy 
 ┃ ┃ ┃ ┣ 📜f1-score
 ┃ ┃ ┃ ┣ 📜precision
 ┃ ┃ ┃ ┗ 📜recall
 ┃ ┃ ┣ 📂params : `log_params` 함수에 넣은 `dict[str, Any]` 자료구조로, key가 filename이 되며, value가 content of file이 됨
                  (단, nested dictionary 가능하지만, nested일 경우, 가장 바깥에 있는 key가 filename이 되고 나머지 json string이 content of file이 됨)
 ┃ ┃ ┃ ┣ 📜max_iter
 ┃ ┃ ┃ ┣ 📜multi_class
 ┃ ┃ ┃ ┣ 📜random_state
 ┃ ┃ ┃ ┗ 📜solver
 ┃ ┃ ┣ 📂tags : Single Run에 기본적으로 남겨지는 태그 정보와 사용자가 `set_tag` 함수로 추가로 남길 수 있는 태그 정보들
 ┃ ┃ ┃ ┣ 📜mlflow.log-model.history : 모델 스키마, 사이즈 등 모델에 대한 정보가 남겨짐
 ┃ ┃ ┃ ┣ 📜mlflow.runName : `mlflow.start_run`의 `run_name`에 넘겨지는 이름
 ┃ ┃ ┃ ┣ 📜mlflow.source.name : 학습 소스코드 실행된 스크립트명. 단, CLI에서 해당 스크립트를 실행했을 때의 현재 기준 경로로 명시됨
 ┃ ┃ ┃ ┣ 📜mlflow.source.type : 어떤 환경에서 실행되었는지 명시. 기본값은 `LOCAL` 이나 사용자가 `set_tag` 함수로 overwrite 할 수 있음(ex. dev, staging, prod 등.. 다양한 커스텀 환경 명시 가능)
 ┃ ┃ ┃ ┣ 📜mlflow.user : 머신에 설정된 `USER` 환경 변수
 ┃ ┃ ┃ ┣ 📜mlflow.source.git.commit : 학습 소스코드가 있는 레포지토리가 git 레포지토리라면 그 레포지토리에서 가장 최종 commit 상태의 해쉬값이 명시됨
           (따라서 [학습할 소스코드를 수정 -> commit -> 소스코드 실행] 순으로 실행되어야 학습한 소스코드의 스냅샷에 대한 commit 해쉬값이 잘 남음)
 ┃ ┃ ┃ ┗ 📜(ex)Training-info : 사용자가 `set_tag` 함수로 남기는 값. `set_tag(key, value)`에서 key가 filename이, value가 content of file이 됨
 ┃ ┃ ┗ 📜meta.yaml : Single Run에 대한 id, name, 해당 Run이 속한 Experiment id, 해당 Run이 만들어낸 artifact 경로가 들어있음
 ┃ ┗ 📜meta.yaml : Single Experiment에 대한 id, name, 해당 Experiment의 경로가 들어있음
 ┗ 📂models : mlflow-ui에서 `Models` 탭에 있는 정보들
 ┃ ┗ 📂$REGISTERED_MODEL_NAME : `mlflow.flavor.log_model`의 `registered_model_name` argument에 명시되는 값
 ┃ ┃ ┣ 📂version-1 
 ┃ ┃ ┃ ┗ 📜meta.yaml : 해당 모델과 연결되는 Run id, 해당 모델 객체가 있는 경로가 들어있음
 ┃ ┃ ┣ 📂version-2
 ┃ ┃ ┃ ┗ 📜meta.yaml : 해당 모델과 연결되는 Run id, 해당 모델 객체가 있는 경로가 들어있음
 ┃ ┃ ┗ 📜meta.yaml : $REGISTERD_MODEL_NAME에 대한 이름과 해당 모델의 1번째 버전이 언제 만들어졌고, 가장 최근에 만들어진 버전이 언제 만들어졌는지에 대한 정보
 ┗ 📂.trash : mlflow-ui에서 삭제시킨 Experiment, Run에 대한 정보가 임시로 담기는 공간이라고 함
              (하지만 테스트 해보았을 때는 삭제한 Run 또는 Experiment가 `.trash` 디렉토리로 옮겨지지 않고 원래 경로에 그대로 있음. 심지어 mlflow-ui 서버를 재시작해도 삭제시킨 Run 또는 Experiment가 ui 상에서 복원되는 것도 아님)
```
