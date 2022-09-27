FROM python:3.9
WORKDIR /climate_control
COPY . .
RUN pip install .
CMD ["python", "src/controller/main.py"]