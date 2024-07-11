# home-mlops
Building my own open-source MLOps from scratch

- 나홀로 집에서 구축하는 Home MLOps 시스템은 다음의 환경에 따라 실행 방법이 상이함
    - localhost 개발 환경
    - k8s 운영 환경

## 1. localhost
localhost 에서의 애플리케이션 아키텍처 구조는 다음과 같음

![스크린샷 2024-07-12 오전 12 04 11](https://github.com/young-hun-jo/home-mlops/assets/54783194/f289e2c3-04c5-40c8-907a-48b9505ba6b2)


### 1-2. Tutorials
#### Step00: Introduction 
- clone github repository
```bash
git clone https://github.com/young-hun-jo/home-mlops.git
```
- structure of projcet
```
home-mlops
┣ common 
┣ serving
┃ ┣ $APP_NAME_1
┃ ┃ ┣ bento-ml
┃ ┃ ┣ fast-api
┃ ┣ $APP_NAME_2
┃ ┃ ┣ bento-ml
┃ ┃ ┣ fast-api
┣ training
┃ ┣ mlruns       # directory archiving artifacts and metadata for trained model in MLflow
┃ ┣ $APP_NAME_1
┃ ┃ ┣ train.py
┃ ┣ $APP_NAME_2
┗ ┗ ┗ train.py
```

- install dependencies
```bash
pip install -e home-mlops/common
```
- 학습된 모델에 대한 다양한 artifacts, metadata를 트래킹할 수 있는 MLflow UI 서버를 컨테이너 형태로 배포
```bash
home-mlops/training/deploy.sh
```
- Container Registry Repository 2개를 생성
    - ex) Docker-hub, Github Container Registry, Google Cloud Artifact Registry, ...
    - BentoML Serving 용 1개
    - FastAPI Serving 용 1개
    - <a href='https://hub.docker.com/repositories/jo181'>example registry</a>

#### Step01: Training
- 오픈소스 모델을 사용해서 학습시키되 반드시 스크립트에 `set_mlflow_backend_store_uri` 함수를 initialize 시켜주기
```python
from home.utils import set_mlflow_backend_store_uri

import mlflow

# necessarily initialize !
set_mlflow_backend_store_uri()


...(train source code)...
```

#### Step02: Build Serving(1) - BentoML
- 4가지 파일이 필요
```
build.sh : build Bento, image, and push it to container registry
bentofile.yaml : configuration for building Bento
import.py : save model trained by MLflow to BentoML Model Store
service.py : define BentoML Serving API (only defined functional interface not Class)
```
- 4개의 argument를 입력한 후 `build.sh` 스크립트 실행
- 이 때, 반드시 `bentofile.yaml` 파일이 존재하는 경로에서 스크립트를 실행
```bash
export MLFLOW_EXPERIMENT_ID="experiment-id"     # MLflow에 모델이 학습될 때 등록된 실험 ID
export MLFLOW_RUN_ID="run-id"                   # MLflow에 모델이 학습될 때 등록된 Run ID
export APP_NAME="iris-classifier"               # 만들고자 하는 애플리케이션 이름 명시
export BENTOML_AR_NAME="jo181/bentoml-serving"  # image가 저장될 registry repository 주소 

./build.sh $MLFLOW_EXPERIMENT_ID $MLFLOW_RUN_ID $APP_NAME $BENTOML_AR_NAME
```
- registry에 가서 push된 이미지 이름 확인 후, 배포 때 활용 예정
- 참고로, 빌드가 되면서 `bentofile.yaml`에 정의되어야 하는 `.python.packages`, `.models` 항목은 자동 반영되므로 별도로 사용자가 수정하지 않아도 됨

#### Step03: Build Serving(2) - FastAPI
- BentoML Serving API와 통신하는 로직을 추가여 소스코드 개발(<a href='https://github.com/young-hun-jo/home-mlops/blob/e277ef86d50a72b101b5c429c1e8d9e870d083f4/serving/tabular-iris-multi-classifier/fast-api/app/models/inference.py#L32-L36'>example</a>)
- 2개의 argument를 입력한 후, `build.sh` 스크립트 실행
- 이 때, 반드시 `Dockerfile` 파일이 존재하는 경로에서 스크립트를 실행
```bash
export APP_NAME="iris-classifier" # 만들고자 하는 애플리케이션 이름 명시(BentoML에서의 이름과 동일 권장)
export FASTAPI_AR_NAME="jo181/fastapi-serving"  # image가 저장될 registry repository 주소

./build.sh $APP_NAME $FASTAPI_AR_NAME
```
- registry에 가서 push된 이미지 이름 확인 후, 배포 때 활용 예정

#### Step04: Deployment
- `docker-compose.yaml` 파엘에 아래의 내용을 기입
```yml
version: '3.0'
services:
  ${APP_NAME}-bento-svc:
    image: `specify your bento image uri`
    environment:
      - BENTOML_SVC_NAME=${APP_NAME}-bento-svc
      - BENTOML_MODEL_NAME=${APP_NAME}-bento-model
    command: serve
  ${APP_NAME}-fastapi-svc:
    image: `specify your fastapi image uri`
    ports:
      - "8000:8000"
    depends_on:
      - ${APP_NAME}-bento-svc
```
- BentoML, FastAPI 배포
```bash
docker-compose up -d
```

#### Step05: Test
- FastAPI application URL
```
http://localhost:8000
```


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
