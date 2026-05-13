FROM public.ecr.aws/lambda/python:3.11

# 의존성 설치
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt --target ${LAMBDA_TASK_ROOT}

# 소스 복사
COPY . ${LAMBDA_TASK_ROOT}

# Lambda 핸들러 지정
CMD ["lambda_function.lambda_handler"]
