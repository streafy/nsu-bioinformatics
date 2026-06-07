### Ссылка на загруженные прочтения из NCBI SRA

- [NCBI SRA ERR16175435](https://www.ncbi.nlm.nih.gov/sra/ERR16175435)
- [NCBI Trace ERR16175435](https://trace.ncbi.nlm.nih.gov/Traces/?run=ERR16175435)

### Скрипт на bash с реализованным алгоритмом

[`scripts/quality_mapping.sh`](scripts/quality_mapping.sh)

### Результат команды `samtools flagstat`

[`results/ERR16175435/flagstat.txt`](results/ERR16175435/flagstat.txt)

### Скрипт разбора файлов с этими результатами

[`scripts/parse_flagstat.py`](scripts/parse_flagstat.py)

### Инструкцию по развертыванию и установке фреймворка

Использованный фреймворк: `Luigi`.

Установка:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Файл зависимостей:

[`requirements.txt`](requirements.txt)

### Код любого тестового пайплайна ("Hello world") на фреймворке

Код:

[`luigi_pipeline/hello_luigi.py`](luigi_pipeline/hello_luigi.py)

Запуск:

```bash
source .venv/bin/activate
python -m luigi --module luigi_pipeline.hello_luigi HelloWorld --local-scheduler
```

### Результаты работы пайплайна на фреймворке и лог-файлы

[`results/hello_luigi.txt`](results/hello_luigi.txt)

### Код пайплайна "оценки качества картирования" на фреймворке

Код Luigi pipeline:

[`luigi_pipeline/mapping_pipeline.py`](luigi_pipeline/mapping_pipeline.py)

Запуск:

```bash
source .venv/bin/activate
python -m luigi --module luigi_pipeline.mapping_pipeline MappingQualityPipeline --local-scheduler
```

### Выведенные результаты работы пайплайна на загруженных данных в отдельном файле

[`results/ERR16175435/luigi/mapping_status.txt`](results/ERR16175435/luigi/mapping_status.txt)

### Лог-файлы работы пайплайна на загруженных данных

Логи bash-скрипта:

[`results/ERR16175435/logs/quality_mapping.log`](results/ERR16175435/logs/quality_mapping.log)

Логи Luigi pipeline:

[`results/ERR16175435/luigi/logs/pipeline.log`](results/ERR16175435/luigi/logs/pipeline.log)

### Визуализацию пайплайна в виде графического файла

Файл визуализации:

[`results/luigi_dag.png`](results/luigi_dag.png)

### Описание использованного способа визуализации и отличия полученной визуализации от блок-схемы алгоритма

Визуализация выполнена через встроенный веб-интерфейс Luigi Task Visualiser. 

Для этого был запущен центральный планировщик:

```bash
luigid --port 8082
```

После был запущен пайплайн:

```bash
python -m luigi --module luigi_pipeline.mapping_pipeline MappingQualityPipeline --scheduler-host localhost --scheduler-port 8082
```

После запуска пайплайна граф был открыт в браузере по адресу:

```text
http://localhost:8082/static/visualiser/index.html#tab=graph&taskId=MappingQualityPipeline__99914b932b&visType=d3
```

Полученная визуализация является DAG: она показывает зависимости между задачами пайплайна. Блок-схема из задания показывает последовательность алгоритма и условную проверку `% mapped > 90%`. В Luigi эта проверка реализована как задача `EvaluateMapping`.
