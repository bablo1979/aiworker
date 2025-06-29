
Per testare in dev, avviare con docker compose up -d
e ed usare kafkacat per lanciare gli eventi come segue:

kafkacat -b localhost:9092 -t seo -P
{"sender":"seobroker","event":"scan:new","data":{"uuid":"0e5bccfa-28fc-11f0-b985-0e1abde6410b"}}