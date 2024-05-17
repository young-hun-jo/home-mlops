# home-mlops
Building my own open-source MLOps from scratch

## 1. Step00: local 구조
- local 에서 개발하는 단계이므로 추후 변동 가능성 큼
- mlflow-ui 서버에 기록되는 것들은 학습 소스코드를 실질적으로 실행하는 머신에 존재하는 상태임. 따라서 mlflow-ui 서버와 학습 소스코드를 실행하는 머신이 분리되어 있기 때문에 두 파일 시스템을 연결해야 함
    - 해당 파일 시스템은 Serving에 사용되는 BentoML 서버에도 연결되어야 함. 그래야 모델 로드가 가능할 예정(더 알아보긴 해야 함)
 
![스크린샷 2024-05-17 오후 10 24 47](https://github.com/young-hun-jo/home-mlops/assets/54783194/c3cc1d7d-27a1-4cb1-abd4-9e85906ff52e)
