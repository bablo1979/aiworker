
import json
import socket
from kafka import KafkaConsumer
import sys
import logging
import asyncio
from config import Config
from neutrai_client import NeutraAIClient
from openai import OpenAI
sys.stdout.flush()
print("Kickstart")
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s %(message)s')

config = Config()

host = config.get_required('KAFKA_URI')
port = config.get_required('KFAKA_PORT')
print(sys.version)



async def generate_questions(dispute_uuid):
    sbc = NeutraAIClient(config)
    dispute_info = sbc.get_dispute_info(dispute_uuid=dispute_uuid)
    dispute = dispute_info['dispute']
    part_0 = dispute_info['partecipants'][0]
    part_1 = dispute_info['partecipants'][1]

    print(dispute)

    main_prompt = f"""
Sei un mediatore esperto ed imparziale.
Devi generare domande 10 neutre da porre a $partecipant_1 e 10 domande neutre da porre a $partecipant_2 per comprendere meglio la situazione.
Alcune delle domande devono essere poste ad entrambi i partecipanti a seconda della questione. 
I  partecipanti alla disputa sono "{dispute['partecipants_relationship']}". 
L'output deve essere esclusivamente in formato JSON con questa struttura: {{"questions": [ {{ "user_uuid": {part_0['uuid']}, "text": "..." }}, {{ "user_uuid": {part_1['uuid']}, "text": "..." }} ] }}
Usa esattamente questi user_id:
Utente {part_0['uuid']} = {part_0['name']}
Utente {part_1['uuid']} = {part_1['name']}
Non includere commenti o spiegazioni nel risultato, solo JSON puro.    
    """
    init_prompt = f"""
{part_0['name']} ha dato come contesto iniziale il seguente: {dispute['initial_statement']}
"""

    openai_cli = OpenAI(api_key=config.get_required('OPENAI_KEY'))

    msgs = [
        {"role": "system", "content": main_prompt},
        {"role": "user", "content": init_prompt}
    ]
    completion  = openai_cli.chat.completions.create(
        model="gpt-4",
        messages=msgs
    )
    for choice in completion.choices:
        questions = json.loads(choice.message.content)
        print(questions)
        sbc.store_questions(dispute_uuid=dispute_uuid, questions=questions)


#generate_questions('2ce29ccd-5447-11f0-9e95-fe1414fda368')
#sys.exit()

try:
    socket.create_connection((host, port), timeout=5)
    print(f"✅ Kafka ({host}:{port}) raggiungibile!")
except Exception as e:
    print(f"❌ Kafka ({host}:{port}) NON raggiungibile! Errore: {e}")

consumer = KafkaConsumer(
    bootstrap_servers='{0}:{1}'.format(host,port),
    group_id='neutrai-consumer',
    auto_offset_reset='earliest',
    enable_auto_commit=False,
    value_deserializer=lambda m: m.decode('utf-8')
)
consumer.subscribe(['neutrai'])


print("🚀 Attendo messaggi (poll)...")
logging.info("🚀 Attendo messaggi...")

try:
    while True:
        message_pack = consumer.poll(timeout_ms=500, max_records=100)
        for tp, messages in message_pack.items():
            for message in messages:
                logging.info(f"✅ Ricevuto: {message.value}")
                try:
                    msg = json.loads(message.value)
                    print(msg)
                    match msg['event']:
                        case 'dispute:new':
                            dispute_uuid = msg['data']['dispute_uuid']
                            asyncio.run(generate_questions(dispute_uuid))
                        case _:
                            pass
                except Exception as err:
                    print(err)

            # Fai commit solo DOPO aver processato il batch completo
        if message_pack:
            consumer.commit()
            print("✅ Commit batch completato.", flush=True)

except Exception as err:
    print(err)

print ("Quit")
