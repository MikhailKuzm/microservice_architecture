import pika
import numpy as np
import json
import time
from sklearn.datasets import load_diabetes
from datetime import datetime

np.random.seed(42)
# Загружаем датасет о диабете
X, y = load_diabetes(return_X_y=True)
 

# Подключение к серверу на локальном хосте:
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

# Создаём очередь y_true
channel.queue_declare(queue='y_true')
# Создаём очередь features
channel.queue_declare(queue='features')

# Публикуем сообщение в очередь y_true
while True:
    # Формируем случайный индекс строки
    random_row = np.random.randint(0, X.shape[0]-1)
    message_id = datetime.timestamp(datetime.now())
    message_features = {
    'id': message_id,
    'body': list(X[random_row])
    }
    message_y_true = {
    'id': message_id,
    'body': y[random_row]
    }
    #json.dumps(y[random_row]) json.dumps(list(X[random_row])))
    channel.basic_publish(exchange='',
                        routing_key='y_true',
                        body=json.dumps(message_y_true ))
    print('Сообщение с правильным ответом отправлено в очередь')

    # Публикуем сообщение в очередь features
    channel.basic_publish(exchange='',
                        routing_key='features',
                        body=json.dumps(message_features))
    print('Сообщение с вектором признаков отправлено в очередь')
    time.sleep(5)

# Закрываем подключение
connection.close()