### 실행에 필요한 module 설치
> 소스 폴더를 보면 requirements.txt가 있는 것을 확인 할 수 있다.
```shell
$ ls -al
```
> 가상환경(virtualenv) 생성
```shell
--가상환경 모듈이 없을 경우 설치 실행
$ pip install virtualenv 
-- 아래 명령어를 실행하여 venv란 가상환경 설정 (가상환경 신규 생성이 필요한 경우에만 실행)
$ virtualenv venv
$ source venv/bin/activate
```

> dependency module 설치
```shell
$ pip install -r requirements.txt
```

### 실패 시 수작업 
> NoBatch 실행
```python
# 라이브 실행 시
$ python NoBatchMain.py L
# 데이터 홈쇼핑 실행 시
$ python NoBatchMain.py T
```

### 서버 접근
> sudo권한으로 변경
```shell
$ sudo -i
$ su - service

$ cd applications

```
