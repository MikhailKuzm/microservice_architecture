import pika
import json
import pandas as pd
import sys

try:
    # Создаём подключение к серверу на локальном хосте
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
   
    # Объявляем очередь y_true
    channel.queue_declare(queue='y_true')
    # Объявляем очередь y_pred
    channel.queue_declare(queue='y_pred')
    dct_que = {'y_true': {}, 'y_pred': {}}
    # Создаём функцию callback для обработки данных из очереди
    def callback(ch, method, properties, body):
        print(f'Из очереди {method.routing_key} получено значение {json.loads(body)}')
        row =json.loads(body)
        print(row)
         
        if method.routing_key == 'y_pred':
             
            if row['id'] in dct_que['y_true']:
                true = dct_que['y_true'][row['id']]
                pred = row['body']
                 
                df = pd.DataFrame(columns = ['id','y_true','y_pred','absolute_error'], data = [[row['id'], true, pred, abs(true-pred)]])
                print(f'{method.routing_key}')
                df.to_csv('.\logs\metric_log.csv', mode='a', header=False)
                del dct_que['y_true'][row['id']]
            else:  
                dct_que['y_pred'][row['id']] == row['body']
            return

        if row['id'] in dct_que['y_pred']:
            pred = dct_que['y_pred'][row['id']]
            true = row['body']
            df = pd.DataFrame(columns = ['id','y_true','y_pred','absolute_error'], data = [row['id'], true, pred, abs(true-pred)])
            df.to_csv('.\logs\metric_log.csv', mode='a', header=False)
            del dct_que['y_pred'][row['id']]
        else: 
            dct_que['y_true'][row['id']] = row['body']
 
    # Извлекаем сообщение из очереди y_true
    channel.basic_consume(
        queue='y_true',
        on_message_callback=callback,
        auto_ack=True
    )
    # Извлекаем сообщение из очереди y_pred
    channel.basic_consume(
        queue='y_pred',
        on_message_callback=callback,
        auto_ack=True
    )
 
    # Запускаем режим ожидания прихода сообщений
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
except:
    print('Не удалось подключиться к очереди')