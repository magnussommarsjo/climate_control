FROM python:3.9
WORKDIR /climate_control
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY pyproject.toml setup.cfg ./
COPY src src
RUN pip install .
CMD ["python", "src/controller/main.py"]