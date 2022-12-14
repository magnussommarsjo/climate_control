FROM python:3.10
WORKDIR /climate_control
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY pyproject.toml setup.cfg ./
COPY src src
RUN pip install .
HEALTHCHECK CMD curl --fail http://localhost/health || exit 1
CMD ["python", "src/controller/main.py"]