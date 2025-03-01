import pika
import pickle
import numpy as np
import json

# Читаем файл с сериализованной моделью
with open('myfile.pkl', 'rb') as pkl_file:
    regressor = pickle.load(pkl_file)

# Создаём подключение к серверу на локальном хосте:
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

# Объявляем очередь features
channel.queue_declare(queue='features')
# Объявляем очередь y_pred
channel.queue_declare(queue='y_pred')
 
# Создаём функцию callback для обработки данных из очереди y_pred
def callback(ch, method, properties, body):
    print(f'Получен вектор признаков {body}')
    features = json.loads(body)['body']
    id = json.loads(body)['id']
    pred = regressor.predict(np.array(features).reshape(1, -1))
    channel.basic_publish(exchange='',
                      routing_key='y_pred',
                      body=json.dumps({'id': id, 'body': pred[0]}) )
    print(f'Предсказание {pred[0]} отправлено в очередь y_pred')

# Извлекаем сообщение из очереди features
# on_message_callback показывает, какую функцию вызвать при получении сообщения
channel.basic_consume(
    queue='features',
    on_message_callback=callback,
    auto_ack=True
)
print('...Ожидание сообщений, для выхода нажмите CTRL+C')

# Запускаем режим ожидания прихода сообщений
channel.start_consuming()